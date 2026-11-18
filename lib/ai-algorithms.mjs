import path from 'node:path';
import {access,readFile} from 'node:fs/promises';
import {hash,readJson} from './workflow.mjs';

async function resolveGenerator(root, file) {
  const inDir = path.join(root, 'generators', file);
  try { await access(inDir); return inDir; } catch { return path.join(root, file); }
}

export const AI_BOOK = 'ai-algorithms-2026';
export const AI_SITE = '2091774261898891268';
export const AI_POLICY = Object.freeze({
  subject: '数据结构',
  answerFormat: 'typst',
  codeLanguage: 'cpp',
  codeStyle: 'C风格，使用ElemType/typedef、数组、结构体和指针，不使用STL',
  narration: '核对真实正文及全部附件；明确要求视频或语音讲解时增加逐题口述文稿',
  codeDelivery: 'PDF内嵌完整代码，并归档可独立编译的.cpp、测试用例与实际测试结果',
});

export function aiReferences(source) {
  if(source.course?.id!==AI_SITE || source.course?.bookId!==AI_BOOK)
    throw new Error('人工智能算法与工程课程绑定变化，需核对');
  return {supported:true,refs:[source.id+'/'+hash(source)]};
}

export async function aiMaterialDigest(root,refs) {
  if(refs.length!==1 || !/^\d{10,25}\/[a-f0-9]{64}$/.test(refs[0]))return null;
  const [id,sourceHash]=refs[0].split('/');
  const bank=path.join(root,'题库',AI_BOOK,id,sourceHash);
  const index=await readJson(path.join(bank,'index.json'));
  if(!index)return null;
  if(index.bookId!==AI_BOOK || index.sourceHash!==sourceHash || index.assignmentId!==id ||
     index.generator!=='ai_algorithms.py' || index.requiredRefs?.join()!==refs.join())
    throw new Error('数据结构材料与真实作业来源不匹配');
  const review=index.requirementsReview;
  if(review?.reviewed!==true || typeof review.narrationRequired!=='boolean' ||
     !review.evidence?.trim() || review.allAttachmentsRead!==true)
    throw new Error('数据结构作业缺少正文、附件及讲解要求的核对记录');
  const files=new Map((index.files||[]).map(item=>[item.file,item]));
  const required=['题目.md','解答.md','解答.typ','核对记录.md','verification.json'];
  if(review.narrationRequired)required.push('讲解文稿.md');
  if(required.some(file=>!files.has(file)) || ![...files.keys()].some(file=>file.endsWith('.cpp')))
    throw new Error('数据结构材料缺少Typst、C++代码、验证记录或讲解文稿');
  const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],
    ['generator',hash(await readFile(await resolveGenerator(root,index.generator)))],
    ['policy',hash(await readFile(new URL('./ai-algorithms.mjs',import.meta.url)))]];
  for(const item of files.values()) {
    if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..'))
      throw new Error('数据结构材料路径越界');
    const bytes=await readFile(path.join(bank,item.file));
    if(hash(bytes)!==item.sha256)throw new Error('数据结构原题、解答、代码或文稿已变化，需复核');
    parts.push([item.file,item.sha256]);
  }
  const verification=await readJson(path.join(bank,'verification.json'));
  if(verification?.ok!==true || verification.codeCompiled!==true || !(verification.testCases>0))
    throw new Error('数据结构C++代码尚未编译或测试');
  return {digest:hash(parts),index,bank,generator:index.generator};
}
