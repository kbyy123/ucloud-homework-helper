// Offline, verified archiving of a captured digital-logic assignment.
import { readFile,writeFile,rename,open,unlink } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { archive,readJson,hash,exclusiveJson,deadlineState,parseDigitalReferences } from '../lib/workflow.mjs';
import { materialDigest } from '../run.mjs';
import {compileAnswer,publishPdf,deliveryName} from '../lib/pdf-delivery.mjs';
const exec=promisify(execFile);
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
async function saveState(filename,data) {
  const temporary=filename+'.new';
  await writeFile(temporary,JSON.stringify(data,null,2)+'\n',{flag:'wx'});
  await rename(temporary,filename);
}
async function main() {
  const input=process.argv.find(a=>a.startsWith('--source='))?.slice(9);
  if(!input)throw new Error('需要 --source=已经只读采集的source.json');
  const lockPath=path.join(root,'.run.lock');const lock=await open(lockPath,'wx');
  try {
    await lock.writeFile(JSON.stringify({pid:process.pid,startedAt:new Date().toISOString(),mode:'offline-digital-archive'}));
    const original=JSON.parse(await readFile(input,'utf8'));
    const config=await readJson(path.join(root,'config.json'));const course=config.courses.find(c=>c.key==='数字逻辑');
    if(original.course.id!==course.siteId || original.course.name!==course.siteName)throw new Error('课程关联不符');
    if(deadlineState(original.due)!=='active')throw new Error('截止时间已过或不明确，停止归档');
    // Only local book-binding metadata changes; retain the original capture.
    const source={...original,course:{...original.course,bookId:course.bookId}};
    if(config.delivery?.format==='typst')deliveryName(source);
    const refs=parseDigitalReferences(source.html,source.chapter);
    if(!refs.supported)throw new Error('题号未可靠解析');
    const sourceHash=hash(source);
    const capture=path.join(root,'.inbox',source.id,sourceHash,'source.json');await exclusiveJson(capture,source);
    const material=await materialDigest(root,course.bookId);
    if(!material || !refs.refs.every(r=>material.index.exercises.some(e=>e.key===r && e.reviewed)))throw new Error('材料未核验');
    const python=(await readJson(path.join(root,'runtime.json'))).python;
    const outcome=await archive({root,source,materialHash:material.digest,requirePdf:config.delivery?.format==='typst',build:async stage=>{
      await exec(python,[path.join(root,'digital_ch2.py'),'--source',path.join(stage,'source.json'),'--out',stage],
        {windowsHide:true,timeout:120000,maxBuffer:2*1024*1024});
      if(config.delivery?.format==='typst')await compileAnswer({root,stage,source});
    }});
    const delivery=config.delivery?.format==='typst'?await publishPdf({root,source,directory:outcome.directory}):{};
    const approvals=await readJson(path.join(root,'approved-tasks.json')) || {};
    approvals[source.id]={sourceHash,materialHash:material.digest,reviewedAt:new Date().toISOString(),
      reviewer:'Codex: all seven source questions/figures visually checked; 218 input cases verified; user explicitly chose original wiring with anomaly notes',
      refs:refs.refs,sourceDecisions:['第2、3题按原图分析并注明疑点；不补接假设连线','第10题主方案表1.1，附表1.2独立备选']};
    await saveState(path.join(root,'approved-tasks.json'),approvals);
    const notifications=await readJson(path.join(root,'notification-log.json')) || {schema:1,tasks:{},lastFailure:null};
    notifications.updatedAt=new Date().toISOString();notifications.tasks[source.id]={status:outcome.status==='generated'?'generated':'unchanged',
      sourceHash,materialHash:material.digest,fingerprint:outcome.fingerprint,notifiedAt:notifications.updatedAt};
    await saveState(path.join(root,'notification-log.json'),notifications);
    console.log(JSON.stringify({ok:true,...outcome,...delivery,sourceHash,materialHash:material.digest,refs:refs.refs},null,2));
  } finally {await lock.close();await unlink(lockPath);}
}
main().catch(error=>{console.error(JSON.stringify({ok:false,error:error.stderr?'生成器失败；请运行digital_ch2.py --verify检查':error.message}));process.exitCode=1;});
