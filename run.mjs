import { access, readFile, mkdir, writeFile, open, unlink } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { UcloudClient } from './lib/ucloud.mjs';
import { collectAttachments } from './lib/attachments.mjs';
import { archive, hash, readJson, exclusiveJson, deadlineState, parseReferences, parseDigitalReferences, sourceRecord, safeId } from './lib/workflow.mjs';
import {pdfDeliveryDigest,deliveryName,compileAnswer,publishPdf} from './lib/pdf-delivery.mjs';
import {parseProbabilityReferences} from './lib/probability.mjs';
import {parseComputerReferences} from './lib/computer.mjs';
import {parseProbabilitySecondReferences} from './lib/probability-second.mjs';
import {parseProbabilityFourthReferences} from './lib/probability-fourth.mjs';
import {bindGroupTextbook,parseGroupReferences} from './lib/group-theory.mjs';
import {parseSemigroupReferences,SEMIGROUP_REFS} from './lib/group-semigroups.mjs';
import {AI_BOOK,AI_POLICY,aiReferences,aiMaterialDigest} from './lib/ai-algorithms.mjs';

export const ROOT = path.dirname(fileURLToPath(import.meta.url));
const exec = promisify(execFile);

async function resolveGenerator(root, file) {
  const inDir = path.join(root, 'generators', file);
  try { await access(inDir); return inDir; } catch { return path.join(root, file); }
}

export async function materialDigest(root = ROOT, bookId = 'rosen-8', refs = []) {
  const material=await bookMaterialDigest(root,bookId,refs);
  if(material && (await readJson(path.join(root,'config.json')))?.delivery?.format==='typst') {
    return {...material,exerciseDigest:material.digest,digest:hash({exercise:material.digest,pdf:await pdfDeliveryDigest(root)})};
  }
  return material;
}

