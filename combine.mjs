import { createHash } from 'node:crypto';
import {
  copyFile,
  mkdir,
  readFile,
  readdir,
  rm,
  stat,
  writeFile
} from 'node:fs/promises';
import path from 'node:path';

const CATALOG_FILE = path.resolve(process.env.CATALOG_FILE || 'catalog/catalog.json');
const COMBINED_DIR = path.resolve(process.env.COMBINED_DIR || 'combined');
const PACKAGE_ROOT = path.resolve(process.env.PACKAGE_ROOT || 'package/Refero_Styles');

const REQUIRED_FILES = [
  { file: 'design.md', kind: 'design' },
  { file: 'tailwind-v4.css', kind: 'tailwind' },
  { file: 'css-variables.css', kind: 'variables' },
  { file: 'design-tokens.json', kind: 'tokens' }
];

async function sha256File(filePath) {
  const data = await readFile(filePath);
  return createHash('sha256').update(data).digest('hex');
}

async function validateFile(filePath, kind, expectedHash) {
  const info = await stat(filePath);
  if (!info.isFile() || info.size < 20) throw new Error(`Missing or empty file: ${filePath}`);

  const text = await readFile(filePath, 'utf8');
  if (kind === 'design' && (!text.trimStart().startsWith('#') || !/Style Reference|Tokens|Theme/i.test(text))) {
    throw new Error(`Invalid DESIGN.md: ${filePath}`);
  }
  if (kind === 'tailwind' && !text.includes('@theme')) throw new Error(`Invalid Tailwind file: ${filePath}`);
  if (kind === 'variables' && !text.includes(':root')) throw new Error(`Invalid CSS Variables file: ${filePath}`);
  if (kind === 'tokens') JSON.parse(text);

  const hash = await sha256File(filePath);
  if (expectedHash && hash !== expectedHash) {
    throw new Error(`SHA-256 mismatch for ${filePath}: expected ${expectedHash}, received ${hash}`);
  }

  return { bytes: info.size, sha256: hash };
}

async function readJsonFiles(prefix) {
  const names = (await readdir(COMBINED_DIR))
    .filter((name) => name.startsWith(prefix) && name.endsWith('.json'))
    .sort();

  const values = [];
  for (const name of names) {
    values.push({ name, value: JSON.parse(await readFile(path.join(COMBINED_DIR, name), 'utf8')) });
  }
  return values;
}

async function copyDirectory(source, destination) {
  await mkdir(destination, { recursive: true });
  const entries = await readdir(source, { withFileTypes: true });

  for (const entry of entries) {
    const from = path.join(source, entry.name);
    const to = path.join(destination, entry.name);
    if (entry.isDirectory()) {
      await copyDirectory(from, to);
    } else if (entry.isFile()) {
      await copyFile(from, to);
    }
  }
}

