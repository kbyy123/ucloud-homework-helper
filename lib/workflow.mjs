import { createHash, randomUUID } from 'node:crypto';
import { readFile, writeFile, mkdir, rename, readdir, rm } from 'node:fs/promises';
import path from 'node:path';

export const hash = value => createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : JSON.stringify(value)).digest('hex');

export function deadlineState(due, now = Date.now()) {
  if (typeof due !== 'string' || !/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?$/.test(due)) return 'unknown';
  const normalized = due.replace(' ', 'T');
  const canonical = normalized.length === 16 ? normalized + ':00' : normalized;
  const time = Date.parse(`${canonical}+08:00`);
  if (!Number.isFinite(time) || new Date(time+8*3600000).toISOString().slice(0,19)!==canonical) return 'unknown';
  return time > now ? 'active' : 'expired';
}

export function plainRequirements(html) {
  return String(html || '').replace(/<sup>(.*?)<\/sup>/gis, '^$1').replace(/<sub>(.*?)<\/sub>/gis, '_$1')
    .replace(/<br\s*\/?\s*>|<\/(?:p|div|li)>/gi, '\n').replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .split('\n').map(s => s.trim()).filter(Boolean).join('\n');
}

/** Narrow explicit textbook references only; ambiguous/unsupported prose is never guessed. */
export function parseReferences(html) {
  const text = plainRequirements(html);
  const headings = [...text.matchAll(/\b(\d+\.\d+)\s+Exercises?\s*[:：]/gi)];
  const refs = [];
  if (!headings.length || text.slice(0, headings[0].index).trim()) return { refs: [], supported: false, text };
  for (let i=0; i<headings.length; i++) {
    const start = headings[i].index + headings[i][0].length;
    let clause = text.slice(start, headings[i+1]?.index ?? text.length);
    // Notes are preserved in source but must be approved by an agent for a new fingerprint.
    clause = clause.replace(/[（(][^）)]*[）)]/g, '');
    if (!/^\s*\d+(?:\s*[,，、]\s*\d+)*\s*[.。]?\s*$/.test(clause)) return { refs: [], supported: false, text };
    for (const number of clause.match(/\d+/g) || []) refs.push(`${headings[i][1]}/${Number(number)}`);
  }
  return { refs: [...new Set(refs)], supported: refs.length > 0, text };
}

/** The chapter must come from assignment detail; never infer it from the title. */
export function parseDigitalReferences(html, chapter) {
  const text=plainRequirements(html);
  if(chapter!=='第二章 组合逻辑') return {refs:[],supported:false,text};
  const stripped=text.replace(/[（(][^）)]*[）)]/g,'').replace(/\s+/g,'');
  if(!/^课后题\d+(?:[、，,]\d+)*[。.]?$/.test(stripped)) return {refs:[],supported:false,text};
  const numbers=stripped.match(/\d+/g) || [];
  if(numbers.some(n=>!Number.isSafeInteger(Number(n)) || Number(n)<1)) return {refs:[],supported:false,text};
  return {refs:[...new Set(numbers.map(n=>`2/${Number(n)}`))],supported:numbers.length>0,text};
}

export function sourceRecord(item, detail, course, attachments = []) {
  if (String(detail.id) !== item.id || !detail.assignmentContent || !detail.assignmentTitle) throw new Error('作业详情缺少必要字段或 ID 不一致');
  return {
    schema: 1, id: item.id, title: detail.assignmentTitle, due: item.due,
    ...(detail.assignmentBeginTime ? {assignedAt:detail.assignmentBeginTime} : {}),
    course: { key: course.key, id: course.siteId, name: course.siteName, bookId: course.bookId },
    chapter: detail.chapterName || '', html: detail.assignmentContent,
    requirements: plainRequirements(detail.assignmentContent), resources: detail.assignmentResource || [], attachments,
  };
}

