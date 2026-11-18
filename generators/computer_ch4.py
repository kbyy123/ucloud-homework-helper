"""Source-checked Chinese solutions for the verified Chapter 4 assignment."""
import argparse,hashlib,json,re,shutil
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BANK=ROOT/'题库'/'computer-organization-7'
CAT=ROOT/'题库'/'页面索引'/'computer-organization-7'
BOOK=ROOT.parent/'26fa-computer_architecture'/'计算机组成原理.pdf'
SHA='2ba7dedba8de7135c5a748163c9aed1ac45c455bf2eff28c715f65be868d748c'
REFS=['4/2','4/7','4/8','4/9','4/11','4/12','4/17']
REQUIREMENTS='第四章课后习题：2、7、8、9、11、12、17。'
IMAGES=[1,2,3,139,140,141,146,148,149,153,154,158,159]
COURSE={'key':'计算机组成原理与体系结构','id':'2091774261634650117','name':'计算机组成与体系结构','bookId':'computer-organization-7'}
QUESTIONS={
 '4/2':'假设某计算机指令长度为32位，具有双操作数、单操作数、无操作数三类指令形式，指令系统共有70条指令，请设计满足要求的指令格式。',
 '4/7':'某计算机字长为32位，主存容量为64KB，采用单字长单地址指令，共有40条指令。试采用直接、立即、变址、相对四种寻址方式设计指令格式。',
 '4/8':'某机字长为32位，主存容量为1MB，单字长指令，有50种操作码，采用寄存器寻址、寄存器间接寻址、立即寻址、直接寻址等方式。CPU中有PC，IR，AR，DR和16个通用寄存器。问：\n\n(1)指令格式如何安排？\n\n(2)能否增加其他寻址方式？',
 '4/9':'设某机字长为32位，CPU中有16个32位通用寄存器，设计一种能容纳64种操作的指令系统。如果采用通用寄存器作基址寄存器，则RS型指令的最大存储空间是多少？',
 '4/11':'从以下有关RISC的描述中，正确的是(　)。\n\nA. 采用RISC技术后，计算机的体系结构又恢复到早期的比较简单的情况\n\nB. 为了实现兼容，新设计的RISC，是从原来CISC系统的指令系统中挑选一部分实现的\n\nC. RISC的主要目标是减少指令数\n\nD. RISC设有乘、除法指令和浮点运算指令',
 '4/12':'根据操作数所在位置，指出其寻址方式：\n\n(1)操作数在寄存器中，为_______寻址方式。\n\n(2)操作数地址在寄存器，为_______寻址方式。\n\n(3)操作数在指令中，为_______寻址方式。\n\n(4)操作数地址(主存)在指令中，为_______寻址方式。\n\n(5)操作数的地址为某一寄存器内容与位移量之和，可以是_______、_______或_______寻址方式。',
 '4/17':'设某指令系统字长为16位，地址码为4位。试设计指令格式，使该系统中有11条三地址指令、70条二地址指令和150条单地址指令。并指明该系统中最多还可以有多少条零地址指令。',
}
def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(text):return re.sub(r'\s+','',text)
def keep(file,data):
 file.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,str):data=data.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserve existing/manual file: '+str(file))
 else:file.write_bytes(data)
def filename(ref):return 'questions/'+ref.replace('/','-')+'.md'
def pack(values,widths):
 assert len(values)==len(widths)
 result=0
 for value,width in zip(values,widths):
  assert 0<=value<1<<width
  result=(result<<width)|value
 assert result<1<<sum(widths)
 return result
def unpack(word,widths):
 values=[]
 for width in reversed(widths):values.append(word&((1<<width)-1));word>>=width
 assert word==0
 return list(reversed(values))
