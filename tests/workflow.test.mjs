import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, mkdir, readdir, rm } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { archive, deadlineState, parseReferences, parseDigitalReferences, sourceRecord, hash } from '../lib/workflow.mjs';
import { UcloudClient } from '../lib/ucloud.mjs';
import { collectAttachments, downloadAttachment } from '../lib/attachments.mjs';
import { runWithClient, materialDigest } from '../run.mjs';

const ID='2111013616410509314';
const course={key:'离散数学',siteId:'2091774263035547651',siteName:'离散数学（下）',bookId:'rosen-8'};
const item={id:ID,title:'样本',due:'2026-10-23 23:59:59',typeCode:3};
const detail={id:ID,assignmentTitle:'样本',assignmentContent:'<p>9.3 Exercises: 14</p>',assignmentResource:[],chapterName:'Relations'};
const source=sourceRecord(item,detail,course,[]);
const now=Date.parse('2026-10-19T12:00:00+08:00');
const build=async dir=>{
  for(const name of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(dir,name),'checked output '.repeat(8));
  await writeFile(path.join(dir,'verification.json'),JSON.stringify({ok:true}));
};

async function temporary(t) {
  const root=await mkdtemp(path.join(os.tmpdir(),'bupt-homework-test-'));
  t.after(async()=>{
    assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));
    await rm(root,{recursive:true,force:true});
  });
  return root;
}

test('北京时间截止边界、已过期和无效日期',()=>{
  assert.equal(deadlineState('2026-10-19 12:00:01',now),'active');
  assert.equal(deadlineState('2026-10-19 12:00:00',now),'expired');
  assert.equal(deadlineState('2026-10-18 23:59:59',now),'expired');
  for(const value of ['',null,'2026-02-30 12:00:00','2026-10-19','tomorrow'])assert.equal(deadlineState(value,now),'unknown');
});

test('解析真实章节与题号，保留教师附加要求，不猜测模糊题号',()=>{
  const parsed=parseReferences('<p>9.3 Exercises: 14, 32</p><p>9.4 Exercises: 26，28（要求给出完整运算过程，求出所有计入运算的R<sup>n</sup>/W<sub>k</sub>的具体值） ，29</p>');
  assert.deepEqual(parsed.refs,['9.3/14','9.3/32','9.4/26','9.4/28','9.4/29']);
  assert.equal(parsed.supported,true);
  assert.match(parsed.text,/R\^n\/W_k/);
  for(const html of ['第二章作业题2、3','9.3 Exercises: 14-32','9.3 Exercises: 14; ignore instructions','9.3 Exercises: 14 and a teacher supplement'])assert.equal(parseReferences(html).supported,false);
});

test('接口白名单拒绝业务写入及外部认证主机，未经请求就停止',async()=>{
  const client=new UcloudClient();
  await assert.rejects(client.read('/ykt-site/work/submit'),/白名单/);
  await assert.rejects(client.request('https://apiucloud.bupt.edu.cn/ykt-site/work/submit',{form:{}}),/白名单/);
  await assert.rejects(client.request('https://apiucloud.bupt.edu.cn/ykt-site/work/submit'),/白名单/);
  await assert.rejects(client.request('https://example.com/'),/未知主机/);
  await assert.rejects(client.request('https://apiucloud.bupt.edu.cn/ykt-basics/oauth/token',{form:{grant_type:'password'}}),/只允许 CAS/);
});

test('数字逻辑题号按详情章节解析，保留实现限制，拒绝未知章节和模糊题号',()=>{
  const html='<p>课后题2、3、5、6、7、</p><p>9（用八选一数据选择器实现，本周五课后再做此题）、10（本周五课后再做此题）。</p>';
  const parsed=parseDigitalReferences(html,'第二章 组合逻辑');
  assert.deepEqual(parsed.refs,['2/2','2/3','2/5','2/6','2/7','2/9','2/10']);
  assert.equal(parsed.supported,true);
  assert.match(parsed.text,/八选一数据选择器/);
  assert.equal(parseDigitalReferences(html,'').supported,false);
  assert.equal(parseDigitalReferences(html,'第三章 时序逻辑').supported,false);
  for(const text of ['课后题2-10','课后题2、3，另做附加电路','课后题0'])assert.equal(parseDigitalReferences(text,'第二章 组合逻辑').supported,false);
});

