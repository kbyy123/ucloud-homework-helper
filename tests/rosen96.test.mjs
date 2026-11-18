import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash,parseReferences} from '../lib/workflow.mjs';

const ID='2117142590505717762';
const source=JSON.parse(await readFile(path.join(ROOT,'.inbox',ID,'0ded50bab9a1db3219948acd7f73499da6e1828ad71f352ba1feed9d588d8d8d','source.json'),'utf8'));
const refs=['9.6/4','9.6/16','9.6/32','9.6/44'];

test('9.6真实来源与完整原图/原生解答有独立指纹，9.5及旧章节不变',async()=>{
 assert.deepEqual(parseReferences(source.html).refs,refs);
 const approved=JSON.parse(await readFile(path.join(ROOT,'approved-tasks.json'),'utf8'));
 const previous=await materialDigest(ROOT,'rosen-8',['9.5/16','9.5/26','9.5/46','9.5/60']);
 assert.equal(previous.digest,approved['2113561808636010497'].materialHash);
 const current=await materialDigest(ROOT,'rosen-8',refs);
 assert.equal(current.generator,'rosen96.py');assert.deepEqual(current.index.requiredRefs,refs);
 assert.notEqual(current.digest,previous.digest);
 assert.equal(current.index.figure32.coversLowerToUpper.length,15);
 assert.deepEqual(current.index.exercises.map(e=>e.subparts),['a–d','a–c','a–h','a–d']);
 assert.ok(current.index.extraFiles.some(e=>e.file==='solutions.typ'));
});

test('9.6需核对完整组及来源；修改/新增要求不复用，人工修改和旧归档保留',async t=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-rosen96-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:c.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await writeFile(path.join(root,'rosen96.py'),'reviewed section solver');
 const textbook=path.join(root,'book.pdf');await writeFile(textbook,'exact edition');
 const bank=path.join(root,'题库',c.bookId,'9.6');await mkdir(bank,{recursive:true});
 for(const [f,text] of [['question.md','complete original'],['solutions.typ','complete native answer'],['figure.png','original Hasse figure']])await writeFile(path.join(bank,f),text);
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:c.bookId,section:'9.6',generator:'rosen96.py',textbook,sha256:hash('exact edition'),requiredRefs:refs,
  exercises:refs.map(key=>({key,file:'question.md',sha256:hash('complete original'),reviewed:true})),
  extraFiles:[{file:'solutions.typ',sha256:hash('complete native answer')}],images:[{file:'figure.png',sha256:hash('original Hasse figure')}]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:source.chapter};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const f of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,f),'complete and verified original and answer '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const options={root,now:Date.parse('2026-11-03T12:00:00+08:00'),build};
 const pending=await runWithClient(client,options);assert.equal(pending.needsReview.length,1);
 const p=pending.needsReview[0];assert.deepEqual(p.refs,refs);
 await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:p.sourceHash,materialHash:p.materialHash}}));
 const generated=await runWithClient(client,options);assert.equal(generated.generated.length,1);
 const directory=generated.generated[0].directory;
 await writeFile(path.join(directory,'解答.md'),'manual annotations');
 const skipped=await runWithClient(client,{...options,build:async()=>assert.fail('Do not overwrite manually edited archive')});
 assert.deepEqual(skipped.unchanged[0].preservedEdits,['解答.md']);assert.equal(await readFile(path.join(directory,'解答.md'),'utf8'),'manual annotations');
 for(const html of ['9.6 Exercises: 4, 16, 32','9.6 Exercises: 4, 16, 32, 44, 45','9.6 Exercises: 4, 16, 32, 44（另证一种方法）']){
  client.assignment=async()=>({...detail,assignmentContent:html});
  assert.equal((await runWithClient(client,{...options,build:async()=>assert.fail('Do not ignore changed requirements')})).needsReview.length,1);
 }
 for(const [f,original] of [['solutions.typ','complete native answer'],['figure.png','original Hasse figure'],['question.md','complete original']]){
  await writeFile(path.join(bank,f),'changed material');await assert.rejects(materialDigest(root,c.bookId,refs),/原文、解答或图片已变化/);await writeFile(path.join(bank,f),original);
 }
 await writeFile(textbook,'different edition');await assert.rejects(materialDigest(root,c.bookId,refs),/教材已变化/);
});
