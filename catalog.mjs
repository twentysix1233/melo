import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const BASE_URL = 'https://styles.refero.design';
const OUTPUT_DIR = path.resolve(process.env.CATALOG_OUTPUT_DIR || 'catalog');
const MAX_PAGES = Number(process.env.MAX_PAGES || '500');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchJson(url, attempts = 6) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: {
          accept: 'application/json',
          'user-agent': 'refero-full-export/1.0 (+github-actions)'
        },
        signal: AbortSignal.timeout(45_000)
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`HTTP ${response.status} for ${url}: ${body.slice(0, 500)}`);
      }

      return await response.json();
    } catch (error) {
      lastError = error;
      if (attempt < attempts) {
        const delay = Math.min(10_000, 750 * 2 ** (attempt - 1));
        console.warn(`Request failed (${attempt}/${attempts}), retrying in ${delay}ms: ${error}`);
        await sleep(delay);
      }
    }
  }
  throw lastError;
}

function sanitizeSegment(value, fallback) {
  const cleaned = String(value || '')
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_')
    .replace(/[. ]+$/g, '')
    .trim();
  return cleaned || fallback;
}

function sourceHost(style) {
  try {
    const host = new URL(style.url).hostname.toLowerCase();
    return sanitizeSegment(host, `unknown-site-${style.id.slice(0, 8)}`);
  } catch {
    return `unknown-site-${style.id.slice(0, 8)}`;
  }
}

function slug(value) {
  return String(value || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48) || 'style';
}

async function fetchAllStyles() {
  const byId = new Map();
  const visitedPages = new Set();
  let page = 1;
  let pageCount = 0;

  while (page != null) {
    if (visitedPages.has(page)) throw new Error(`Pagination loop detected at page ${page}`);
    if (pageCount >= MAX_PAGES) throw new Error(`Aborted after MAX_PAGES=${MAX_PAGES}`);

    visitedPages.add(page);
    pageCount += 1;
    console.log(`Fetching catalog page ${page}...`);

    const payload = await fetchJson(`${BASE_URL}/api/styles?page=${encodeURIComponent(page)}`);
    if (!Array.isArray(payload.styles)) {
      throw new Error(`Unexpected response on page ${page}: styles is not an array`);
    }

    for (const style of payload.styles) {
      if (!style?.id) continue;
      byId.set(style.id, style);
    }

    if (payload.nextPage == null || payload.styles.length === 0) break;
    page = Number(payload.nextPage);
    if (!Number.isFinite(page) || page < 1) {
      throw new Error(`Invalid nextPage value: ${payload.nextPage}`);
    }

    await sleep(175);
  }

  return { styles: [...byId.values()], pageCount };
}

function buildCatalog(styles) {
  const groupedByHost = new Map();

  for (const style of styles) {
    const host = sourceHost(style);
    if (!groupedByHost.has(host)) groupedByHost.set(host, []);
    groupedByHost.get(host).push(style);
  }

  const entries = [];
  const usedFolders = new Set();

  for (const [host, group] of groupedByHost) {
    group.sort((a, b) => String(a.id).localeCompare(String(b.id)));

    for (const style of group) {
      let folder = group.length === 1
        ? host
        : `${host}__${slug(style.siteName)}__${String(style.id).slice(0, 8)}`;

      folder = sanitizeSegment(folder.slice(0, 180), `style-${String(style.id).slice(0, 8)}`);
      if (usedFolders.has(folder)) folder = `${folder}__${String(style.id).slice(0, 8)}`;
      usedFolders.add(folder);

      entries.push({
        id: String(style.id),
        siteName: String(style.siteName || host),
        sourceUrl: String(style.url || ''),
        detailUrl: `${BASE_URL}/style/${style.id}`,
        folder,
        colorScheme: style.colorScheme ?? null,
        createdAt: style.createdAt ?? null
      });
    }
  }

  entries.sort((a, b) => a.id.localeCompare(b.id));
  return entries;
}

async function main() {
  await mkdir(OUTPUT_DIR, { recursive: true });

  const { styles, pageCount } = await fetchAllStyles();
  if (styles.length === 0) throw new Error('Refero catalog is empty');

  const entries = buildCatalog(styles);
  const generatedAt = new Date().toISOString();
  const catalog = {
    schemaVersion: 1,
    generatedAt,
    source: `${BASE_URL}/api/styles`,
    pageCount,
    totalStyles: entries.length,
    entries
  };

  await writeFile(path.join(OUTPUT_DIR, 'catalog.json'), JSON.stringify(catalog, null, 2), 'utf8');
  await writeFile(
    path.join(OUTPUT_DIR, '_catalog-summary.json'),
    JSON.stringify({ generatedAt, pageCount, totalStyles: entries.length }, null, 2),
    'utf8'
  );

  console.log(`Catalog complete: ${entries.length} unique styles across ${pageCount} pages.`);
}

main().catch((error) => {
  console.error(error?.stack || error);
  process.exitCode = 1;
});
