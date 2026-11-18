import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseProbabilityFourthReferences,FOURTH_REFS} from '../lib/probability-fourth.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
import {readOptionalJson} from './_local.mjs';
const ID='2120815538116870145';
const source=await readOptionalJson('.inbox',ID,'a441d22da30ccc9871577c444af15953b9120293fd2f4056fd6e7809f693eb53','source.json');

test('第四次完整八道教材题及补充证明路由；指定小问和全部附加要求参与核对',async t=>{
 const approval=await readOptionalJson('approved-tasks.json');
 if(!source || !approval)return t.skip('需要本地 .inbox/题库/approved-tasks.json 数据');
 assert.deepEqual(parseProbabilityFourthReferences(source.html).refs,FOURTH_REFS);
 for(const html of [source.html.replace('22(2)','22(1)'),source.html.replace('22(2)','22'),source.html+'\n另证独立性',source.html.split('\n\n')[0]])
  assert.equal(parseProbabilityFourthReferences(html).supported,false);
 const material=await materialDigest(ROOT,'probability-bupt-2021',FOURTH_REFS);
 assert.equal(material.generator,'probability_fourth.py');assert.deepEqual(material.index.requiredRefs,FOURTH_REFS);
 for(const id of ['2113586328423948289','2116142042516131842','2118854975265439746'])
  assert.equal((await materialDigest(ROOT,'probability-bupt-2021',approval[id].refs)).digest,approval[id].materialHash);
});

test('第四次审批绑定来源和原题/解答/图片版本；重跑保留人工注释',async t=>{
 if(!source)return t.skip('需要本地 .inbox 数据');
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-probability-fourth-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:c.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib/probability-fourth.mjs'),'verified parser');
 await writeFile(path.join(root,'probability_fourth.py'),'verified solver');
 const book=path.join(root,'book.pdf');await writeFile(book,'exact edition');
 const bank=path.join(root,'题库',c.bookId,'fourth');await mkdir(bank,{recursive:true});
 const assets=[['question.md','exact question'],['solutions.typ','native answers'],['source.png','scanned page']];
 for(const [f,s] of assets)await writeFile(path.join(bank,f),s);
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:c.bookId,assignment:'fourth',generator:'probability_fourth.py',textbook:book,sha256:hash('exact edition'),requiredRefs:FOURTH_REFS,
  exercises:FOURTH_REFS.map(key=>({key,file:'question.md',sha256:hash('exact question'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native answers')}],images:[{file:'source.png',sha256:hash('scanned page')}]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:''};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const f of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,f),'Complete verified learning materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const options={root,now:Date.parse('2026-11-13T12:00:00+08:00'),build};
 const pending=(await runWithClient(client,options)).needsReview[0];assert.deepEqual(pending.refs,FOURTH_REFS);
 await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:pending.sourceHash,materialHash:pending.materialHash}}));
 const generated=await runWithClient(client,options);assert.equal(generated.generated.length,1);
 await writeFile(path.join(generated.generated[0].directory,'解答.md'),'Manual student annotations');
 const skipped=await runWithClient(client,{...options,build:async()=>assert.fail('Must preserve edits')});
 assert.deepEqual(skipped.unchanged[0].preservedEdits,['解答.md']);
 client.assignment=async()=>({...detail,assignmentContent:source.html+'\n另有附加要求'});
 assert.equal((await runWithClient(client,{...options,build:async()=>assert.fail('Changed source')})).needsReview.length,1);
 for(const [f,s] of assets){await writeFile(path.join(bank,f),'changed');await assert.rejects(materialDigest(root,c.bookId,FOURTH_REFS),/原题、解答或图片已变化/);await writeFile(path.join(bank,f),s);}
 await writeFile(book,'other edition');await assert.rejects(materialDigest(root,c.bookId,FOURTH_REFS),/教材已变化/);
});
