import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseComputerReferences} from '../lib/computer.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
import {readOptionalJson} from './_local.mjs';

const ID='2113174433014059010';
const expected=['4/2','4/7','4/8','4/9','4/11','4/12','4/17'];
const source=await readOptionalJson('.inbox',ID,'08909035409c496381de81cd71f2da66f2a02f92e091957b44636d4bfc327cb0','source.json');

test('计组从真实正文解析章号与七题；附加要求、范围和不明确小问不悄悄丢弃',t=>{
 if(!source)return t.skip('需要本地 .inbox 数据');
 assert.deepEqual(parseComputerReferences(source.html).refs,expected);
 assert.equal(parseComputerReferences(source.html).supported,true);
 assert.deepEqual(parseComputerReferences('第10章课后习题：1,2。').refs,['10/1','10/2']);
 for(const html of ['第二次作业','第四章课后习题：2—17。','第四章课后习题：8(1)。','第四章课后习题：0。','第四章课后习题：2、2。',source.html+'<p>另给第二种解法</p>'])assert.equal(parseComputerReferences(html).supported,false,html);
});

test('计组题库指纹包含解答与教材，只有完整七题及匹配复核记录才生成；重跑保留人工修改',async t=>{
 if(!source)return t.skip('需要本地 .inbox 数据');
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-computer-test-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const course={key:source.course.key,siteId:source.course.id,siteName:source.course.name,bookId:source.course.bookId};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib','computer.mjs'),'fixture parser');
 await writeFile(path.join(root,'computer_ch4.py'),'fixture verified solver');
 const book=path.join(root,'book.pdf');await writeFile(book,'verified book version');
 const bank=path.join(root,'题库',course.bookId);await mkdir(bank,{recursive:true});
 await writeFile(path.join(bank,'question.md'),'complete originals');await writeFile(path.join(bank,'solutions.typ'),'native answers');
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:course.bookId,generator:'computer_ch4.py',textbook:book,sha256:hash('verified book version'),requiredRefs:expected,
  exercises:expected.map(key=>({key,file:'question.md',sha256:hash('complete originals'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native answers')}],images:[]}));
 const material=await materialDigest(root,course.bookId,expected);assert.equal(material.generator,'computer_ch4.py');
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:source.chapter};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:course.siteId,siteName:course.siteName}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const name of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,name),'verified learning material '.repeat(5));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const now=Date.parse('2026-10-25T12:00:00+08:00');
 const pending=await runWithClient(client,{root,now,build});assert.equal(pending.needsReview.length,1);
 const review=pending.needsReview[0];await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:review.sourceHash,materialHash:review.materialHash}}));
 const generated=await runWithClient(client,{root,now,build});assert.equal(generated.generated.length,1);
 const manual=path.join(generated.generated[0].directory,'解答.md');await writeFile(manual,'manual correction');
 assert.equal((await runWithClient(client,{root,now,build:async()=>assert.fail('Same material must not rebuild')})).unchanged.length,1);
 assert.equal(await readFile(manual,'utf8'),'manual correction');
 client.assignment=async()=>({...detail,assignmentContent:'第四章课后习题：2。'});
 assert.equal((await runWithClient(client,{root,now,build:async()=>assert.fail('Subset cannot run full group solver')})).needsReview.length,1);
 await writeFile(path.join(bank,'solutions.typ'),'manual answer changes');await assert.rejects(materialDigest(root,course.bookId,expected),/解答或图片已变化/);
 await writeFile(path.join(bank,'solutions.typ'),'native answers');await writeFile(book,'another edition');await assert.rejects(materialDigest(root,course.bookId,expected),/教材已变化/);
});