async function bookMaterialDigest(root, bookId, refs) {
  if (!/^[a-z0-9-]+$/.test(bookId)) throw new Error('教材标识无效');
  if(bookId===AI_BOOK)return aiMaterialDigest(root,refs);
  if(bookId==='kolman-6' && refs.length===SEMIGROUP_REFS.length && SEMIGROUP_REFS.every(ref=>refs.includes(ref))) {
    const bank=path.join(root,'题库',bookId,'9.2'),index=await readJson(path.join(bank,'index.json'));
    if(!index)return null;
    if(index.bookId!==bookId || index.section!=='9.2' || index.generator!=='kolman92.py')throw Error('半群教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib/group-semigroups.mjs')))],['binding',hash(await readFile(path.join(root,'lib/group-theory.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw Error('群论教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file)||item.file.split(/[\\/]/).includes('..'))throw Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw Error('半群原题、解答或图片已变化，需复核');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  if(bookId==='probability-bupt-2021' && refs.includes('supplement/bivariate-normal-correlation-v1')) {
    const bank=path.join(root,'题库',bookId,'fourth'),index=await readJson(path.join(bank,'index.json'));
    if(!index)return null;
    if(index.bookId!==bookId || index.assignment!=='fourth' || index.generator!=='probability_fourth.py')
      throw new Error('概率第四次教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],
      ['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib','probability-fourth.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw new Error('概率教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..'))throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw new Error('概率第四次原题、解答或图片已变化，需复核');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  if(bookId==='kolman-6') {
    const bank=path.join(root,'题库',bookId,'9.1'),index=await readJson(path.join(bank,'index.json'));
    if(!index)return null;
    if(index.bookId!==bookId||index.generator!=='kolman91.py')throw Error('群论教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib','group-theory.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw Error('群论教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file)||item.file.split(/[\\/]/).includes('..'))throw Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw Error('群论原题、解答或图片已变化，需重新核对');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  const thirdRefs=['3/21','3/28','3/29','4/2','4/5','4/6(2)','4/7(2)','1/40','1/42','1/47'];
  if(bookId==='probability-bupt-2021' && refs.length===thirdRefs.length && thirdRefs.every(ref=>refs.includes(ref))) {
    const bank=path.join(root,'题库',bookId,'third'),index=await readJson(path.join(bank,'index.json'));
    if(!index)return null;
    if(index.bookId!==bookId || index.assignment!=='third' || index.generator!=='probability_third.py')throw new Error('概率第三次教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib','probability.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw new Error('概率教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..'))throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw new Error('概率第三次题库原文、解答或图片已变化，需复核');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  if(bookId==='probability-bupt-2021' && refs.includes('supplement/inclusion-exclusion-induction-v1')) {
    const bank=path.join(root,'题库',bookId,'second'),index=await readJson(path.join(bank,'index.json'));
    if(!index)return null;
    if(index.bookId!==bookId || index.generator!=='probability_second.py')throw new Error('概率第二次教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib','probability-second.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw new Error('概率教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..'))throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw new Error('概率第二次题库原文、解答或图片已变化，需复核');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  // Keep the earlier 9.3/9.4 approval fingerprints stable. New sections have
  // their own source-checked bank and explicitly registered generator.
  if (bookId==='rosen-8' && refs.length && refs.every(ref=>ref.startsWith('9.6/'))) {
    const bank=path.join(root,'题库',bookId,'9.6');
    const index=await readJson(path.join(bank,'index.json'));
    if (!index) return null;
    if (index.bookId!==bookId || index.section!=='9.6' || index.generator!=='rosen96.py') throw new Error('教材章节或生成器绑定变化，需重新核对');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,'rosen96.py')))]];
    const actualBook=hash(await readFile(index.textbook));
    if (actualBook!==index.sha256) throw new Error('离散数学教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for (const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if (path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..')) throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if (hash(content)!==item.sha256) throw new Error('离散数学题库原文、解答或图片已变化，需重新核对索引');
      parts.push([item.key || item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:'rosen96.py'};
  }
  if (bookId==='rosen-8' && refs.length && refs.every(ref=>ref.startsWith('9.5/'))) {
    const bank=path.join(root,'题库',bookId,'9.5');
    const index=await readJson(path.join(bank,'index.json'));
    if (!index) return null;
    if (index.bookId!==bookId || index.section!=='9.5' || index.generator!=='rosen95.py') throw new Error('教材章节或生成器绑定变化，需重新核对');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,'rosen95.py')))]];
    const actualBook=hash(await readFile(index.textbook));
    if (actualBook!==index.sha256) throw new Error('离散数学教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for (const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if (path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..')) throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if (hash(content)!==item.sha256) throw new Error('离散数学题库原文或图片已变化，需重新核对索引');
      parts.push([item.key || item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:'rosen95.py'};
  }
  const chapter5Refs=['5/3','5/6','5/8','5/16'];
  const computerChapter5=bookId==='computer-organization-7' &&
    refs.length===chapter5Refs.length && chapter5Refs.every(ref=>refs.includes(ref));
  const bank=path.join(root,'题库',bookId,...(computerChapter5?['5']:[]));
  const index=await readJson(path.join(bank,'index.json'));
  if (!index) return null;
  if(bookId==='probability-bupt-2021' || bookId==='computer-organization-7') {
    const computer=bookId==='computer-organization-7';
    const label=computer?'计算机组成原理':'概率论';
    const expectedGenerator=computerChapter5?'computer_ch5.py':computer?'computer_ch4.py':'probability_first.py';
    if(index.bookId!==bookId || index.generator!==expectedGenerator)throw new Error(label+'教材或生成器绑定变化，需复核');
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,index.generator)))],
      ['parser',hash(await readFile(path.join(root,'lib',computer?'computer.mjs':'probability.mjs')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256)throw new Error(label+'教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.extraFiles,...index.images]) {
      if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..'))throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256)throw new Error(label+'题库原文、解答或图片已变化，需复核');
      parts.push([item.key||item.file,hash(content)]);
    }
    return {digest:hash(parts),index,generator:index.generator};
  }
  if(bookId==='digital-logic-7') {
    const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,'digital_ch2.py')))]];
    const actualBook=hash(await readFile(index.textbook));
    if(actualBook!==index.sha256) throw new Error('数字逻辑教材已变化，需重新核对版本');
    parts.push(['textbook',actualBook]);
    for(const item of [...index.exercises,...index.images]) {
      if(path.isAbsolute(item.file) || item.file.split(/[\\/]/).includes('..')) throw new Error('题库路径越界');
      const content=await readFile(path.join(bank,item.file));
      if(hash(content)!==item.sha256) throw new Error('数字逻辑题库原文或图片已变化，需重新核对索引');
      parts.push([item.key || item.file,hash(content)]);
    }
    return {digest:hash(parts),index};
  }
  const parts=[['index',hash(await readFile(path.join(bank,'index.json')))],['solver',hash(await readFile(await resolveGenerator(root,'pilot.py')))]];
  for (const exercise of index.exercises) {
    if (path.isAbsolute(exercise.file) || exercise.file.split(/[\\/]/).includes('..')) throw new Error('题库路径越界');
    const content=await readFile(path.join(bank,exercise.file));
    if (hash(content)!==exercise.sha256) throw new Error('题库转录已变化，需重新核对索引');
    parts.push([exercise.key,hash(content)]);
  }
  // The diagram and source-page hashes are part of the approval, too.
  for (const filename of ['pdf-650.png','pdf-661.png','pdf-657.png','9.3-graph-26.png','9.3-graph-27.png','9.3-graph-28.png']) {
    parts.push([filename,hash(await readFile(path.join(bank,'images',filename)))]);
  }
  return { digest:hash(parts),index };
}

