import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseProbabilityReferences} from '../lib/probability.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
import {readOptionalJson} from './_local.mjs';
const ID='2118854975265439746';
const source=await readOptionalJson('.inbox',ID,'3869731a5601965eb657c31038aeb7a1423317a48aa8aa5996f238dff6e479dc','source.json');
const refs=['3/21','3/28','3/29','4/2','4/5','4/6(2)','4/7(2)','1/40','1/42','1/47'];

test('第三次完整题号、小问及独立路由；旧两次材料指纹保持不变',async t=>{
 const approval=await readOptionalJson('approved-tasks.json');
 if(!source || !approval)return t.skip('需要本地 .inbox/题库/approved-tasks.json 数据');
 assert.deepEqual(parseProbabilityReferences(source.html).refs,refs);
 const first=['2/1','2/3','2/8','2/13','2/18','2/23(1)','2/35(2)','3/2','3/7','3/8','3/9','supplement/empty-axioms-v1','1/26'];
 const second=['1/21','supplement/inclusion-exclusion-induction-v1','1/23','1/26','3/10','3/11','3/15','3/16','3/20','3/26'];
 assert.equal((await materialDigest(ROOT,'probability-bupt-2021',first)).digest,approval['2113586328423948289'].materialHash);
 assert.equal((await materialDigest(ROOT,'probability-bupt-2021',second)).digest,approval['2116142042516131842'].materialHash);
 const current=await materialDigest(ROOT,'probability-bupt-2021',refs);
 assert.equal(current.generator,'probability_third.py');assert.deepEqual(current.index.requiredRefs,refs);
 assert.equal(current.index.assignment,'third');
 assert.ok(current.index.extraFiles.some(e=>e.file==='solutions.typ'));
 assert.equal(parseProbabilityReferences(source.html+'\n另证独立性').supported,false);
});

test('第三次来源/小问变化不套旧答案；题干、解答、图、版本变化拦截；重跑保留人工修改',async t=>{
 if(!source)return t.skip('需要本地 .inbox 数据');
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-probability-third-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:c.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib/probability.mjs'),'verified parser');
 await writeFile(path.join(root,'probability_third.py'),'verified solver');
 const book=path.join(root,'book.pdf');await writeFile(book,'exact edition');
 const bank=path.join(root,'题库',c.bookId,'third');await mkdir(bank,{recursive:true});
 const assets=[['question.md','exact original'],['solutions.typ','exact native answers'],['source.png','exact scanned page']];
 for(const [f,s] of assets)await writeFile(path.join(bank,f),s);
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:c.bookId,assignment:'third',generator:'probability_third.py',textbook:book,sha256:hash('exact edition'),requiredRefs:refs,
  exercises:refs.map(key=>({key,file:'question.md',sha256:hash('exact original'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('exact native answers')}],images:[{file:'source.png',sha256:hash('exact scanned page')}]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:''};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const f of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,f),'Complete verified learning materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const options={root,now:Date.parse('2026-11-08T12:00:00+08:00'),build};
 const pending=await runWithClient(client,options),p=pending.needsReview[0];assert.deepEqual(p.refs,refs);
 await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:p.sourceHash,materialHash:p.materialHash}}));
 const generated=await runWithClient(client,options);assert.equal(generated.generated.length,1);
 const dir=generated.generated[0].directory;await writeFile(path.join(dir,'解答.md'),'Manual student annotations');
 const skipped=await runWithClient(client,{...options,build:async()=>assert.fail('Must not overwrite')});
 assert.deepEqual(skipped.unchanged[0].preservedEdits,['解答.md']);
 for(const html of [source.html.replace('6(2)','6(1)'),source.html.replace('7(2)','7'),source.html+'\n增加一道证明题']){
  client.assignment=async()=>({...detail,assignmentContent:html});
  assert.equal((await runWithClient(client,{...options,build:async()=>assert.fail('Changed requirements')})).needsReview.length,1);
 }
 for(const [f,s] of assets){await writeFile(path.join(bank,f),'changed');await assert.rejects(materialDigest(root,c.bookId,refs),/原文、解答或图片已变化/);await writeFile(path.join(bank,f),s);}
 await writeFile(book,'different edition');await assert.rejects(materialDigest(root,c.bookId,refs),/教材已变化/);
});
