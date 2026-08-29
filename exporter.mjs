import { chromium } from 'playwright';
import { mkdir, writeFile, stat } from 'node:fs/promises';
import path from 'node:path';

const BASE = 'https://styles.refero.design';
const OUT = path.resolve('output');
const LIMIT = Number(process.env.LIMIT || '1');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchJson(url, attempts = 5) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: {
          accept: 'application/json',
          'user-agent': 'refero-exporter/1.0 (+github-actions)'
        },
        signal: AbortSignal.timeout(45_000)
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      return await response.json();
    } catch (error) {
      lastError = error;
      if (attempt < attempts) await sleep(500 * attempt);
    }
  }
  throw lastError;
}

async function getCatalog() {
  const result = await fetchJson(`${BASE}/api/styles?page=1`);
  if (!Array.isArray(result.styles) || result.styles.length === 0) {
    throw new Error(`Unexpected catalog response: ${JSON.stringify(result).slice(0, 1000)}`);
  }
  return result.styles;
}

function folderNameFor(style) {
  let host = 'unknown-site';
  try {
    host = new URL(style.url).hostname || host;
  } catch {}
  return host.replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_').replace(/[. ]+$/g, '') || `style-${style.id}`;
}

async function lastVisible(locator) {
  for (let index = (await locator.count()) - 1; index >= 0; index -= 1) {
    const item = locator.nth(index);
    if (await item.isVisible().catch(() => false)) return item;
  }
  return null;
}

async function clickNamedButton(page, name) {
  const exact = page.getByRole('button', { name, exact: true });
  let target = await lastVisible(exact);
  if (!target) {
    const regex = new RegExp(`^\\s*${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`, 'i');
    target = await lastVisible(page.locator('button').filter({ hasText: regex }));
  }
  if (!target) throw new Error(`Visible button not found: ${name}`);
  await target.scrollIntoViewIfNeeded();
  await target.click({ timeout: 15_000 });
}

async function visibleButtonDiagnostics(page) {
  const buttons = page.locator('button');
  const rows = [];
  for (let i = 0; i < await buttons.count(); i += 1) {
    const button = buttons.nth(i);
    if (!(await button.isVisible().catch(() => false))) continue;
    rows.push({
      index: i,
      text: (await button.innerText().catch(() => '')).trim(),
      aria: await button.getAttribute('aria-label'),
      title: await button.getAttribute('title')
    });
  }
  return rows;
}

async function findDownloadButton(page, extension) {
  const buttons = page.locator('button');
  const candidates = [];
  for (let i = 0; i < await buttons.count(); i += 1) {
    const button = buttons.nth(i);
    if (!(await button.isVisible().catch(() => false))) continue;
    const text = (await button.innerText().catch(() => '')).trim();
    const aria = (await button.getAttribute('aria-label')) || '';
    const title = (await button.getAttribute('title')) || '';
    const combined = `${text} ${aria} ${title}`.trim();
    let score = 0;
    if (text === extension) score = 100;
    else if (text.toLowerCase() === `download ${extension}`.toLowerCase()) score = 95;
    else if (/download/i.test(combined) && combined.includes(extension)) score = 90;
    else if (text.endsWith(extension)) score = 80;
    else if (combined.includes(extension)) score = 60;
    if (score > 0) candidates.push({ button, score, index: i, text, aria, title });
  }
  candidates.sort((a, b) => b.score - a.score || b.index - a.index);
  return candidates[0] || null;
}

async function largestVisibleCodeBlock(page) {
  const selectors = ['pre', 'code'];
  let best = '';
  for (const selector of selectors) {
    const blocks = page.locator(selector);
    for (let i = 0; i < await blocks.count(); i += 1) {
      const block = blocks.nth(i);
      if (!(await block.isVisible().catch(() => false))) continue;
      const text = await block.textContent().catch(() => '');
      if (text && text.length > best.length) best = text;
    }
  }
  return best;
}

async function downloadActive(page, destination, extension) {
  const candidate = await findDownloadButton(page, extension);
  if (!candidate) {
    const fallback = await largestVisibleCodeBlock(page);
    if (!fallback) throw new Error(`No download button or visible code block for ${extension}`);
    await writeFile(destination, fallback, 'utf8');
    return { method: 'visible-code-fallback', button: null };
  }

  try {
    const downloadPromise = page.waitForEvent('download', { timeout: 15_000 });
    await candidate.button.scrollIntoViewIfNeeded();
    await candidate.button.click({ timeout: 15_000 });
    const download = await downloadPromise;
    await download.saveAs(destination);
    return {
      method: 'download',
      button: { text: candidate.text, aria: candidate.aria, title: candidate.title },
      suggestedFilename: download.suggestedFilename()
    };
  } catch (error) {
    const fallback = await largestVisibleCodeBlock(page);
    if (!fallback) throw error;
    await writeFile(destination, fallback, 'utf8');
    return {
      method: 'visible-code-fallback-after-click',
      button: { text: candidate.text, aria: candidate.aria, title: candidate.title },
      downloadError: String(error)
    };
  }
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const catalog = (await getCatalog()).slice(0, LIMIT);
  console.log(`Testing ${catalog.length} style(s)`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US'
  });
  const page = await context.newPage();
  await page.route('**/*', async (route) => {
    const type = route.request().resourceType();
    if (['image', 'media', 'font'].includes(type)) await route.abort();
    else await route.continue();
  });

  const diagnostics = [];
  for (const style of catalog) {
    const folder = path.join(OUT, folderNameFor(style));
    await mkdir(folder, { recursive: true });
    const detailUrl = `${BASE}/style/${style.id}`;
    console.log(`Opening ${detailUrl}`);
    await page.goto(detailUrl, { waitUntil: 'domcontentloaded', timeout: 60_000 });
    await page.getByText(style.siteName, { exact: true }).first().waitFor({ state: 'visible', timeout: 30_000 }).catch(() => {});
    await page.waitForTimeout(1_000);

    const entry = {
      id: style.id,
      siteName: style.siteName,
      sourceUrl: style.url,
      detailUrl,
      initialButtons: await visibleButtonDiagnostics(page),
      files: {}
    };

    const exports = [
      { tab: 'DESIGN.md', extension: '.md', file: 'design.md' },
      { tab: 'Tailwind v4', extension: '.css', file: 'tailwind-v4.css' },
      { tab: 'CSS Variables', extension: '.css', file: 'css-variables.css' },
      { tab: 'Design Tokens', extension: '.json', file: 'design-tokens.json' }
    ];

    for (const spec of exports) {
      console.log(`  ${spec.tab}`);
      await clickNamedButton(page, spec.tab);
      await page.waitForTimeout(250);
      await clickNamedButton(page, 'Extended');
      await page.waitForTimeout(250);
      const destination = path.join(folder, spec.file);
      const result = await downloadActive(page, destination, spec.extension);
      const info = await stat(destination);
      if (info.size === 0) throw new Error(`Empty output: ${destination}`);
      entry.files[spec.file] = { ...result, bytes: info.size };
    }

    diagnostics.push(entry);
  }

  await writeFile(path.join(OUT, '_diagnostics.json'), JSON.stringify(diagnostics, null, 2), 'utf8');
  await browser.close();
  console.log('Done');
}

main().catch(async (error) => {
  console.error(error?.stack || error);
  process.exitCode = 1;
});