async function main() {
  const catalog = JSON.parse(await readFile(CATALOG_FILE, 'utf8'));
  if (!Array.isArray(catalog.entries) || catalog.entries.length === 0) {
    throw new Error(`Invalid or empty catalog: ${CATALOG_FILE}`);
  }

  const manifestParts = await readJsonFiles('_manifest-part-');
  const errorParts = await readJsonFiles('_errors-part-');
  if (manifestParts.length === 0) throw new Error('No shard manifests were downloaded');

  const completedById = new Map();
  for (const part of manifestParts) {
    for (const entry of part.value.entries || []) {
      if (completedById.has(entry.id)) throw new Error(`Duplicate completed style ID: ${entry.id}`);
      completedById.set(entry.id, entry);
    }
  }

  const reportedErrors = errorParts.flatMap((part) => part.value.errors || []);
  const expectedIds = new Set(catalog.entries.map((entry) => entry.id));
  const completedIds = new Set(completedById.keys());
  const missing = catalog.entries.filter((entry) => !completedIds.has(entry.id));
  const unexpected = [...completedIds].filter((id) => !expectedIds.has(id));

  const validationErrors = [];
  const validatedEntries = [];

  for (let index = 0; index < catalog.entries.length; index += 1) {
    const catalogEntry = catalog.entries[index];
    const completed = completedById.get(catalogEntry.id);
    if (!completed) continue;

    try {
      if (completed.folder !== catalogEntry.folder) {
        throw new Error(`Folder mismatch: catalog=${catalogEntry.folder}, shard=${completed.folder}`);
      }

      const folderPath = path.join(COMBINED_DIR, completed.folder);
      const files = {};
      for (const spec of REQUIRED_FILES) {
        const expectedHash = completed.files?.[spec.file]?.sha256;
        files[spec.file] = await validateFile(path.join(folderPath, spec.file), spec.kind, expectedHash);
      }

      validatedEntries.push({
        id: catalogEntry.id,
        siteName: catalogEntry.siteName,
        sourceUrl: catalogEntry.sourceUrl,
        detailUrl: catalogEntry.detailUrl,
        folder: catalogEntry.folder,
        files
      });
    } catch (error) {
      validationErrors.push({
        id: catalogEntry.id,
        folder: catalogEntry.folder,
        message: error?.message || String(error)
      });
    }

    if ((index + 1) % 100 === 0) {
      console.log(`Validated ${index + 1}/${catalog.entries.length} catalog entries...`);
    }
  }

  const problems = {
    reportedErrors,
    missing: missing.map((entry) => ({ id: entry.id, siteName: entry.siteName, folder: entry.folder })),
    unexpected,
    validationErrors
  };

  if (reportedErrors.length || missing.length || unexpected.length || validationErrors.length) {
    await writeFile(path.join(COMBINED_DIR, '_combine-problems.json'), JSON.stringify(problems, null, 2), 'utf8');
    throw new Error(
      `Incomplete export: reported=${reportedErrors.length}, missing=${missing.length}, ` +
      `unexpected=${unexpected.length}, invalid=${validationErrors.length}`
    );
  }

  validatedEntries.sort((a, b) => a.folder.localeCompare(b.folder));
  const generatedAt = new Date().toISOString();
  const manifest = {
    schemaVersion: 1,
    generatedAt,
    catalogGeneratedAt: catalog.generatedAt,
    source: 'https://styles.refero.design/',
    totalStyles: validatedEntries.length,
    filesPerStyle: REQUIRED_FILES.map((item) => item.file),
    entries: validatedEntries
  };

  const readme = `Refero Styles — полный Extended-экспорт\n\n` +
    `Источник: https://styles.refero.design/\n` +
    `Собрано: ${generatedAt}\n` +
    `Проектов: ${validatedEntries.length}\n\n` +
    `В каждой папке лежат четыре файла:\n` +
    `- design.md\n` +
    `- tailwind-v4.css\n` +
    `- css-variables.css\n` +
    `- design-tokens.json\n\n` +
    `Папки названы по домену оригинального сайта. Если один домен представлен несколькими ` +
    `записями, к имени добавлены название проекта и первые 8 символов ID, чтобы ничего не перезаписалось.\n\n` +
    `Полное соответствие папок, оригинальных URL и Refero-страниц находится в _manifest.json.\n`;

  await rm(PACKAGE_ROOT, { recursive: true, force: true });
  await mkdir(PACKAGE_ROOT, { recursive: true });

  for (const entry of validatedEntries) {
    await copyDirectory(path.join(COMBINED_DIR, entry.folder), path.join(PACKAGE_ROOT, entry.folder));
  }

  await writeFile(path.join(PACKAGE_ROOT, '_manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
  await writeFile(path.join(PACKAGE_ROOT, '_README.txt'), readme, 'utf8');
  await writeFile(
    path.join(PACKAGE_ROOT, '_summary.json'),
    JSON.stringify({
      generatedAt,
      catalogGeneratedAt: catalog.generatedAt,
      totalStyles: validatedEntries.length,
      totalFiles: validatedEntries.length * REQUIRED_FILES.length
    }, null, 2),
    'utf8'
  );

  console.log(`Complete and validated: ${validatedEntries.length} styles, ${validatedEntries.length * 4} files.`);
}

main().catch((error) => {
  console.error(error?.stack || error);
  process.exitCode = 1;
});