def sext(value,width):return value-(1<<width) if value&(1<<(width-1)) else value
def verify():
 checks=[]
 assert (70-1).bit_length()==7 and (40-1).bit_length()==6 and (50-1).bit_length()==6
 # Independent round trips at address boundaries and all allocated opcodes.
 types=Counter()
 for op in range(70):
  kind=2 if op<32 else 1 if op<64 else 0;types[kind]+=1
  for a in [0,1,2047,2048,4095]:
   for b in [0,1,4095]:
    fields=[op,0,a if kind==2 else 0,b if kind else 0]
    assert unpack(pack(fields,[7,1,12,12]),[7,1,12,12])==fields
 assert types=={2:32,1:32,0:6}
 checks.append('4/2：70个有效OP、三类32/32/6分配及12位地址边界编码/解码；字段合计32位')
 for op in range(40):
  for mode in range(4):
   for d in [0,1,32767,32768,65535]:
    fields=[op,mode,0,d];assert unpack(pack(fields,[6,2,8,16]),[6,2,8,16])==fields
 assert (65536-1).bit_length()==16
 for width in [16,19,20]:
  decoded=[sext(v,width) for v in range(1<<width)]
  assert min(decoded)==-(1<<(width-1)) and max(decoded)==(1<<(width-1))-1
  assert len(set(decoded))==1<<width
  assert all((value&((1<<width)-1))==raw for raw,value in enumerate(decoded))
 checks.append('4/7：40操作×4模式、64KB直接寻址上界和字段往返；16/19/20位补码全域范围及一一对应核对')
 for op in range(50):
  for mode in range(4):
   for rd in range(16):
    for a in [0,15,16,524287,524288,1048575]:
     f=[op,mode,rd,a];assert unpack(pack(f,[6,2,4,20]),[6,2,4,20])==f
 old_register=set(range(16));new_relative=set(range(1<<19,1<<20))
 assert old_register.isdisjoint(new_relative) and len(new_relative)==1<<19
 for a in range(1<<20):
  hits=int(a in old_register)+int(a in new_relative)
  assert hits<=1
 assert max(range(1<<20))==1048575
 checks.append('4/8：50操作×4模式×16通用寄存器的字段边界往返；穷举2^20个A值检查旧寄存器子格式与新增PC相对子格式无重叠；1MB地址上界')
 for op in range(64):
  for r in range(16):
   for b in range(16):
    for d in [0,1,131071,131072,262143]:
     f=[op,r,b,d];assert unpack(pack(f,[6,4,4,18]),[6,4,4,18])==f
 for address in [0,1,262143,262144,0x7fffffff,0x80000000,0xffffffff]:
  base=address;displacement=0;assert base+displacement==address and base<1<<32
 assert 2**32==4*1024**3 and 2**32*4==16*1024**3
 checks.append('4/9：全部64操作、16×16寄存器选择和18位位移边界；任意地址取基址=x、D=0的覆盖构造，字节/字编址容量换算')
 counts=Counter();ops=defaultdict(set)
 for word in range(1<<16):
  p4,p8,p12=word>>12,word>>8,word>>4
  matches=[]
  if p4<=0xA:matches.append((3,p4))
  if 0xB0<=p8<=0xF5:matches.append((2,p8))
  if 0xF60<=p12<=0xFF5:matches.append((1,p12))
  if 0xFF60<=word<=0xFFFF:matches.append((0,word))
  assert len(matches)==1,(word,matches)
  arity,op=matches[0];counts[arity]+=1;ops[arity].add(op)
 assert counts=={3:45056,2:17920,1:2400,0:160}
 assert {n:len(v) for n,v in ops.items()}=={3:11,2:70,1:150,0:160}
 assert (1<<16)-11*(1<<12)-70*(1<<8)-150*(1<<4)==160
 checks.append('4/17：穷举65536个机器字，四类每个字恰好匹配一个前缀；操作码数量11/70/150/160与容量上界独立吻合')
 return {'ok':True,'refs':REFS,'checks':checks,'prefixWordCounts':dict(counts),'zeroAddressMaximum':160,
  'reasoningChecks':['4/11：对照教材RISC特征、P=I*C*T和PowerPC浮点格式，排除A/B/C，D按本章一般机器讨论。',
   '4/12：寄存器存操作数与存地址分开；立即/直接分开；PC、基址、变址角色与EA公式一致。'],
  'limits':['格式设计不唯一；4/2三类数量和4/7隐含IX是明确的构造选择。',
   '4/9缺少编址单位和独立地址宽度，给出按32位有效地址的常规设计与字节/字两种容量，不擅自推定实际装机容量。',
   '程序验证可计算编码和边界，概念判断与一般覆盖论证由文字推理复核；不能把样例测试冒充一般证明。']}
