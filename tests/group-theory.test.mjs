import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {bindGroupTextbook,parseGroupReferences,GROUP_REFS} from '../lib/group-theory.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
const ID='2118625671952728065';
const source=JSON.parse(await readFile(path.join(ROOT,'.inbox',ID,'1afd0fc778ad2dfea1a59ff9982bff937d1917882f4d14ad05198c9b436cc8aa','source.json'),'utf8'));
const index=JSON.parse(await readFile(path.join(ROOT,'题库/kolman-6/9.1/index.json'),'utf8'));

test('群论按真实章节选教材，按第六版分支选题并核验全部内嵌公式',()=>{
 const c={key:'离散数学',bookId:'rosen-8',chapterBindings:[{chapter:'Group Theory',bookId:'kolman-6'}]};
 assert.equal(bindGroupTextbook(c,{chapterName:'Relations'}).bookId,'rosen-8');
 assert.equal(bindGroupTextbook(c,{chapterName:'Group Theory'}).bookId,'kolman-6');
 assert.equal(bindGroupTextbook({...c,key:'另一课程'},{chapterName:'Group Theory'}).bookId,'rosen-8');
 assert.deepEqual(parseGroupReferences(source.html,source.chapter,index.inlineImageHashes).refs,GROUP_REFS);
 for(const html of [source.html.replace('Sixth Edition','Fifth Edition'),source.html.replace('16, 32, 34','16, 28, 34'),
  source.html+'<p>另证一条性质</p>',source.html.replace('iVBOR','aVBOR')])assert.equal(parseGroupReferences(html,source.chapter,index.inlineImageHashes).supported,false);
 assert.equal(parseGroupReferences(source.html,'Relations',index.inlineImageHashes).supported,false);
});

test('群论新绑定不改变Rosen既有材料指纹；新解答包含版本/正文/依赖校验',async()=>{
 const approved=JSON.parse(await readFile(path.join(ROOT,'approved-tasks.json'),'utf8'));
 for(const [id,refs] of [['2113561808636010497',['9.5/16','9.5/26','9.5/46','9.5/60']],['2117142590505717762',['9.6/4','9.6/16','9.6/32','9.6/44']]])
  assert.equal((await materialDigest(ROOT,'rosen-8',refs)).digest,approved[id].materialHash);
 const material=await materialDigest(ROOT,'kolman-6',GROUP_REFS);
 assert.equal(material.generator,'kolman91.py');assert.deepEqual(material.index.requiredRefs,GROUP_REFS);
 assert.equal(material.index.exercises.find(e=>e.key==='9.1/32').dependencies[0],'images/pdf-0372.png');
});

test('真实课程内新教材来源需重新核对；公式或来源变化不复用；修改/教材变化拦截',async t=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-group-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:'rosen-8',chapterBindings:[{chapter:'Group Theory',bookId:'kolman-6'}]};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));await writeFile(path.join(root,'lib/group-theory.mjs'),'verified binding/parser');
 await writeFile(path.join(root,'kolman91.py'),'verified solver');const book=path.join(root,'book.pdf');await writeFile(book,'exact sixth edition');
 const bank=path.join(root,'题库/kolman-6/9.1');await mkdir(bank,{recursive:true});
 await writeFile(path.join(bank,'question.md'),'original');await writeFile(path.join(bank,'solutions.typ'),'native answer');
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:'kolman-6',generator:'kolman91.py',textbook:book,sha256:hash('exact sixth edition'),requiredRefs:GROUP_REFS,inlineImageHashes:index.inlineImageHashes,
  exercises:GROUP_REFS.map(key=>({key,file:'question.md',sha256:hash('original'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native answer')}],images:[]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:'Group Theory'};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const f of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,f),'complete reviewed learning materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const options={root,now:Date.parse('2026-11-08T20:00:00+08:00'),build};
 const pending=await runWithClient(client,options),p=pending.needsReview[0];assert.deepEqual(p.refs,GROUP_REFS);
 const captured=JSON.parse(await readFile(path.join(p.directory,'source.json'),'utf8'));assert.equal(captured.course.bookId,'kolman-6');
 await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:p.sourceHash,materialHash:p.materialHash}}));
 const generated=await runWithClient(client,options);assert.equal(generated.generated.length,1);
 await writeFile(path.join(generated.generated[0].directory,'解答.md'),'manual notes');
 const repeat=await runWithClient(client,{...options,build:async()=>assert.fail('Must preserve edits')});assert.deepEqual(repeat.unchanged[0].preservedEdits,['解答.md']);
 client.assignment=async()=>({...detail,assignmentContent:source.html.replace('16, 32, 34','16, 28, 34')});
 assert.equal((await runWithClient(client,{...options,build:async()=>assert.fail('Changed version branch')})).needsReview.length,1);
 await writeFile(path.join(bank,'solutions.typ'),'changed');await assert.rejects(materialDigest(root,'kolman-6',GROUP_REFS),/原题、解答或图片已变化/);
 await writeFile(path.join(bank,'solutions.typ'),'native answer');await writeFile(book,'wrong edition');await assert.rejects(materialDigest(root,'kolman-6',GROUP_REFS),/教材已变化/);
});
