"""Source-verified sixth-edition group-theory pilot: 9.1/16,32,34."""
import argparse,hashlib,json,re,shutil
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BANK=ROOT/'题库'/'kolman-6'/'9.1';CAT=ROOT/'题库'/'页面索引'/'kolman-6'
BOOK=next((ROOT.parent/'26fa-离散数学（下）').glob('Discrete mathematical structures sixth edition*.pdf'))
SHA='9e95e1abd601348e39696917e4cf1fa9252b51ffc0aa2d23bdb469b9ea48fe48'
REFS=['9.1/16','9.1/32','9.1/34']
CAPTURE=ROOT/'.inbox'/'2118625671952728065'/'fce797fa3272937d54960cfb13909e88421359aebabc90e54b9389a7984ac609'
QUESTIONS={
'16':r'''In Exercises 9 through 19, determine whether the binary operation $*$ is commutative and whether it is associative on the set.

16. On $\mathbb R$, where $a*b$ is $ab+2b$.''',
'32':r'''Let $*$ be a binary operation on a set $A$, and suppose that $*$ satisfies the idempotent, commutative, and associative properties, as discussed in Example 16. Define a relation $\le$ on $A$ by $a\le b$ if and only if $b=a*b$. Show that $(A,\le)$ is a poset and, for all $a$ and $b$, $\operatorname{LUB}(a,b)=a*b$.''',
'34':r'''Define a binary operation on a set $S$ by $a*b=b$. Is $*$ associative? commutative? idempotent?'''
}
def digest(data):return hashlib.sha256(data).hexdigest()
def keep(file,data):
 file.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,str):data=data.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserve existing/manual file: '+str(file))
 else:file.write_bytes(data)
def verify():
 op=lambda a,b:a*b+2*b
 values=[Q(i,2) for i in range(-6,7)]
 for a,b in product(values,repeat=2):assert op(a,b)-op(b,a)==2*(b-a)
 for a,b,c in product(values,repeat=3):
  assert op(op(a,b),c)==a*b*c+2*b*c+2*c
  assert op(a,op(b,c))==a*b*c+2*a*c+2*b*c+4*c
 assert op(0,1)==2 and op(1,0)==0
 assert op(op(1,1),1)==5 and op(1,op(1,1))==9
 counts={};tables_checked=0
 for n in [1,2,3]:
  good=0;v=range(n)
  for table in product(v,repeat=n*n):
   tables_checked+=1
   f=lambda a,b:table[a*n+b]
   if any(f(a,a)!=a for a in v):continue
   if any(f(a,b)!=f(b,a) for a,b in product(v,repeat=2)):continue
   if any(f(f(a,b),c)!=f(a,f(b,c)) for a,b,c in product(v,repeat=3)):continue
   good+=1
   # Independent relation/bound enumeration, not merely symbolic substitution.
   r={(a,b) for a,b in product(v,repeat=2) if b==f(a,b)}
   assert all((a,a) in r for a in v)
   assert all(a==b or (b,a) not in r for a,b in r)
   assert all((a,c) in r for a,b in r for x,c in r if b==x)
   for a,b in product(v,repeat=2):
    upper={u for u in v if (a,u) in r and (b,u) in r}
    least={u for u in upper if all((u,w) in r for w in upper)}
    assert least=={f(a,b)}
  counts[n]=good
 assert counts=={1:1,2:2,3:9}
 for n in range(6):
  v=range(n);f=lambda a,b:b
  assert all(f(f(a,b),c)==f(a,f(b,c)) for a,b,c in product(v,repeat=3))
  assert all(f(a,a)==a for a in v)
  assert all(f(a,b)==f(b,a) for a,b in product(v,repeat=2))==(n<=1)
 return {'ok':True,'refs':REFS,'checks':[
  '9.1/16：13个精确有理数的169组交换差与2197组三元组展开核对；(0,1)及(1,1,1)反例准确',
  f'9.1/32：穷举1、2、3元素集全部{tables_checked}个二元运算表，筛出1、2、9个满足三性质者；独立枚举所得偏序和全部最小上界',
  '9.1/34：大小0—5的集合全部有序对/三元组核对；结合、幂等恒成立，交换恰好在大小≤1时成立'],
  'semilatticeCounts':counts,'limits':[
   '第32题任意集合的一般结论由完整代数证明给出；有限表枚举不是无限情形的证明。',
   '第32题定义是b=a*b，对应LUB；Example16是a=a*b，对应GLB，方向不能互换。',
   '第34题通常至少两元素时不交换；空集及单元素集单列，不用不存在的不同元素构造反例。']}
