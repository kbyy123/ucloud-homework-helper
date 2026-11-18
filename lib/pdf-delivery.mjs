import {readFile,writeFile,mkdir,copyFile,rename,open,unlink,constants} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {randomUUID} from 'node:crypto';
import {hash,readJson} from './workflow.mjs';

const exec=promisify(execFile);
const MODULE=fileURLToPath(import.meta.url);

// assignmentBeginTime is verified against the real student detail endpoint.
// Never substitute deadline, download time, file mtime, or a date encoded in an ID.
export function deliveryName(source) {
  const match=/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?$/.exec(source.assignedAt || '');
  if (!match) throw new Error('缺少可靠布置时间 assignmentBeginTime，不能猜测PDF文件日期');
  const [year,month,day,hour,minute,second]=match.slice(1).map(n=>Number(n || 0));
  const check=new Date(Date.UTC(year,month-1,day,hour,minute,second));
  if(check.toISOString().slice(0,19)!==`${match[1]}-${match[2]}-${match[3]}T${match[4]}:${match[5]}:${match[6] || '00'}`)throw new Error('布置时间无效');
  const course=source.course?.key;
  if(!course || /[<>:"/\\|?*\x00-\x1f]/.test(course) || /[. ]$/.test(course))throw new Error('课程名不适合PDF文件名');
  const ordinal='第[零〇一二三四五六七八九十百千万两\\d]+次';
  const assignment=source.title?.match(new RegExp(ordinal+'作业'))?.[0] ||
    (new RegExp('^'+ordinal+'$').test(source.title||'')?source.title+'作业':null) ||
    (source.course?.bookId==='ai-algorithms-2026' &&
      /^第[零〇一二三四五六七八九十百千万两\d]+章作业$/.test(source.title||'')?source.title:null);
  if(!assignment)throw new Error('标题没有明确第几次作业，需核实命名后再输出PDF');
  const filename=`${match[2]}.${match[3]}-${assignment}.pdf`;
  const legacyFilename=`${match[2]}.${match[3]}-${course}-${assignment}.pdf`;
  return {filename,relativePath:`${course}/${filename}`,legacyFilename,course,assignment,
    assignedDate:`${match[1]}-${match[2]}-${match[3]}`,dateField:'assignmentBeginTime',assignedAt:source.assignedAt};
}

export async function pdfDeliveryDigest(root) {
  const runtime=await readJson(path.join(root,'runtime.json'));
  if(!runtime?.typst)throw new Error('缺少Typst运行时配置');
  const parts=[];
  for(const file of [MODULE,path.join(root,'templates','homework.typ'),path.join(root,'scripts','check-pdf.py'),runtime.typst])parts.push(hash(await readFile(file)));
  return hash({format:'typst-pdf-v2',runtime:{typst:runtime.typst},parts});
}

export async function compileAnswer({root,stage,source}) {
  const naming=deliveryName(source);
  const runtime=await readJson(path.join(root,'runtime.json'));
  const input=path.join(stage,'解答.typ'),pdf=path.join(stage,'解答.pdf');
  if(!await exists(input)) throw new Error('缺少原生 Typst 源文件 解答.typ');
  const compiled=await exec(runtime.typst,['compile','--root',stage,'--diagnostic-format','short',input,pdf],
    {windowsHide:true,timeout:120000,maxBuffer:4*1024*1024});
  if(compiled.stderr.trim())throw new Error('Typst编译存在警告，需检查字体、公式或资源');
  const {stdout}=await exec(runtime.python,[path.join(root,'scripts','check-pdf.py'),pdf],
    {windowsHide:true,timeout:60000,maxBuffer:2*1024*1024});
  const check=JSON.parse(stdout);
  if(check.ok!==true)throw new Error('编译PDF验证失败');
  const record={schema:1,ok:true,engine:'typst',...naming,sourceHash:hash(source),pdfSha256:hash(await readFile(pdf)),typstSha256:hash(await readFile(input)),pages:check.pages};
  await writeFile(path.join(stage,'pdf-verification.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  return record;
}

async function exists(file) {try {await readFile(file);return true;}catch(e){if(e.code==='ENOENT')return false;throw e;}}

// Publish only a compiled, archived PDF. The registry guards manual edits and
// filename collisions, and a failed copy can be retried without regenerating.
export async function publishPdf({root,source,directory}) {
  const naming=deliveryName(source);
  const record=await readJson(path.join(directory,'pdf-verification.json'));
  const pdf=await readFile(path.join(directory,'解答.pdf'));
  const validFilename=record?.filename===naming.filename || record?.filename===naming.legacyFilename;
  if(record?.engine!=='typst' || record.sourceHash!==hash(source) || !validFilename || record.pdfSha256!==hash(pdf) || record.typstSha256!==hash(await readFile(path.join(directory,'解答.typ'))))throw new Error('归档PDF缺少有效编译记录或源文件已被修改，需重新核验');
  const output=path.join(root,'output',naming.course);await mkdir(output,{recursive:true});
  const lockPath=path.join(root,'.pdf-output.lock');
  const lock=await open(lockPath,'wx');
  try {
    const registryPath=path.join(root,'pdf-output.json');
    const registry=await readJson(registryPath) || {schema:1,files:{}};
    const registryKey=naming.relativePath;
    const target=path.join(output,naming.filename),previous=registry.files[registryKey];
    let current=null;try {current=hash(await readFile(target));}catch(e){if(e.code!=='ENOENT')throw e;}
    if(current===record.pdfSha256) {
      if(previous && previous.id!==source.id)throw new Error('同名PDF属于其他作业，保留现有文件');
    } else if(current) {
      if(!previous || previous.id!==source.id || previous.pdfSha256!==current)throw new Error('output中同名PDF已有人工修改或来自其他来源，保留文件并交给agent核对');
      const temporary=target+'.'+randomUUID()+'.new';
      try {
        await copyFile(path.join(directory,'解答.pdf'),temporary,constants.COPYFILE_EXCL);
        if(hash(await readFile(target))!==current)throw new Error('输出PDF在发布期间被修改，保留人工修改');
        await rename(temporary,target);
      } finally {await unlink(temporary).catch(e=>{if(e.code!=='ENOENT')throw e;});}
    } else await copyFile(path.join(directory,'解答.pdf'),target,constants.COPYFILE_EXCL);
    registry.files[registryKey]={id:source.id,sourceHash:hash(source),pdfSha256:record.pdfSha256,directory,
      assignedAt:source.assignedAt,dateField:naming.dateField,updatedAt:previous?.pdfSha256===record.pdfSha256?previous.updatedAt:new Date().toISOString()};
    const registryTemporary=registryPath+'.'+randomUUID()+'.new';
    try {
      await writeFile(registryTemporary,JSON.stringify(registry,null,2)+'\n',{flag:'wx'});await rename(registryTemporary,registryPath);
    } finally {await unlink(registryTemporary).catch(e=>{if(e.code!=='ENOENT')throw e;});}
    return {pdf:target,typst:path.join(directory,'解答.typ'),pages:record.pages};
  } finally {await lock.close();await unlink(lockPath);}
}