def prepare():
 assert digest(BOOK.read_bytes())==SHA
 exercises=[]
 for ref in REFS:
  p=147 if ref=='4/2' else 148
  text=f'## {ref}\n\n书页：{p}；PDF页：{p+11}。\n\n'+QUESTIONS[ref]+'\n'
  keep(BANK/filename(ref),text)
  exercises.append({'key':ref,'file':filename(ref),'sha256':digest(text.encode()),'reviewed':True,'printedPages':[p],'pdfPages':[p+11]})
 images=[]
 for n in IMAGES:
  file=f'images/pdf-{n:04}.png';data=(CAT/file).read_bytes();keep(BANK/file,data);images.append({'file':file,'sha256':digest(data)})
 extra=[{'file':file,'sha256':digest((BANK/file).read_bytes())} for file in ['solutions.typ','solutions.md']]
 index={'schema':1,'bookId':'computer-organization-7','title':'计算机组成原理','edition':'第七版（2024年6月）','authors':['戴志涛','白中英'],
  'isbn':'978-7-03-078281-6','textbook':str(BOOK),'sha256':SHA,'generator':'computer_ch4.py','requiredRefs':REFS,
  'requirementsCanonical':canonical(REQUIREMENTS),'exercises':exercises,'extraFiles':extra,'images':images,
  'scope':'第四章2、7、8、9、11、12、17整组已核验；全书截图索引覆盖10章168题，其他题目继续定位、作答、核验后扩充。'}
 keep(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')
def build(sourcefile,out):
 source=json.loads(Path(sourcefile).read_text(encoding='utf-8'));out=Path(out)
 expected={**COURSE,'id':source['course'].get('id')}
 if source['course']!=expected or expected['id'] not in {'2091774261634650117','2091774263081684995'}:raise ValueError('Wrong course/textbook binding')
 if source.get('resources') or source.get('attachments'):raise ValueError('New attachments need review')
 if canonical(source['requirements'])!=canonical(REQUIREMENTS):raise ValueError('Changed requirements need new solutions')
 if source.get('chapter')!='计组-指令系统':raise ValueError('Chapter association changed')
 index=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
 assert digest(BOOK.read_bytes())==SHA
 for item in index['exercises']+index['extraFiles']+index['images']:
  assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed'
 checked=verify();shutil.copytree(BANK/'images',out/'images')
 intro=f"课程：{source['course']['name']}（归档名：{source['course']['key']}）\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}；截止：{source['due']}（北京时间）。\n"
 parts=['# 题目：'+source['title']+'\n',intro,'## 云邮真实要求\n\n'+source['requirements']+'\n',
  '无附件。教材：戴志涛、白中英主编《计算机组成原理》第七版，科学出版社，2024年6月，ISBN 978-7-03-078281-6；409个PDF页，书页+11=PDF页。\n']
 for ref in REFS:parts.append((BANK/filename(ref)).read_text(encoding='utf-8'))
 parts.append('## 原书题目页与必要定义\n\n本次所选七题无独立题图；整页中其他题目的图只作原页保留，不加入作业范围。\n')
 for n in [158,159,139,140,141,146,148,149,153,154,1,2,3]:
  parts.append(f'PDF第{n}页'+(f'／书页{n-11}' if n>11 else '／封面、书名页或版权页')+f'：\n\n![原书PDF第{n}页](images/pdf-{n:04}.png)\n')
 keep(out/'题目.md','\n'.join(parts));keep(out/'解答.md',(BANK/'solutions.md').read_bytes())
 shutil.copyfile(ROOT/'templates'/'homework.typ',out/'layout.typ')
 date=datetime.fromisoformat(source['assignedAt']).strftime('%Y-%m-%d')
 header='#import "layout.typ": homework\n#show: homework.with(course: '+json.dumps(source['course']['key'],ensure_ascii=False)+', assignment: '+json.dumps(source['title'],ensure_ascii=False)+', assigned: '+json.dumps(date)+', due: '+json.dumps(source['due'])+')\n\n'
 keep(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
 record=['# 核对记录\n',intro,'## 来源和完整性\n',f'教材SHA256：`{SHA}`。本人账号有两门同名课；本作业经学生课程和活动ID关联确认属于课程2091774261634650117，另一门2091774263081684995当前没有该作业，不凭课程标题猜绑定。\n',
  '作业正文明确第四章2、7、8、9、11、12、17，无附件。P147/PDF158的第2题与P148/PDF159的其余六题已逐项核对；第8题两问、第11题四选项、第12题五问完整保留。所选题均无题图，原书整页仍归档。\n',
  '## 独立复核\n',
  '- 第2题没有给出三类数量，32/32/6仅为构造选择；位数和70操作核对，不声称唯一格式。\n',
  '- 第7题按字节编址、隐含IX和16位补码立即数是明确的方案约定；PC参照P137/P142当前指令基准，EA越界不默认回绕。\n',
  '- 第8题四种基本方式齐全；专用寄存器不混入16个通用寄存器。新增方式通过A最高位扩展子格式，不声称2位模式可直接表示5个独立值。\n',
  '- 第9题RS必须同时选择运算和基址寄存器，位移18位；总地址空间与固定基址窗口分开。保留原题未写编址单位和地址宽度的情况，列出32位EA下字节/字编址两种容量，未将其当成已知装机容量。\n',
  '- 第11题D按本章RISC代表机理解，不扩大成所有RISC基本子集的强制要求；性能目标与静态指令种类、动态执行条数分开。第12题按表4.5及相对/基址/变址定义复核。\n',
  '- 第17题从完整机器字容量上界和扩展前缀构造两条路径核验，达到160且无歧义。\n',
  '## 程序检查\n']+['- '+s+'\n' for s in checked['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checked['limits']]+[
  '\n原生Typst和本地模板随作业归档；统一入口编译并检查PDF后归档，再对正式PDF逐页视觉核验。相同指纹重跑跳过，人工修改和旧版保留。只生成本地学习资料，不提交作业。\n']
 keep(out/'核对记录.md','\n'.join(record));keep(out/'verification.json',json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--source');p.add_argument('--out');a=p.parse_args()
 if a.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
 elif a.prepare:verify();prepare();print(json.dumps({'ok':True,'prepared':REFS}))
 elif a.source and a.out:build(a.source,a.out);print(json.dumps({'ok':True}))
 else:p.error('choose --verify, --prepare or --source FILE --out DIR')