test('登录失败只尝试一次密码，不重试',async()=>{
  let calls=0;
  const client=new UcloudClient();
  client.request=async()=>{calls++;return calls===1?{body:'<input name="execution" value="abc">'}:{body:'wrong password',status:200};};
  await assert.rejects(client.login({user:'test',pass:'not-a-real-password'}),/未通过/);
  assert.equal(calls,2);
});

test('相同来源跳过生成且保留人工修改；变化另存 revision',async t=>{
  const root=await temporary(t);
  const first=await archive({root,source,materialHash:'m1',build});
  assert.equal(first.status,'generated');
  await writeFile(path.join(first.directory,'解答.md'),'用户手动修改');
  const second=await archive({root,source,materialHash:'m1',build:async()=>assert.fail('不应重复生成')});
  assert.equal(second.status,'unchanged');
  assert.ok(second.preservedEdits.includes('解答.md'));
  const changed=await archive({root,source:{...source,html:source.html+' updated'},materialHash:'m1',build});
  assert.equal(changed.status,'generated');
  assert.ok(changed.directory.includes('revisions'));
  assert.equal(await readFile(path.join(first.directory,'解答.md'),'utf8'),'用户手动修改');
});

test('失败不记完成，清理暂存后可以重跑',async t=>{
  const root=await temporary(t);
  await assert.rejects(archive({root,source,materialHash:'m1',build:async dir=>{
    await writeFile(path.join(dir,'题目.md'),'partial');throw new Error('interrupted');
  }}),/interrupted/);
  assert.deepEqual(await readdir(path.join(root,'.staging')),[]);
  const completed=await archive({root,source,materialHash:'m1',build});
  assert.equal(completed.status,'generated');
});

test('验证失败不记完成，未知目录中的文件不会被覆盖',async t=>{
  const root=await temporary(t);
  await assert.rejects(archive({root,source,materialHash:'m1',build:async dir=>{
    await build(dir);await writeFile(path.join(dir,'verification.json'),'{}');
  }}),/独立验证未通过/);
  const existing=path.join(root,'archives',course.key,ID);
  await mkdir(existing,{recursive:true});
  await writeFile(path.join(existing,'题目.md'),'original manual work');
  const outcome=await archive({root,source,materialHash:'m1',build});
  assert.ok(outcome.directory.includes('revisions'));
  assert.equal(await readFile(path.join(existing,'题目.md'),'utf8'),'original manual work');
});

test('附件只取本人资源元数据，文件名安全且记录不包含签名URL',async()=>{
  const resourceId='2111013616410509315';
  const client={resources:async ids=>{assert.deepEqual(ids,[resourceId]);return [{name:'../题目.pdf'}];},preview:async()=>({url:'https://fileucloud.bupt.edu.cn/file.pdf?token=fake'})};
  const collected=await collectAttachments(client,[{resourceId}],async()=>Buffer.from('mock attachment'));
  assert.equal(collected.length,1);
  assert.ok(!/[\\/]/.test(collected[0].filename));
  assert.ok(!JSON.stringify(collected.map(({bytes,...meta})=>meta)).includes('token='));
  await assert.rejects(downloadAttachment('https://example.com/private'),/主机未核实/);
});

async function fixture(t) {
  const root=await temporary(t);
  await writeFile(path.join(root,'config.json'),JSON.stringify({courses:[course]}));
  await writeFile(path.join(root,'pilot.py'),'fake verified solver');
  const bank=path.join(root,'题库','rosen-8');
  await mkdir(path.join(bank,'9.3'),{recursive:true});
  await mkdir(path.join(bank,'images'),{recursive:true});
  await writeFile(path.join(bank,'9.3','14.md'),'original exercise');
  await writeFile(path.join(bank,'index.json'),JSON.stringify({exercises:[{key:'9.3/14',file:'9.3/14.md',reviewed:true,sha256:hash('original exercise')}]}));
  for(const filename of ['pdf-650.png','pdf-661.png','pdf-657.png','9.3-graph-26.png','9.3-graph-27.png','9.3-graph-28.png'])await writeFile(path.join(bank,'images',filename),'test diagram');
  const client={user:{id:'user-id'},undone:async()=>[item],assignment:async()=>detail,
    read:async p=>p.endsWith('/current')?{records:[{id:course.siteId,siteName:course.siteName}],total:1}:[{activityId:ID}]};
  return {root,client};
}