async function inbox(root,source,attachments=[]) {
  const dir=path.join(root,'.inbox',safeId(source.id),hash(source));
  await exclusiveJson(path.join(dir,'source.json'),source);
  for (const attachment of attachments) {
    const file=path.join(dir,'attachments',attachment.filename);
    await mkdir(path.dirname(file),{recursive:true});
    try { await writeFile(file,attachment.bytes,{flag:'wx'}); } catch(e) { if(e.code!=='EEXIST')throw e; }
  }
  return dir;
}

export async function runWithClient(client, { root=ROOT, onlyId=null, now=Date.now(), captureOnly=false, build=null } = {}) {
  const config=await readJson(path.join(root,'config.json'));
  if (!config?.courses?.length) throw new Error('缺少课程配置');
  const items=await client.undone();
  const result={ok:true,checkedAt:new Date(now).toISOString(),generated:[],unchanged:[],needsReview:[],expired:0,unconfigured:0};
  const selected=items.filter(it=>(!onlyId || it.id===onlyId));
  if (onlyId && !selected.length) throw new Error('目标不在当前未完成列表；不处理已完成作业');
  const active=[];
  for (const item of selected) {
    const status=deadlineState(item.due,now);
    if (status==='active') active.push(item);
    else if (status==='expired') result.expired++;
    else result.needsReview.push({id:item.id,title:item.title,reason:'截止时间未知，未自动作答'});
  }
  if (!active.length) return result;
  const current=await client.read('/ykt-site/site/list/student/current',{userId:client.user.id,current:1,size:100});
  if (!Array.isArray(current?.records) || current.total>current.records.length) throw new Error('本人课程列表不完整，停止以免错误绑定');
  const membership=new Map();
  for (const course of config.courses) {
    const actual=current.records.find(it=>String(it.id)===course.siteId);
    if (!actual) continue;
    if (actual.siteName!==course.siteName) throw new Error('课程名称或绑定已变化，需人工确认');
    const activities=await client.read('/ykt-site/site/list/activity',{siteId:course.siteId,type:3});
    if (!Array.isArray(activities)) throw new Error('课程活动列表结构变化，停止');
    for (const activity of activities) {
      const id=String(activity.activityId);
      if (membership.has(id)) throw new Error('同一作业出现多个课程归属，需人工确认');
      membership.set(id,course);
    }
  }
  for (const item of active) {
    const memberCourse=membership.get(item.id);
    if (!memberCourse) { result.unconfigured++; continue; }
    const detail=await client.assignment(item.id);
    const course=bindGroupTextbook(memberCourse,detail);
    const resources=detail.assignmentResource;
    if (!Array.isArray(resources)) throw new Error('作业缺少明确的附件列表，需人工确认');
    const attachments=await collectAttachments(client,resources);
    const source=sourceRecord(item,detail,course,attachments.map(({bytes,...meta})=>meta));
    // Store resource identity and downloaded digest, never signed URLs or credentials.
    source.resources=resources.map(r=>({id:String(r.resourceId || r.id || ''),name:String(r.name || r.resourceName || '')}));
    const dir=await inbox(root,source,attachments);
    if(config.delivery?.format==='typst') {
      try {deliveryName(source);} catch(e) {
        result.needsReview.push({id:item.id,title:item.title,reason:e.message,directory:dir,sourceHash:hash(source)});
        continue;
      }
    }
    const probabilitySecond=course.bookId==='probability-bupt-2021'?parseProbabilitySecondReferences(source.html):null;
    const probabilityFourth=course.bookId==='probability-bupt-2021'?parseProbabilityFourthReferences(source.html):null;
    const groupIndex=course.bookId==='kolman-6'?await readJson(path.join(root,'题库','kolman-6','9.1','index.json')):null;
    const semigroup=course.bookId==='kolman-6'?parseSemigroupReferences(source.html,source.chapter):null;
    const parsed=course.bookId===AI_BOOK?aiReferences(source):
      course.bookId==='kolman-6'?(semigroup.supported?semigroup:parseGroupReferences(source.html,source.chapter,groupIndex?.inlineImageHashes)):
      course.bookId==='digital-logic-7'?parseDigitalReferences(source.html,source.chapter):
      course.bookId==='probability-bupt-2021'?(probabilityFourth.supported?probabilityFourth:probabilitySecond.supported?probabilitySecond:parseProbabilityReferences(source.html)):
      course.bookId==='computer-organization-7'?parseComputerReferences(source.html):parseReferences(source.html);
    const material=await materialDigest(root,course.bookId,parsed.refs);
    const approvals=await readJson(path.join(root,'approved-tasks.json')) || {};
    const approved=approvals[item.id];
    const covered=material && parsed.supported && parsed.refs.every(ref=>material.index.exercises.some(e=>e.key===ref && e.reviewed)) &&
      (!material.index.requiredRefs || (parsed.refs.length===material.index.requiredRefs.length && material.index.requiredRefs.every(ref=>parsed.refs.includes(ref))));
    // AI homework is defined by its complete source, including attachment hashes.
    const attachmentsReviewed=course.bookId===AI_BOOK &&
      material?.index.sourceHash===hash(source) && material.index.requirementsReview?.allAttachmentsRead===true;
    const ready=!captureOnly && covered && (!attachments.length || attachmentsReviewed) && approved?.sourceHash===hash(source) && approved?.materialHash===material.digest;
    if (!ready) {
      result.needsReview.push({id:item.id,title:item.title,reason:course.bookId===AI_BOOK?
        '数据结构作业需agent核对正文及全部附件，整理Typst、C风格C++和测试结果，按要求补充讲解文稿':
        !parsed.supported?'题号无法可靠解析，需核对正文和附件':!covered?'已核验解答未覆盖；agent 应定位准确原题、整理作答并核验':'来源或材料尚未核对，交给 agent 复核',directory:dir,
        refs:parsed.refs,sourceHash:hash(source),materialHash:material?.digest || null,
        ...(course.bookId===AI_BOOK?{workflow:AI_POLICY}:{})});
      continue;
    }
    const generator=material.generator || {'rosen-8':'pilot.py','digital-logic-7':'digital_ch2.py'}[course.bookId];
    if (!generator) throw new Error('尚未为此教材注册已验证的生成器');
    const python=(typeof process !== 'undefined' ? process.env.HOMEWORK_PYTHON : null) || (await readJson(path.join(root,'runtime.json')))?.python;
    if (!python && !build) throw new Error('未配置 Python 运行时');
    const outcome=await archive({root,source,materialHash:material.digest,requirePdf:config.delivery?.format==='typst',build:async stage=>{
      if(build)await build(stage);
      else await exec(python,[await resolveGenerator(root,generator),'--source',path.join(stage,'source.json'),'--out',stage],
        {windowsHide:true,timeout:120000,maxBuffer:2*1024*1024});
      if(config.delivery?.format==='typst')await compileAnswer({root,stage,source});
    }});
    const delivery=config.delivery?.format==='typst'?await publishPdf({root,source,directory:outcome.directory}):{};
    result[outcome.status==='generated'?'generated':'unchanged'].push({id:item.id,...outcome,...delivery});
  }
  return result;
}