def prepare():
 assert digest(BOOK.read_bytes())==SHA
 images=[]
 for n in [1,5,24,372,373,374]:
  name=f'images/pdf-{n:04}.png';data=(CAT/name).read_bytes();keep(BANK/name,data);images.append({'file':name,'sha256':digest(data)})
 inline=[]
 for n in range(1,5):
  name=f'images/inline-{n:02}.png';data=(CAPTURE/name).read_bytes();keep(BANK/name,data)
  value=digest(data);inline.append(value);images.append({'file':name,'sha256':value})
 exercises=[]
 for number,text in QUESTIONS.items():
  printed=349 if number=='34' else 348;pdf=printed+25
  text=f'## 9.1 Exercise {number}\n\n来源：Kolman第六版，书页{printed} / PDF第{pdf}页。\n\n'+text+'\n'
  keep(BANK/(number+'.md'),text)
  exercises.append({'key':'9.1/'+number,'file':number+'.md','sha256':digest(text.encode('utf-8')),'reviewed':True,'printedPage':printed,'pdfPage':pdf,
                    'dependencies':['images/pdf-0372.png'] if number=='32' else []})
 index={'schema':1,'bookId':'kolman-6','section':'9.1','edition':'Sixth Edition','isbn':'978-7-04-031045-0','textbook':str(BOOK),'sha256':SHA,
  'generator':'kolman91.py','requiredRefs':REFS,'inlineImageHashes':inline,'exercises':exercises,'images':images,
  'extraFiles':[{'file':name,'sha256':digest((BANK/name).read_bytes())} for name in ['solutions.md','solutions.typ']],
  'scope':'第六次完整三题；采用Sixth Edition分支16、32、34，不合并Fourth Edition分支16、28。所有一般证明独立复核。'}
 keep(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')
def build(sourcefile,out):
 source=json.loads(Path(sourcefile).read_text(encoding='utf-8'));out=Path(out)
 assert source['course']=={'key':'离散数学','id':'2091774263035547651','name':'离散数学（下）','bookId':'kolman-6'},'Course/textbook mismatch'
 assert source['chapter']=='Group Theory' and not source.get('attachments') and not source.get('resources'),'Changed source or attachments'
 original=json.loads((CAPTURE/'source.json').read_text(encoding='utf-8'))
 assert source['html']==original['html'] and source['requirements']==original['requirements'],'New requirements require independent review'
 index=json.loads((BANK/'index.json').read_text(encoding='utf-8'));assert digest(BOOK.read_bytes())==SHA
 for item in index['exercises']+index['extraFiles']+index['images']:assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed'
 checks=verify();shutil.copytree(BANK/'images',out/'images')
 intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}；截止：{source['due']}（北京时间）。\n"
 parts=['# 题目：'+source['title']+'\n',intro,'## 原始要求与版本选择\n\n'+source['requirements']+'\n',
  '源正文同时列出第六版和第四版替代题号。本次使用用户新提供的Kolman/Busby/Ross第六版，选择9.1/16、32、34三题，不再额外做第四版的第28题。云邮内嵌公式不能由纯文本替代，以下原图完整保留。\n',
  '34. Define a binary operation ![原式运算符](images/inline-01.png) on a set ![原式集合S](images/inline-02.png) by ![原式a*b=b](images/inline-03.png). Is ![原式运算符](images/inline-04.png) associative? commutative? idempotent?\n',
  '教材：Discrete Mathematical Structures, Sixth Edition；高教社2010年11月英文影印版，ISBN978-7-04-031045-0。SHA256：`'+SHA+'`。书页+25=PDF页。\n']
 for number in QUESTIONS:parts.append((BANK/(number+'.md')).read_text(encoding='utf-8'))
 parts.append('## 第32题依赖与原书页面\n\nExample16位于P347/PDF372，其定义是a=a*b、结论GLB。本题改成b=a*b、结论LUB，解答重新证明，未照抄相反序的结论。\n')
 for n in [372,373,374,1,5,24]:parts.append(f'![原书PDF{n}页](images/pdf-{n:04}.png)\n')
 keep(out/'题目.md','\n'.join(parts));keep(out/'解答.md',(BANK/'solutions.md').read_bytes());shutil.copyfile(ROOT/'templates/homework.typ',out/'layout.typ')
 header='#import "layout.typ": homework\n#show: homework.with(course: "离散数学", assignment: "第六次作业：代数结构及二元运算", assigned: '+json.dumps(source['assignedAt'])+', due: '+json.dumps(source['due'])+')\n\n'
 keep(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
 records=['# 核对记录\n',intro,
 '## 版本及来源核对\n','本人课程活动关联由只读入口核实。采用正文Sixth Edition分支；第四版是替代选项，不混合题号。用户明确恢复群论处理，新教材封面、版权、目录及书页逐页核对；旧Rosen的关系题保留原绑定。\n',
 f'教材SHA256：`{SHA}`。第16、32题在书页348/PDF373；34题在349/PDF374；32引用Example16在347/PDF372。原题英文、共享题干及全部三个判断要求齐全；四张源公式图片均保留。\n',
 '## 独立推理\n',
 '- 第16题a*b=ab+2b而非ab+2a；交换反例0*1=2、1*0=0；结合反例(1*1)*1=5、1*(1*1)=9，并对一般实数符号展开核对。\n',
 '- 第32题不循环假定偏序或LUB存在：先证三条关系性质，再证u=a*b为上界且小于等于任意上界。反对称用了交换性，传递用了结合性。例16的序方向相反，不能套其GLB证明的结论。空集情形全称命题空真。\n',
 '- 第34题右投影a*b=b，结合两边均c，幂等a*a=a；交换恰当且仅当底集至多一个元素，通常两元素以上反例成立。\n',
 '## 程序交叉核验\n']+['- '+s+'\n' for s in checks['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checks['limits']]+[
 '\n原生Typst、模板、原书截图及四张源公式图片随作业归档；统一编译PDF并逐页视觉核对。日期取真实assignmentBeginTime=2026-11-06 16:44，正式PDF集中在output。相同指纹重跑跳过，人工修改及旧版保留，不自动提交。\n']
 keep(out/'核对记录.md','\n'.join(records));keep(out/'verification.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--source');p.add_argument('--out');a=p.parse_args()
 if a.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
 elif a.prepare:verify();prepare();print(json.dumps({'ok':True,'prepared':REFS}))
 elif a.source and a.out:build(a.source,a.out);print(json.dumps({'ok':True}))
 else:p.error('Choose --verify, --prepare, or --source FILE --out DIR')
