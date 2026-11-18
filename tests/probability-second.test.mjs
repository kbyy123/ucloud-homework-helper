import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseProbabilitySecondReferences} from '../lib/probability-second.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
import {readOptionalJson} from './_local.mjs';

const ID='2116142042516131842';
const source=await readOptionalJson('.inbox',ID,'e9f3fc1a5685ecdd69eabe78132c74aa2fd4418116a764932a0adeb96b2187dd','source.json');
const refs=['1/21','supplement/inclusion-exclusion-induction-v1','1/23','1/26','3/10','3/11','3/15','3/16','3/20','3/26'];

test('第二次从真实同行书页/题号及归纳证明解析，拒绝遗漏或替换附加方法',t=>{
 if(!source)return t.skip('需要本地 .inbox 数据');
 assert.deepEqual(parseProbabilitySecondReferences(source.html).refs,refs);
 assert.equal(parseProbabilitySecondReferences(source.html).supported,true);
 for(const text of [source.html.replace('数学归纳法','组合方法'),source.html.replace('p105 -108','p35 -108'),source.html.replace('26</p>','26（1）</p>'),
  source.html+'<p>附加要求：另证独立</p>',source.html.replace('    20','    21')])assert.equal(parseProbabilitySecondReferences(text).supported,false);
});

test('新增独立题库不改变第一次材料指纹',async t=>{
 const approved=await readOptionalJson('approved-tasks.json');
 if(!approved)return t.skip('需要本地 题库/approved-tasks.json 数据');
 const firstRefs=['2/1','2/3','2/8','2/13','2/18','2/23(1)','2/35(2)','3/2','3/7','3/8','3/9','supplement/empty-axioms-v1','1/26'];
 const first=await materialDigest(ROOT,'probability-bupt-2021',firstRefs);
 assert.equal(first.digest,approved['2113586328423948289'].materialHash);
 const second=await materialDigest(ROOT,'probability-bupt-2021',refs);assert.equal(second.generator,'probability_second.py');
 assert.notEqual(second.digest,first.digest);assert.deepEqual(second.index.requiredRefs,refs);
});

test('第二次整组校验、来源变更与素材篡改拦截、归档重跑',async t=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-probability-second-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:c.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib','probability-second.mjs'),'fixture parser');
 await writeFile(path.join(root,'probability_second.py'),'fixture solver');
 const book=path.join(root,'book.pdf');await writeFile(book,'source textbook');
 const bank=path.join(root,'题库',c.bookId,'second');await mkdir(bank,{recursive:true});
 await writeFile(path.join(bank,'question.md'),'all originals');await writeFile(path.join(bank,'solutions.typ'),'native complete solutions');
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:c.bookId,generator:'probability_second.py',textbook:book,sha256:hash('source textbook'),requiredRefs:refs,
  exercises:refs.map(key=>({key,file:'question.md',sha256:hash('all originals'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native complete solutions')}],images:[]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:''};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const name of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,name),'verified complete materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const now=Date.parse('2026-10-31T21:10:00+08:00');
 const pending=await runWithClient(client,{root,now,build});assert.equal(pending.needsReview.length,1);assert.deepEqual(pending.needsReview[0].refs,refs);
 const review=pending.needsReview[0];await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:review.sourceHash,materialHash:review.materialHash}}));
 assert.equal((await runWithClient(client,{root,now,build})).generated.length,1);
 assert.equal((await runWithClient(client,{root,now,build:async()=>assert.fail('Must skip same material')})).unchanged.length,1);
 client.assignment=async()=>({...detail,assignmentContent:source.html.replace('数学归纳法','直接引用公式')});
 assert.equal((await runWithClient(client,{root,now,build:async()=>assert.fail('Do not ignore proof restriction')})).needsReview.length,1);
 await writeFile(path.join(bank,'solutions.typ'),'changed answer');await assert.rejects(materialDigest(root,c.bookId,refs),/解答或图片已变化/);
 await writeFile(path.join(bank,'solutions.typ'),'native complete solutions');await writeFile(book,'different edition');await assert.rejects(materialDigest(root,c.bookId,refs),/教材已变化/);
});
