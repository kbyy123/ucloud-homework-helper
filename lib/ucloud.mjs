import https from 'node:https';

const API = 'https://apiucloud.bupt.edu.cn';
const CAS = 'https://auth.bupt.edu.cn/authserver/login';
const SERVICE = 'https://ucloud.bupt.edu.cn/uclass';
const BASIC = 'Basic c3dvcmQ6c3dvcmRfc2VjcmV0';
const READ_PATHS = new Set([
  '/ykt-basics/info', '/ykt-basics/userroledomaindept/listByUserId',
  '/ykt-site/site/student/undone', '/ykt-site/work/detail',
  '/ykt-site/site/detail', '/ykt-site/site/list/student/current', '/ykt-site/site/list/activity',
  '/blade-source/resource/list/byId', '/blade-source/resource/preview-url',
]);

/** Only authentication POSTs and an explicit set of read endpoints are supported. */
export class UcloudClient {
  constructor() { this.cookies = new Map(); this.token = ''; this.identity = ''; this.user = null; }

  async request(url, { form, api = false, redirects = 0 } = {}) {
    const u = new URL(url);
    if (u.protocol !== 'https:') throw new Error('只允许 HTTPS');
    if (![new URL(API).host, new URL(CAS).host, 'ucloud.bupt.edu.cn'].includes(u.host)) {
      throw new Error('拒绝向未知主机发送认证请求');
    }
    if (u.origin === API) api = true;
    if (api && !READ_PATHS.has(u.pathname) && !(form && u.pathname === '/ykt-basics/oauth/token')) {
      throw new Error('接口不在只读白名单内');
    }
    if (form && !((u.origin === new URL(CAS).origin && u.pathname === '/authserver/login') ||
      (u.origin === API && u.pathname === '/ykt-basics/oauth/token'))) {
      throw new Error('禁止业务写入请求');
    }
    if (form && u.origin === API && !['third','refresh_token'].includes(form.grant_type)) {
      throw new Error('只允许 CAS 换票与学生角色令牌认证');
    }
    const headers = { 'User-Agent': 'Mozilla/5.0 (local-homework-assistant)', Accept: 'application/json,text/html' };
    const cookies = this.cookies.get(u.host);
    if (cookies?.size) headers.Cookie = [...cookies].map(([k,v]) => `${k}=${v}`).join('; ');
    if (api) {
      headers.Authorization = BASIC;
      headers['Tenant-Id'] = '000000';
      if (this.token) headers['Blade-Auth'] = this.token;
      if (this.identity) headers.identity = this.identity;
    }
    const body = form ? new URLSearchParams(form).toString() : undefined;
    if (body !== undefined) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
      headers['Content-Length'] = Buffer.byteLength(body);
    }
    const response = await new Promise((resolve, reject) => {
      const req = https.request(u, { method: form ? 'POST' : 'GET', headers, timeout: 20000 }, res => {
        const chunks = [];
        res.on('data', c => chunks.push(c));
        res.on('end', () => resolve({ path: u.pathname, status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString('utf8') }));
        res.on('error', reject);
      });
      req.on('error', reject);
      req.on('timeout', () => req.destroy(new Error('请求超时')));
      req.end(body);
    });
    for (const cookie of response.headers['set-cookie'] || []) {
      const pair = cookie.split(';')[0]; const index = pair.indexOf('=');
      if (index < 1) continue;
      if (!this.cookies.has(u.host)) this.cookies.set(u.host, new Map());
      this.cookies.get(u.host).set(pair.slice(0,index), pair.slice(index+1));
    }
    if (response.status >= 300 && response.status < 400) {
      if (!response.headers.location) throw new Error('跳转缺少 Location');
      const next = new URL(response.headers.location, u);
      if (next.searchParams.has('ticket')) {
        if (next.hostname !== 'ucloud.bupt.edu.cn') throw new Error('CAS ticket 目标主机不符');
        return { ...response, ticket: next.searchParams.get('ticket') };
      }
      if (form) throw new Error('认证提交未返回 ticket，停止登录');
      if (redirects >= 5) throw new Error('跳转次数过多');
      if (next.protocol === 'http:') next.protocol = 'https:';
      return this.request(next, { api, redirects: redirects + 1 });
    }
    return response;
  }

  decode(response) {
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`云邮 ${response.path} HTTP ${response.status}；停止本轮，未重试登录`);
    }
    let result;
    try { result = JSON.parse(response.body); } catch { throw new Error('云邮返回非 JSON，停止本轮'); }
    if (result.success === false || (result.code !== undefined && ![0,200,'200'].includes(result.code))) {
      throw new Error(`云邮业务请求失败：${String(result.msg || result.message || result.code).slice(0,150)}`);
    }
    return result;
  }

  async read(path, params = {}) {
    if (!READ_PATHS.has(path)) throw new Error('接口不在只读白名单内');
    const url = new URL(path, API);
    url.search = new URLSearchParams(params).toString();
    const result = this.decode(await this.request(url, { api: true }));
    if (!Object.hasOwn(result, 'data')) throw new Error('云邮响应缺少 data');
    return result.data;
  }

  async login({ user = process.env.UC_USER, pass = process.env.UC_PASS } = {}) {
    if (!user || !pass) throw new Error('需要临时环境变量 UC_USER 和 UC_PASS；不会读取凭据文件');
    const casUrl = `${CAS}?service=${encodeURIComponent(SERVICE)}`;
    const page = await this.request(casUrl);
    let ticket = page.ticket;
    if (!ticket) {
      const execution = page.body.match(/name="execution"[^>]*value="([^"]+)"/)?.[1];
      if (!execution) throw new Error('认证页缺少 execution，停止登录');
      const response = await this.request(casUrl, { form: { username: user, password: pass,
        type: 'username_password', execution, _eventId: 'submit' } });
      ticket = response.ticket;
      if (!ticket) throw new Error('统一认证未通过或要求验证码，停止登录，不重试');
    }
    const token = this.decode(await this.request(`${API}/ykt-basics/oauth/token`, {
      api: true, form: { ticket, grant_type: 'third' },
    }));
    if (!token.access_token || !token.refresh_token) throw new Error('认证未返回令牌，停止登录');
    this.token = token.access_token;
    let info = await this.read('/ykt-basics/info', { id: token.user_id });
    if (info?.data) info = info.data;
    if (!info?.id) throw new Error('用户信息缺少业务 ID');
    this.user = { id: String(info.id), account: String(info.account || user), name: info.realName || token.real_name || '' };
    const roles = await this.read('/ykt-basics/userroledomaindept/listByUserId', { userId: token.user_id });
    const student = Array.isArray(roles) && roles.find(r => r.roleAliase === 'JS005');
    if (!student) throw new Error('未找到学生角色，停止');
    const roleToken = this.decode(await this.request(`${API}/ykt-basics/oauth/token`, {
      api: true, form: { grant_type: 'refresh_token', refresh_token: token.refresh_token, identity: student.id },
    }));
    if (!roleToken.access_token) throw new Error('学生角色换令牌失败，停止');
    this.token = roleToken.access_token;
    this.identity = `${student.roleAliase}:${student.dept || ''}`;
    return this.user;
  }

  async undone() {
    if (!this.user) throw new Error('尚未登录');
    const data = await this.read('/ykt-site/site/student/undone', { userId: this.user.id });
    if (!Array.isArray(data?.undoneList)) throw new Error('未完成列表结构变化，停止本轮');
    return data.undoneList.map(it => ({
      id: String(it.activityId || it.undoneId || it.id || ''),
      title: it.activityName || it.undoneName || it.name || '',
      due: it.endTime || it.endtime || it.deadline || '',
      course: it.siteName || '', typeCode: it.type,
    }));
  }

  async assignment(id) { return this.read('/ykt-site/work/detail', { assignmentId: id }); }
  async course(id) { return this.read('/ykt-site/site/detail', { id }); }
  async resources(ids) {
    if (!ids.length) return [];
    if (!ids.every(id => /^\d{10,25}$/.test(String(id)))) throw new Error('附件资源 ID 无效');
    return this.read('/blade-source/resource/list/byId', { resourceIds: ids.join(',') });
  }
  async preview(id) {
    if (!/^\d{10,25}$/.test(String(id))) throw new Error('附件资源 ID 无效');
    return this.read('/blade-source/resource/preview-url', { resourceId: id });
  }
  close() { this.token = ''; this.identity = ''; this.cookies.clear(); this.user = null; }
}