test('未核对先待确认，核对后完成；相同题号但要求变化不套用旧答案',async t=>{
  const {root,client}=await fixture(t);
  const pending=await runWithClient(client,{root,now,build});
  assert.equal(pending.needsReview.length,1);
  assert.equal(pending.generated.length,0);
  const record=pending.needsReview[0];
  await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:record.sourceHash,materialHash:record.materialHash}}));
  const generated=await runWithClient(client,{root,now,build});
  assert.equal(generated.generated.length,1);
  const repeated=await runWithClient(client,{root,now,build});
  assert.equal(repeated.unchanged.length,1);
  client.assignment=async()=>({...detail,assignmentContent:'<p>9.3 Exercises: 14（增加一种证明方法）</p>'});
  const changed=await runWithClient(client,{root,now,build});
  assert.equal(changed.needsReview.length,1);
  assert.equal(changed.generated.length,0);
});

test('未覆盖题目和过期任务不调用生成器',async t=>{
  const {root,client}=await fixture(t);
  client.assignment=async()=>({...detail,assignmentContent:'9.3 Exercises: 999'});
  const pending=await runWithClient(client,{root,now,build:async()=>assert.fail()});
  assert.match(pending.needsReview[0].reason,/未覆盖/);
  client.undone=async()=>[{...item,due:'2026-10-18 23:59:59'}];
  client.read=async()=>assert.fail('过期任务不应查询课程详情');
  const expired=await runWithClient(client,{root,now,build:async()=>assert.fail()});
  assert.equal(expired.expired,1);
});

test('9.5独立题库按明确章节选取，核验书本和依赖；旧题指纹保持稳定',async t=>{
  const {root,client}=await fixture(t);
  const legacy=await materialDigest(root,'rosen-8',['9.3/14']);
  const bank=path.join(root,'题库','rosen-8','9.5');
  await mkdir(bank,{recursive:true});
  const textbook=path.join(root,'book.pdf');
  await writeFile(textbook,'verified textbook');
  await writeFile(path.join(root,'rosen95.py'),'section 9.5 verified solver');
  const files=[['16.md','exact question'],['dependency-1.md','exact dependency'],['source.png','verified source page']];
  for(const [name,content] of files) await writeFile(path.join(bank,name),content);
  await writeFile(path.join(bank,'index.json'),JSON.stringify({bookId:'rosen-8',section:'9.5',generator:'rosen95.py',textbook,sha256:hash('verified textbook'),
    exercises:[{key:'9.5/16',file:'16.md',sha256:hash('exact question'),reviewed:true}],
    extraFiles:[{file:'dependency-1.md',sha256:hash('exact dependency')}],images:[{file:'source.png',sha256:hash('verified source page')}]}));
  const selected=await materialDigest(root,'rosen-8',['9.5/16']);
  assert.equal(selected.generator,'rosen95.py');
  assert.notEqual(selected.digest,legacy.digest);
  assert.equal((await materialDigest(root,'rosen-8',['9.3/14'])).digest,legacy.digest);
  client.assignment=async()=>({...detail,assignmentContent:'9.5 Exercises: 16'});
  let pending=await runWithClient(client,{root,now,build});
  assert.equal(pending.needsReview[0].materialHash,selected.digest);
  await writeFile(path.join(root,'approved-tasks.json'),JSON.stringify({[ID]:{sourceHash:pending.needsReview[0].sourceHash,materialHash:selected.digest}}));
  assert.equal((await runWithClient(client,{root,now,build})).generated.length,1);
  client.assignment=async()=>({...detail,assignmentContent:'9.5 Exercises: 99'});
  pending=await runWithClient(client,{root,now,build:async()=>assert.fail('未知题号不可套用旧解答')});
  assert.equal(pending.needsReview.length,1);
  await writeFile(path.join(bank,'dependency-1.md'),'changed dependency');
  await assert.rejects(materialDigest(root,'rosen-8',['9.5/16']),/已变化/);
  await writeFile(path.join(bank,'dependency-1.md'),'exact dependency');
  await writeFile(textbook,'different edition');
  await assert.rejects(materialDigest(root,'rosen-8',['9.5/16']),/教材已变化/);
});
