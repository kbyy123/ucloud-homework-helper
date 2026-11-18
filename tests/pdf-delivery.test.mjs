import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {deliveryName,publishPdf} from '../lib/pdf-delivery.mjs';
import {hash,sourceRecord,archive} from '../lib/workflow.mjs';

const source={id:'2113561808636010497',title:'第四次作业：等价关系',assignedAt:'2026-10-23 17:22',due:'2026-10-30 23:59:59',course:{key:'离散数学'}};

async function temporary(t) {
  const root=await mkdtemp(path.join(os.tmpdir(),'bupt-pdf-test-'));
  t.after(async()=>{assert.ok(path.resolve(root).startsWith(path.resolve(os.tmpdir())+path.sep));await rm(root,{recursive:true,force:true});});
  return root;
}

test('PDF名称只使用真实布置日期，提取作业序号并验证日历和文件名',()=>{
  assert.equal(deliveryName(source).filename,'10.23-第四次作业.pdf');
  assert.equal(deliveryName(source).relativePath,'离散数学/10.23-第四次作业.pdf');
  assert.equal(deliveryName({...source,title:'第一次',course:{key:'概率论与随机过程'}}).relativePath,'概率论与随机过程/10.23-第一次作业.pdf');
  assert.throws(()=>deliveryName({...source,title:'第一次课的练习'}),/第几次作业/);
  assert.equal(deliveryName({...source,title:'第二章第一次作业',course:{key:'数字逻辑'}}).relativePath,'数字逻辑/10.23-第一次作业.pdf');
  assert.equal(deliveryName({...source,assignedAt:'2028-02-29 08:00:00'}).assignedDate,'2028-02-29');
  for(const assignedAt of [undefined,'','2026-02-29 12:00','2026-10-23 24:00'])assert.throws(()=>deliveryName({...source,assignedAt}),/布置时间/);
  assert.throws(()=>deliveryName({...source,title:'期中复习'}),/第几次作业/);
  assert.throws(()=>deliveryName({...source,course:{key:'../坏目录'}}),/课程名/);
});

test('来源指纹包含平台真实assignmentBeginTime，绝不使用截止时间补日期',()=>{
  const item={id:source.id,title:source.title,due:source.due};
  const course={key:'离散数学',siteId:'2091774263035547651',siteName:'离散数学（下）',bookId:'rosen-8'};
  const detail={id:source.id,assignmentTitle:source.title,assignmentContent:'9.5 Exercises: 16',assignmentBeginTime:source.assignedAt};
  const recorded=sourceRecord(item,detail,course);
  assert.equal(recorded.assignedAt,source.assignedAt);
  const unknown=sourceRecord(item,{...detail,assignmentBeginTime:undefined},course);
  assert.equal(unknown.assignedAt,undefined);
  assert.notEqual(hash(recorded),hash(unknown));
});

test('集中输出幂等，同名人工修改和其他作业冲突均保留；失败后可恢复',async t=>{
  const root=await temporary(t),directory=path.join(root,'archive');await mkdir(directory);
  const pdf=Buffer.from('%PDF-1.7\nmock compiled PDF');
  await writeFile(path.join(directory,'解答.pdf'),pdf);
  await writeFile(path.join(directory,'解答.typ'),'native typst source');
  const record={engine:'typst',sourceHash:hash(source),filename:deliveryName(source).filename,pdfSha256:hash(pdf),typstSha256:hash('native typst source'),pages:1};
  await writeFile(path.join(directory,'pdf-verification.json'),JSON.stringify(record));
  const first=await publishPdf({root,source,directory});
  const again=await publishPdf({root,source,directory});assert.equal(again.pdf,first.pdf);
  await writeFile(first.pdf,'manual edit');
  await assert.rejects(publishPdf({root,source,directory}),/人工修改/);
  assert.equal(await readFile(first.pdf,'utf8'),'manual edit');
  await writeFile(first.pdf,pdf);
  const other={...source,id:'2113561808636010498'};
  await writeFile(path.join(directory,'pdf-verification.json'),JSON.stringify({...record,sourceHash:hash(other)}));
  await assert.rejects(publishPdf({root,source:other,directory}),/其他作业/);
  await writeFile(path.join(directory,'pdf-verification.json'),JSON.stringify(record));
  await writeFile(path.join(directory,'解答.pdf'),'invalid changed archive');
  await assert.rejects(publishPdf({root,source,directory}),/已被修改/);
  await writeFile(path.join(directory,'解答.pdf'),pdf);
  assert.equal((await publishPdf({root,source,directory})).pdf,first.pdf);
});

test('要求PDF时，只有数学核验通过但缺少编译产物仍不能记完成',async t=>{
  const root=await temporary(t);
  await assert.rejects(archive({root,source,materialHash:'with-pdf',requirePdf:true,build:async stage=>{
    for(const file of ['题目.md','解答.md','核对记录.md'])await writeFile(path.join(stage,file),'reviewed content '.repeat(8));
    await writeFile(path.join(stage,'verification.json'),JSON.stringify({ok:true}));
  }}),/编译验证未通过/);
});

test('同一作业的新归档更新受管理PDF，保留旧归档字节',async t=>{
  const root=await temporary(t);
  let published;
  for(const version of ['old','new']) {
    const directory=path.join(root,'archive-'+version);await mkdir(directory);
    const pdf='%PDF-1.7\n'+version;
    await writeFile(path.join(directory,'解答.pdf'),pdf);
    await writeFile(path.join(directory,'解答.typ'),version);
    await writeFile(path.join(directory,'pdf-verification.json'),JSON.stringify({engine:'typst',sourceHash:hash(source),
      filename:deliveryName(source).filename,pdfSha256:hash(pdf),typstSha256:hash(version),pages:1}));
    published=await publishPdf({root,source,directory});
  }
  assert.equal(await readFile(published.pdf,'utf8'),'%PDF-1.7\nnew');
  assert.equal(await readFile(path.join(root,'archive-old','解答.pdf'),'utf8'),'%PDF-1.7\nold');
});
