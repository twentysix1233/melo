import { createHash } from 'node:crypto';
import {
  mkdir,
  readFile,
  rename,
  rm,
  stat,
  writeFile
} from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const CATALOG_FILE = path.resolve(process.env.CATALOG_FILE || 'catalog/catalog.json');
const OUTPUT_DIR = path.resolve(process.env.OUTPUT_DIR || 'output');
const SHARD_INDEX = Number(process.env.SHARD_INDEX || '0');
const SHARD_TOTAL = Number(process.env.SHARD_TOTAL || '1');
const MAX_ATTEMPTS = Number(process.env.MAX_ATTEMPTS || '4');
const BETWEEN_STYLES_MS = Number(process.env.BETWEEN_STYLES_MS || '125');

const EXPORTS = [
  { tab: 'DESIGN.md', extension: '.md', file: 'design.md', kind: 'design' },
  { tab: 'Tailwind v4', extension: '.css', file: 'tailwind-v4.css', kind: 'tailwind' },
  { tab: 'CSS Variables', extension: '.css', file: 'css-variables.css', kind: 'variables' },
  { tab: 'Design Tokens', extension: '.json', file: 'design-tokens.json', kind: 'tokens' }
];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const partLabel = String(SHARD_INDEX).padStart(2, '0');

function assertShardSettings() {
  if (!Number.isInteger(SHARD_INDEX) || !Number.isInteger(SHARD_TOTAL)) {
    throw new Error('SHARD_INDEX and SHARD_TOTAL must be integers');
  }
  if (SHARD_TOTAL < 1 || SHARD_INDEX < 0 || SHARD_INDEX >= SHARD_TOTAL) {
    throw new Error(`Invalid shard settings: index=${SHARD_INDEX}, total=${SHARD_TOTAL}`);
  }
}

async function lastVisible(locator) {
  for (let index = (await locator.count()) - 1; index >= 0; index -= 1) {
    const item = locator.nth(index);
    if (await item.isVisible().catch(() => false)) return item;
  }
  return null;
}

async function waitForVisible(locator, timeoutMs = 30_000, description = 'element') {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const target = await lastVisible(locator);
    if (target) return target;
    await sleep(200);
  }
  throw new Error(`Timed out waiting for visible ${description}`);
}

async function namedButton(page, name, timeoutMs = 30_000) {
  const exact = page.getByRole('button', { name, exact: true });
  try {
    return await waitForVisible(exact, timeoutMs, `button “${name}”`);
  } catch {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const fallback = page.locator('button').filter({ hasText: new RegExp(`^\\s*${escaped}\\s*$`, 'i') });
    return await waitForVisible(fallback, 8_000, `fallback button “${name}”`);
  }
}

async function clickNamedButton(page, name) {
  const button = await namedButton(page, name);
  await button.scrollIntoViewIfNeeded();
  await button.click({ timeout: 20_000 });
}

async function sha256File(filePath) {
  const data = await readFile(filePath);
  return createHash('sha256').update(data).digest('hex');
}

async function validateFile(filePath, kind) {
  const info = await stat(filePath);
  if (!info.isFile() || info.size < 20) {
    throw new Error(`Downloaded ${kind} file is missing or too small: ${filePath}`);
  }

  const text = await readFile(filePath, 'utf8');
  if (kind === 'design' && (!text.trimStart().startsWith('#') || !/Style Reference|Tokens|Theme/i.test(text))) {
    throw new Error(`DESIGN.md validation failed: ${filePath}`);
  }
  if (kind === 'tailwind' && !text.includes('@theme')) {
    throw new Error(`Tailwind v4 validation failed: ${filePath}`);
  }
  if (kind === 'variables' && !text.includes(':root')) {
    throw new Error(`CSS Variables validation failed: ${filePath}`);
  }
  if (kind === 'tokens') {
    try {
      JSON.parse(text);
    } catch (error) {
      throw new Error(`Design Tokens JSON validation failed: ${filePath}: ${error}`);
    }
  }

  return {
    bytes: info.size,
    sha256: await sha256File(filePath)
  };
}

async function downloadActiveExport(page, destination, spec) {
  const button = await namedButton(page, spec.extension, 20_000);
  await button.scrollIntoViewIfNeeded();

  const temporary = `${destination}.part`;
  await rm(temporary, { force: true });

  const downloadPromise = page.waitForEvent('download', { timeout: 30_000 });
  await button.click({ timeout: 20_000 });
  const download = await downloadPromise;
  await download.saveAs(temporary);

  const failure = await download.failure();
  if (failure) throw new Error(`Browser download failed for ${spec.tab}: ${failure}`);

  await rename(temporary, destination);
  const validation = await validateFile(destination, spec.kind);

  return {
    ...validation,
    suggestedFilename: download.suggestedFilename()
  };
}

async function exportStyleOnce(context, entry, attempt) {
  const destinationFolder = path.join(OUTPUT_DIR, entry.folder);
  await rm(destinationFolder, { recursive: true, force: true });
  await mkdir(destinationFolder, { recursive: true });

  const page = await context.newPage();
  page.setDefaultTimeout(30_000);
  page.setDefaultNavigationTimeout(60_000);

  try {
    const response = await page.goto(entry.detailUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 60_000
    });

    if (response && !response.ok()) {
      throw new Error(`Detail page returned HTTP ${response.status()}: ${entry.detailUrl}`);
    }

    await namedButton(page, 'DESIGN.md', 45_000);
    await page.waitForTimeout(250);

    const files = {};
    for (const spec of EXPORTS) {
      await clickNamedButton(page, spec.tab);
      await page.waitForTimeout(175);
      await clickNamedButton(page, 'Extended');
      await page.waitForTimeout(175);

      const destination = path.join(destinationFolder, spec.file);
      files[spec.file] = await downloadActiveExport(page, destination, spec);
    }

    return {
      id: entry.id,
      siteName: entry.siteName,
      sourceUrl: entry.sourceUrl,
      detailUrl: entry.detailUrl,
      folder: entry.folder,
      attempts: attempt,
      files
    };
  } finally {
    await page.close().catch(() => {});
  }
}

