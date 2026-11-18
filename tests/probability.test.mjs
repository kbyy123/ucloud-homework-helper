import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseProbabilityReferences} from '../lib/probability.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';

const ID='2113586328423948289';
const input=path.join(ROOT,'.inbox',ID,'18fe9a94c335a9b14193c002ae31631838d0423b24ecbf85b903664359460534','source.json');
const source=JSON.parse(await readFile(input,'utf8'));
const expected=['2/1','2/3','2/8','2/13','2/18','2/23(1)','2/35(2)','3/2','3/7','3/8','3/9','supplement/empty-axioms-v1','1/26'];

test('概率论按书页分章节，保留两个指定小问及补充证明的额外限制',()=>{
 const parsed=parseProbabilityReferences(source.html);
 assert.equal(parsed.supported,true);assert.deepEqual(parsed.refs,expected);
 assert.deepEqual(parseProbabilityReferences('P35\n26').refs,['1/26']);
 assert.deepEqual(parseProbabilityReferences('P65–68\n23（1），35（2）').refs,['2/23(1)','2/35(2)']);
 for(const text of ['P65-68\n1-8','P65-105\n2','P105\n7\n另解附加题','P65\n0'])assert.equal(parseProbabilityReferences(text).supported,false);
 assert.equal(parseProbabilityReferences(source.html.replace('不同于p18 性质4','和p18一样')).supported,false);
 assert.equal(parseProbabilityReferences(source.html+'<p>额外要求：改用其他方法</p>').supported,false);
});

test('概率题库验证真实教材、整组范围和原生Typst；复核后仅处理匹配来源',async t=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-probability-test-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const course={key:source.course.key,siteId:source.course.id,siteName:source.course.name,bookId:source.course.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib','probability.mjs'),'fixture parser');
 await writeFile(path.join(root,'probability_first.py'),'fixture verified solver');
 const book=path.join(root,'book.pdf');await writeFile(book,'textbook version');
 const bank=path.join(root,'题库','probability-bupt-2021');await mkdir(bank,{recursive:true});
 await writeFile(path.join(bank,'question.md'),'verified originals');
 await writeFile(path.join(bank,'solutions.typ'),'native typst answers');
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:course.bookId,generator:'probability_first.py',textbook:book,sha256:hash('textbook version'),requiredRefs:expected,
  exercises:expected.map(key=>({key,file:'question.md',sha256:hash('verified originals'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native typst answers')}],images:[]}));
 const material=await materialDigest(root,course.bookId,expected);assert.equal(material.generator,'probability_first.py');
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:''};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:course.siteId,siteName:course.siteName}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const name of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,name),'verified learning materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const now=Date.parse('2026-10-25T12:00:00+08:00');
 const pending=await runWithClient(client,{root,now,build});assert.equal(pending.needsReview.length,1);
 const review=pending.needsReview[0];await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:review.sourceHash,materialHash:review.materialHash}}));
 assert.equal((await runWithClient(client,{root,now,build})).generated.length,1);
 assert.equal((await runWithClient(client,{root,now,build})).unchanged.length,1);
 client.assignment=async()=>({...detail,assignmentContent:'P65\n1'});
 assert.equal((await runWithClient(client,{root,now,build:async()=>assert.fail('不能用整组生成器处理未经核验的新组合')})).needsReview.length,1);
 await writeFile(book,'another textbook');await assert.rejects(materialDigest(root,course.bookId,expected),/教材已变化/);
});
