import https from 'node:https';
import { hash } from './workflow.mjs';

/** No cookies, OAuth tokens, or Basic headers are ever sent to file storage. */
export async function downloadAttachment(url, redirects = 0) {
  const u = new URL(url);
  if (u.hostname !== 'fileucloud.bupt.edu.cn' || u.username || u.password || (u.port && u.port !== '443')) {
    throw new Error('附件下载主机未核实，需人工确认');
  }
  if (u.protocol === 'http:') u.protocol = 'https:';
  if (u.protocol !== 'https:') throw new Error('附件只允许 HTTPS');
  return new Promise((resolve,reject) => {
    const req = https.get(u, { timeout:20000 }, res => {
      if ([301,302,303,307,308].includes(res.statusCode)) {
        res.resume();
        if (!res.headers.location || redirects >= 5) return reject(new Error('附件跳转异常'));
        return resolve(downloadAttachment(new URL(res.headers.location,u).href,redirects+1));
      }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error(`附件 HTTP ${res.statusCode}`)); }
      const chunks=[];let size=0;
      res.on('data',c => { size+=c.length; if(size > 100*1024*1024) req.destroy(new Error('附件超过100MB，需人工处理')); else chunks.push(c); });
      res.on('end',()=>resolve(Buffer.concat(chunks)));
      res.on('error',reject);
    });
    req.on('error',reject);
    req.on('timeout',()=>req.destroy(new Error('附件请求超时')));
  });
}

export async function collectAttachments(client, resources, download = downloadAttachment) {
  if (!Array.isArray(resources)) throw new Error('附件列表结构变化，需人工确认');
  const results=[];
  for (const resource of resources) {
    const id = String(resource.resourceId || resource.id || '');
    if (!/^\d{10,25}$/.test(id)) throw new Error('附件缺少可核实的资源 ID');
    const meta = await client.resources([id]);
    const info = Array.isArray(meta) ? meta[0] : meta?.records?.[0];
    if (!info) throw new Error('附件元数据缺失');
    const preview = await client.preview(id);
    const url = typeof preview === 'string' ? preview : preview?.downloadUrl || preview?.url || preview?.previewUrl;
    if (!url) throw new Error('附件没有可核实的直接下载地址，需人工确认');
    const bytes=await download(url);
    const rawName=String(info.name || info.resourceName || resource.name || `resource-${id}`);
    const filename=`${id}-${rawName.replace(/[<>:"/\\|?*\x00-\x1f]/g,'_').slice(0,120)}`;
    results.push({resourceId:id,filename,sha256:hash(bytes),size:bytes.length,bytes});
  }
  return results;
}