export async function readJson(file) {
  try { return JSON.parse(await readFile(file, 'utf8')); } catch (e) { if (e.code === 'ENOENT') return null; throw e; }
}

export async function exclusiveJson(file, value) {
  await mkdir(path.dirname(file), { recursive: true });
  try { await writeFile(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' }); }
  catch (e) { if (e.code !== 'EEXIST') throw e; }
}

export function safeId(value) {
  if (!/^\d{10,25}$/.test(value)) throw new Error('待办 ID 格式无效');
  return value;
}

async function fileHashes(dir, prefix = '') {
  const result = {};
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name === '.manifest.json') continue;
    if (entry.isSymbolicLink()) throw new Error('产物中不允许符号链接');
    const rel = path.posix.join(prefix, entry.name);
    if (entry.isDirectory()) Object.assign(result, await fileHashes(path.join(dir, entry.name), rel));
    else result[rel] = hash(await readFile(path.join(dir, entry.name)));
  }
  return result;
}

export async function archive({ root, source, materialHash, build, requirePdf=false }) {
  const fingerprint = hash({ source, materialHash });
  const base = path.join(root, source.course.key, safeId(source.id));
  const candidates = [base, path.join(base, 'revisions', fingerprint)];
  for (const dir of candidates) {
    const manifest = await readJson(path.join(dir, '.manifest.json'));
    if (manifest?.status === 'complete' && manifest.fingerprint === fingerprint) {
      const modified = [];
      for (const [file, expected] of Object.entries(manifest.files)) {
        try { if (hash(await readFile(path.join(dir,file))) !== expected) modified.push(file); }
        catch (e) { if (e.code === 'ENOENT') modified.push(file + '（缺失）'); else throw e; }
      }
      return { status: 'unchanged', directory: dir, fingerprint, preservedEdits: modified };
    }
  }
  const stage = path.join(root, '.staging', randomUUID());
  await mkdir(stage, { recursive: true });
  try {
    await exclusiveJson(path.join(stage, 'source.json'), source);
    await build(stage);
    for (const name of ['题目.md','解答.md','核对记录.md']) {
      if ((await readFile(path.join(stage,name),'utf8')).trim().length < 30) throw new Error(`产物不完整：${name}`);
    }
    const checks = await readJson(path.join(stage, 'verification.json'));
    if (checks?.ok !== true) throw new Error('独立验证未通过，不记为完成');
    if(requirePdf) {
      const pdf=await readJson(path.join(stage,'pdf-verification.json'));
      if(pdf?.ok!==true || pdf.engine!=='typst' || pdf.sourceHash!==hash(source) ||
        pdf.pdfSha256!==hash(await readFile(path.join(stage,'解答.pdf'))) ||
        pdf.typstSha256!==hash(await readFile(path.join(stage,'解答.typ'))))throw new Error('Typst/PDF编译验证未通过，不记为完成');
    }
    const files = await fileHashes(stage);
    await exclusiveJson(path.join(stage, '.manifest.json'), { schema: 1, status: 'complete', fingerprint, materialHash,
      sourceHash: hash(source), completedAt: new Date().toISOString(), files });
    await mkdir(path.dirname(base), { recursive: true });
    let destination = base;
    try { await rename(stage, base); }
    catch (e) {
      if (!['EEXIST','ENOTEMPTY','EPERM','EACCES'].includes(e.code)) throw e;
      destination = candidates[1];
      await mkdir(path.dirname(destination), { recursive: true });
      await rename(stage, destination); // Existing revisions are never overwritten.
    }
    return { status: 'generated', directory: destination, fingerprint };
  } finally {
    // stage is an internally generated absolute child of .staging, never supplied by an input.
    const stagingRoot = path.resolve(root, '.staging') + path.sep;
    if (!path.resolve(stage).startsWith(stagingRoot)) throw new Error('临时目录越界');
    await rm(stage, { recursive: true, force: true });
  }
}