async function exportStyle(context, entry) {
  const attemptErrors = [];

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      return await exportStyleOnce(context, entry, attempt);
    } catch (error) {
      const message = error?.stack || String(error);
      attemptErrors.push({ attempt, message });
      console.warn(`[${entry.id}] attempt ${attempt}/${MAX_ATTEMPTS} failed: ${message.split('\n')[0]}`);

      if (attempt < MAX_ATTEMPTS) {
        await sleep(Math.min(15_000, 1_000 * 2 ** (attempt - 1)));
      }
    }
  }

  await rm(path.join(OUTPUT_DIR, entry.folder), { recursive: true, force: true });
  const error = new Error(`All ${MAX_ATTEMPTS} attempts failed for ${entry.siteName} (${entry.id})`);
  error.attemptErrors = attemptErrors;
  throw error;
}

async function runPass(context, entries, completedById, failureById, label) {
  for (let index = 0; index < entries.length; index += 1) {
    const entry = entries[index];
    const progress = `${index + 1}/${entries.length}`;
    console.log(`[shard ${SHARD_INDEX}/${SHARD_TOTAL}] ${label} ${progress}: ${entry.siteName} — ${entry.id}`);

    try {
      const result = await exportStyle(context, entry);
      completedById.set(entry.id, result);
      failureById.delete(entry.id);
      console.log(`  completed: ${entry.folder}`);
    } catch (error) {
      failureById.set(entry.id, {
        id: entry.id,
        siteName: entry.siteName,
        sourceUrl: entry.sourceUrl,
        detailUrl: entry.detailUrl,
        folder: entry.folder,
        message: error?.message || String(error),
        attemptErrors: error?.attemptErrors || []
      });
      console.error(`  failed: ${error?.message || error}`);
    }

    if (BETWEEN_STYLES_MS > 0) await sleep(BETWEEN_STYLES_MS);
  }
}

async function writePartFiles(catalog, assigned, completedById, failureById) {
  const completed = [...completedById.values()].sort((a, b) => a.id.localeCompare(b.id));
  const errors = [...failureById.values()].sort((a, b) => a.id.localeCompare(b.id));
  const generatedAt = new Date().toISOString();

  await writeFile(
    path.join(OUTPUT_DIR, `_manifest-part-${partLabel}.json`),
    JSON.stringify({
      schemaVersion: 1,
      generatedAt,
      catalogGeneratedAt: catalog.generatedAt,
      shardIndex: SHARD_INDEX,
      shardTotal: SHARD_TOTAL,
      assignedStyles: assigned.length,
      completedStyles: completed.length,
      failedStyles: errors.length,
      entries: completed
    }, null, 2),
    'utf8'
  );

  await writeFile(
    path.join(OUTPUT_DIR, `_errors-part-${partLabel}.json`),
    JSON.stringify({
      generatedAt,
      shardIndex: SHARD_INDEX,
      shardTotal: SHARD_TOTAL,
      errors
    }, null, 2),
    'utf8'
  );

  await writeFile(
    path.join(OUTPUT_DIR, `_stats-part-${partLabel}.json`),
    JSON.stringify({
      generatedAt,
      shardIndex: SHARD_INDEX,
      shardTotal: SHARD_TOTAL,
      assignedStyles: assigned.length,
      completedStyles: completed.length,
      failedStyles: errors.length
    }, null, 2),
    'utf8'
  );
}

async function main() {
  assertShardSettings();
  await mkdir(OUTPUT_DIR, { recursive: true });

  const catalog = JSON.parse(await readFile(CATALOG_FILE, 'utf8'));
  if (!Array.isArray(catalog.entries) || catalog.entries.length === 0) {
    throw new Error(`Invalid or empty catalog: ${CATALOG_FILE}`);
  }

  const assigned = catalog.entries.filter((_, index) => index % SHARD_TOTAL === SHARD_INDEX);
  console.log(`Catalog contains ${catalog.entries.length} styles; shard ${SHARD_INDEX} received ${assigned.length}.`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-dev-shm-usage']
  });
  const context = await browser.newContext({
    acceptDownloads: true,
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    serviceWorkers: 'block'
  });

  await context.route('**/*', async (route) => {
    const type = route.request().resourceType();
    if (type === 'image' || type === 'media' || type === 'font') {
      await route.abort();
    } else {
      await route.continue();
    }
  });

  const completedById = new Map();
  const failureById = new Map();

  try {
    await runPass(context, assigned, completedById, failureById, 'primary');

    if (failureById.size > 0) {
      const recoveryEntries = assigned.filter((entry) => failureById.has(entry.id));
      console.warn(`Recovery pass for ${recoveryEntries.length} failed style(s) starts in 20 seconds.`);
      await sleep(20_000);
      await runPass(context, recoveryEntries, completedById, failureById, 'recovery');
    }
  } finally {
    await writePartFiles(catalog, assigned, completedById, failureById);
    await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }

  if (failureById.size > 0) {
    throw new Error(`Shard ${SHARD_INDEX} finished with ${failureById.size} failed style(s)`);
  }

  console.log(`Shard ${SHARD_INDEX} complete: ${completedById.size}/${assigned.length}.`);
}

main().catch((error) => {
  console.error(error?.stack || error);
  process.exitCode = 1;
});
