import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,copyFile,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {AI_BOOK,AI_SITE,aiReferences,aiMaterialDigest} from '../lib/ai-algorithms.mjs';
import {deliveryName} from '../lib/pdf-delivery.mjs';
import {hash} from '../lib/workflow.mjs';
import {ROOT} from '../run.mjs';
import {readOptionalJson} from './_local.mjs';

const source={id:'2115592895636279298',title:'第三章作业',assignedAt:'2026-10-29 00:00',
  due:'2026-11-12 23:59:59',course:{key:'人工智能算法与工程',id:AI_SITE,bookId:AI_BOOK},
  html:'请按照附件要求完成作业。',attachments:[{filename:'source.docx',sha256:hash('version one')}]};

test('数据结构按真实作业和附件指纹区分；第x章标题只在绑定课程保留',()=>{
  const refs=aiReferences(source).refs;
  assert.notDeepEqual(aiReferences({...source,attachments:[{...source.attachments[0],sha256:hash('new requirements')}]}).refs,refs);
  assert.equal(deliveryName(source).relativePath,'人工智能算法与工程/10.29-第三章作业.pdf');
  assert.throws(()=>deliveryName({...source,course:{key:'离散数学',bookId:'rosen-8'}}),/第几次作业/);
  assert.throws(()=>aiReferences({...source,course:{...source.course,id:'2091774263035547651'}}),/绑定变化/);
});

test('已批准来源仍须包含代码和要求的讲稿；附件变化和篡改不能复用',async t=>{
  const root=await mkdtemp(path.join(os.tmpdir(),'bupt-ai-policy-'));
  t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
  await mkdir(path.join(root,'templates'));
  await writeFile(path.join(root,'ai_algorithms.py'),'trusted fixture generator');
  const sourceHash=hash(source),refs=aiReferences(source).refs;
  const bank=path.join(root,'题库',AI_BOOK,source.id,sourceHash);
  await mkdir(bank,{recursive:true});
  const documents={'题目.md':'complete source','解答.md':'complete solution','解答.typ':'native solution',
    '核对记录.md':'verified','code.cpp':'typedef int ElemType; int main() { return 0; }',
    'verification.json':JSON.stringify({ok:true,codeCompiled:true,testCases:3})};
  const files=[];
  for(const [file,text] of Object.entries(documents)){await writeFile(path.join(bank,file),text);files.push({file,sha256:hash(text)});}
  const index={bookId:AI_BOOK,sourceHash,assignmentId:source.id,generator:'ai_algorithms.py',
    requiredRefs:refs,files,requirementsReview:{reviewed:true,narrationRequired:true,
      allAttachmentsRead:true,evidence:'附件明确语音讲解'}};
  const save=()=>writeFile(path.join(bank,'index.json'),JSON.stringify(index));
  await save();
  await assert.rejects(aiMaterialDigest(root,refs),/文稿/);
  const speech='逐题口述稿';
  await writeFile(path.join(bank,'讲解文稿.md'),speech);
  files.push({file:'讲解文稿.md',sha256:hash(speech)});
  await save();
  const material=await aiMaterialDigest(root,refs);
  assert.equal(material.generator,'ai_algorithms.py');
  const inbox=path.join(root,'.inbox',source.id,sourceHash,'attachments');
  await mkdir(inbox,{recursive:true});
  await writeFile(path.join(inbox,'source.docx'),'version one');
  const sourceFile=path.join(root,'source.json'),out=path.join(root,'archive');
  await writeFile(sourceFile,JSON.stringify(source));await mkdir(out);
  const runtime=(await readOptionalJson('runtime.json')) || {python:process.env.HOMEWORK_PYTHON || 'python'};
  const script="import importlib.util,sys; from pathlib import Path; s=importlib.util.spec_from_file_location('ai_builder',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.ROOT=Path(sys.argv[2]); m.build(Path(sys.argv[3]),Path(sys.argv[4]))";
  await copyFile(path.join(ROOT,'templates','homework.typ'),path.join(root,'templates','homework.typ'));
  execFileSync(runtime.python,['-c',script,path.join(ROOT,'generators','ai_algorithms.py'),root,sourceFile,out],{windowsHide:true});
  assert.equal(await readFile(path.join(out,'attachments','source.docx'),'utf8'),'version one');
  assert.equal(await readFile(path.join(out,'讲解文稿.md'),'utf8'),speech);
  const changed=aiReferences({...source,attachments:[{filename:'source.docx',sha256:hash('version two')}]}).refs;
  assert.equal(await aiMaterialDigest(root,changed),null);
  await writeFile(path.join(bank,'code.cpp'),'modified implementation');
  await assert.rejects(aiMaterialDigest(root,refs),/变化/);
  assert.ok((await readFile(path.join(bank,'讲解文稿.md'),'utf8')).includes('口述'));
});
