import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { ROOT } from '../run.mjs';

export async function readOptionalJson(...parts) {
  try {
    return JSON.parse(await readFile(path.join(ROOT, ...parts), 'utf8'));
  } catch (e) {
    if (e.code === 'ENOENT') return null;
    throw e;
  }
}