export async function main(args=process.argv.slice(2)) {
  const onlyId=args.find(s=>s.startsWith('--id='))?.slice(5) || null;
  if (onlyId) safeId(onlyId);
  if (args.some(arg=>!arg.startsWith('--id=') && arg!=='--capture-only')) throw new Error('未知参数；仅支持 --id=待办ID 和 --capture-only');
  const lockFile=path.join(ROOT,'.run.lock');
  let lock;
  try { lock=await open(lockFile,'wx'); }
  catch(e) { if(e.code==='EEXIST') throw new Error('已有运行锁；确认没有其他运行后才能手动清除 .run.lock'); throw e; }
  const client=new UcloudClient();
  try {
    await lock.writeFile(JSON.stringify({pid:process.pid,startedAt:new Date().toISOString()}));
    await client.login();
    const result=await runWithClient(client,{onlyId,captureOnly:args.includes('--capture-only')});
    console.log(JSON.stringify(result,null,2));
    if (result.needsReview.length) process.exitCode=2;
  } finally {
    client.close();
    delete process.env.UC_PASS;
    await lock.close();
    await unlink(lockFile);
  }
}

if (typeof process !== 'undefined' && process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(error=>{
    // Do not echo response bodies, URLs, form fields, or child-process environment.
    console.error(JSON.stringify({ok:false,error:error.stderr ? '题目生成器或Typst/PDF编译失败，请检查对应源文件与运行时' : error.message}));
    process.exitCode=1;
  });
}
