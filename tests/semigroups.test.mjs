import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {parseSemigroupReferences,SEMIGROUP_REFS} from '../lib/group-semigroups.mjs';
import {runWithClient,materialDigest,ROOT} from '../run.mjs';
import {hash} from '../lib/workflow.mjs';
const ID='2121152547941277697';
const source=JSON.parse(await readFile(path.join(ROOT,'.inbox',ID,'e1e53bbf97a29c43dc18445990fdf93dec92efcfbc841f376a72fbbaf7007a5a','source.json'),'utf8'));

test('半群按第六版完整三题和内嵌正整数公式路由；既有群论与概率材料稳定',async()=>{
 assert.deepEqual(parseSemigroupReferences(source.html,source.chapter).refs,SEMIGROUP_REFS);
 for(const html of [source.html.replace('20, 30','20, 31'),source.html.replace('Sixth Edition','Fifth Edition'),source.html+'<p>另证一条性质</p>',source.html.replace('iVBOR','aVBOR'),source.html.replace(/<img\b[^>]*>/,''),source.html.replace('给出具体判断依据','无需给出依据')])
  assert.equal(parseSemigroupReferences(html,source.chapter).supported,false);
 assert.equal(parseSemigroupReferences(source.html,'Relations').supported,false);
 const m=await materialDigest(ROOT,'kolman-6',SEMIGROUP_REFS);assert.equal(m.generator,'kolman92.py');assert.deepEqual(m.index.requiredRefs,SEMIGROUP_REFS);
 const approved=JSON.parse(await readFile(path.join(ROOT,'approved-tasks.json'),'utf8'));
 for(const [id,book] of [['2118625671952728065','kolman-6'],['2120815538116870145','probability-bupt-2021']])
  assert.equal((await materialDigest(ROOT,book,approved[id].refs)).digest,approved[id].materialHash);
});

test('半群新来源先核对，审批对应完整素材；重跑保留人工修改',async t=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'bupt-semigroups-'));
 t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
 const c=source.course,course={key:c.key,siteId:c.id,siteName:c.name,bookId:'rosen-8',chapterBindings:[{chapter:'Group Theory',bookId:'kolman-6'}]};
 await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
 await mkdir(path.join(root,'lib'));for(const f of ['group-theory.mjs','group-semigroups.mjs'])await writeFile(path.join(root,'lib',f),'verified parser');
 await writeFile(path.join(root,'kolman92.py'),'verified solver');const book=path.join(root,'book.pdf');await writeFile(book,'exact sixth edition');
 const bank=path.join(root,'题库/kolman-6/9.2');await mkdir(bank,{recursive:true});
 const assets=[['question.md','complete original'],['solutions.typ','native proofs'],['formula.png','positive integer formula']];
 for(const [f,s] of assets)await writeFile(path.join(bank,f),s);
 await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:'kolman-6',section:'9.2',generator:'kolman92.py',textbook:book,sha256:hash('exact sixth edition'),requiredRefs:SEMIGROUP_REFS,
  exercises:SEMIGROUP_REFS.map(key=>({key,file:'question.md',sha256:hash('complete original'),reviewed:true})),extraFiles:[{file:'solutions.typ',sha256:hash('native proofs')}],images:[{file:'formula.png',sha256:hash('positive integer formula')}]}));
 const detail={id:ID,assignmentTitle:source.title,assignmentContent:source.html,assignmentBeginTime:source.assignedAt,assignmentResource:[],chapterName:'Group Theory'};
 const client={user:{id:'fixture'},undone:async()=>[{id:ID,title:source.title,due:source.due}],assignment:async()=>detail,
  read:async p=>p.endsWith('/current')?{records:[{id:c.id,siteName:c.name}],total:1}:[{activityId:ID}]};
 const build=async stage=>{for(const f of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,f),'complete reviewed learning materials '.repeat(4));await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));};
 const options={root,now:Date.parse('2026-11-14T14:00:00+08:00'),build};
 const p=(await runWithClient(client,options)).needsReview[0];assert.deepEqual(p.refs,SEMIGROUP_REFS);
 await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:p.sourceHash,materialHash:p.materialHash}}));
 const generated=await runWithClient(client,options);assert.equal(generated.generated.length,1);
 await writeFile(path.join(generated.generated[0].directory,'解答.md'),'manual notes');
 const repeated=await runWithClient(client,{...options,build:async()=>assert.fail('Preserve existing edits')});assert.deepEqual(repeated.unchanged[0].preservedEdits,['解答.md']);
 client.assignment=async()=>({...detail,assignmentContent:source.html+'<p>追加要求</p>'});
 assert.equal((await runWithClient(client,{...options,build:async()=>assert.fail('Changed source')})).needsReview.length,1);
 for(const [f,s] of assets){await writeFile(path.join(bank,f),'changed');await assert.rejects(materialDigest(root,'kolman-6',SEMIGROUP_REFS),/原题、解答或图片已变化/);await writeFile(path.join(bank,f),s);}
 await writeFile(book,'wrong edition');await assert.rejects(materialDigest(root,'kolman-6',SEMIGROUP_REFS),/教材已变化/);
});
