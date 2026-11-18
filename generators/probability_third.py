"""Source-checked third probability assignment, native Typst and independent checks.

Earlier banks and their fingerprints stay untouched. Finite computations are
cross-checks; infinite-series and general-parameter arguments are written out.
"""
import argparse,hashlib,json,math,re,shutil
from collections import defaultdict,Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent
BANK=ROOT/'题库'/'probability-bupt-2021'/'third'
CAT=ROOT/'题库'/'页面索引'/'probability-bupt-2021'
BOOK=ROOT.parent/'26fa-概率论与随机过程'/'概率论与随机过程.pdf'
SHA='80662453203acbf11f5c6b4368c649e2437ba07837dd90465d52f4cceec06200'
REFS=['3/21','3/28','3/29','4/2','4/5','4/6(2)','4/7(2)','1/40','1/42','1/47']
REQ='p107-108\n21 28 29\np143-144\n2 5 6(2) 7(2)\np36-37\n40 42 47'
PAGES={'3/21':[107],'3/28':[108],'3/29':[108],'4/2':[143],'4/5':[143],
       '4/6(2)':[143],'4/7(2)':[143],'1/40':[36],'1/42':[36],'1/47':[37]}
MATRIX=[[Q(1,12),Q(1,6),Q(1,24)],[Q(1,4),Q(1,4),Q(1,40)],
        [Q(1,8),Q(1,20),Q(0)],[Q(1,120),Q(0),Q(0)]]
QUESTIONS={
'3/21':r'''设二维随机变量 $(X,Y)$ 的分布律为

| Y \\ X | 0 | 1 | 2 |
|---|---|---|---|
| 0 | $1/12$ | $1/6$ | $1/24$ |
| 1 | $1/4$ | $1/4$ | $1/40$ |
| 2 | $1/8$ | $1/20$ | $0$ |
| 3 | $1/120$ | $0$ | $0$ |

求：（1）$P\{X=Y\}$，$P\{X+Y\le1\}$；（2）$W_1=X+Y,W_2=XY$ 的分布律。''',
'3/28':r'''设二维随机变量 $(X,Y)$ 的概率密度为

$$f(x,y)=\begin{cases}be^{-(x+y)},&0<x<1,y>0,\\0,&\text{其他}.\end{cases}$$

（1）试确定常数 $b$；

（2）求边缘概率密度 $f_X(x),f_Y(y)$；

（3）求 $U=\max(X,Y)$ 的分布函数。''',
'3/29':r'''对某种电子装置的输出测量了5次，得到结果为 $X_1,X_2,X_3,X_4,X_5$，设它们是相互独立的随机变量且都服从参数 $\sigma=2$ 的瑞利分布，即

$$f(x)=\begin{cases}\dfrac{x}{4}e^{-x^2/8},&x>0,\\0,&\text{其他}.\end{cases}$$

（1）求 $Z=\max\{X_1,X_2,X_3,X_4,X_5\}$ 的分布函数；

（2）求 $P\{Z>4\}$。''',
'4/2':r'将4个球任意地放入4个盒子中，设 $X$ 表示空盒子的个数，求 $E(X)$。',
'4/5':r'''设风速 $V$ 在 $(0,a)$ 上服从均匀分布，即具有概率密度

$$f(v)=\begin{cases}\dfrac1a,&0<v<a,\\0,&\text{其他},\end{cases}$$

又设飞机翼受到的正压力 $W$ 是 $V$ 的函数：$W=kV^2$（$k>0$，常数），求 $W$ 的数学期望。''',
'4/6(2)':r'（2）设 $X\sim\pi(\lambda)$，求 $E[1/(X+1)]$。',
'4/7(2)':r'''（2）设随机变量 $X_1,X_2,\ldots,X_n$ 相互独立，且都服从 $(0,1)$ 上的均匀分布，求：（a）$U=\max\{X_1,X_2,\ldots,X_n\}$ 的数学期望；（b）$V=\min\{X_1,X_2,\ldots,X_n\}$ 的数学期望。''',
'1/40':r'今有两名射手轮流对同一目标射击，甲命中的概率为 $p_1$，乙命中的概率为 $p_2$，甲先射击，谁先命中谁得胜，分别求甲、乙两人得胜的概率。',
'1/42':r'设有 $n$ 门高射炮同时独立地向一敌机各发射一发炮弹，每门炮的命中率均为0.6，若要求至少有一门炮击中敌机的概率不低于0.99，则 $n$ 至少要多少？',
'1/47':r'设在伯努利试验中，事件 $A$ 出现的概率为 $p$（$0<p<1$）。将伯努利试验独立重复地一直做下去称为可列伯努利试验。证明：在可列伯努利试验中，“事件 $A$ 终将出现”的概率为1。'
}
def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(text):return re.sub(r'\s+','',text)
def keep(file,data):
 file.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,str):data=data.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserve existing/manual file: '+str(file))
 else:file.write_bytes(data)
def qfile(ref):return 'questions/'+ref.replace('/','-')+'.md'
def simpson(f,a,b,n=2000):
 assert n%2==0
 if a==b:return 0.
 h=(b-a)/n
 return h/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+h*i) for i in range(1,n)))
def verify():
 checks=[];atoms={(x,y):MATRIX[y][x] for y in range(4) for x in range(3)}
 assert all(p>=0 for p in atoms.values()) and sum(atoms.values())==1
 w1=defaultdict(Q);w2=defaultdict(Q)
 for (x,y),p in atoms.items():w1[x+y]+=p;w2[x*y]+=p
 w1={k:v for k,v in w1.items() if v};w2={k:v for k,v in w2.items() if v}
 assert w1=={0:Q(1,12),1:Q(5,12),2:Q(5,12),3:Q(1,12)}
 assert w2=={0:Q(27,40),1:Q(1,4),2:Q(3,40)}
 eq=sum(p for (x,y),p in atoms.items() if x==y);small=sum(p for (x,y),p in atoms.items() if x+y<=1)
 assert eq==Q(1,3) and small==Q(1,2) and sum(w1.values())==sum(w2.values())==1
 # Integer-weight enumeration is a separate representation of all 120 outcomes.
 outcomes=[(x,y) for (x,y),p in atoms.items() for _ in range(int(120*p))]
 assert Counter(x+y for x,y in outcomes)=={0:10,1:50,2:50,3:10}
 assert Counter(x*y for x,y in outcomes)=={0:81,1:30,2:9}
 checks.append('3/21：12个格点Fraction求和、事件筛选与120个等权原子独立枚举；两个变换分布均归一化')
 b=1/(-math.expm1(-1));fx=lambda x:b*math.exp(-x)
 assert abs(simpson(fx,0,1)-1)<1e-12
 FU=lambda u:0 if u<=0 else b*(-math.expm1(-u))**2 if u<1 else -math.expm1(-u)
 us=[-1,0,1e-6,.1,.5,.999,1,1.001,2,5,20]
 for u in us:
  rectangle=0 if u<=0 else b*simpson(lambda x:math.exp(-x),0,min(1,u))*simpson(lambda y:math.exp(-y),0,u,n=4000)
  assert abs(rectangle-FU(u))<1e-10
 assert abs(b*(1-math.exp(-1))**2-(1-math.exp(-1)))<1e-15
 assert all(0<=FU(u)<=1 for u in us) and all(FU(a)<=FU(c) for a,c in zip(us,us[1:]))
 checks.append('3/28：归一化及11个含0/1两侧端点的u值由矩形积分交叉核对；CDF单调、拼接连续且趋于1')
 F=lambda z:0 if z<=0 else -math.expm1(-z*z/8)
 ray=lambda z:z/4*math.exp(-z*z/8)
 for z in [.01,.5,1,2,4,8,12]:assert abs(simpson(ray,0,z,n=4000)-F(z))<1e-12
 exceed=1-F(4)**5;tail=math.exp(-2)
 by_count=sum(math.comb(5,k)*tail**k*(1-tail)**(5-k) for k in range(1,6))
 assert abs(exceed-by_count)<1e-15
 assert abs(simpson(lambda z:5*F(z)**4*ray(z),0,16,n=8000)-1)<1e-12
 checks.append('3/29：瑞利密度积分核对CDF；五次最大值密度归一化；尾概率与至少一次超4的二项式展开交叉核对')
 occupancy=Counter(4-len(set(assignment)) for assignment in product(range(4),repeat=4))
 assert occupancy=={0:24,1:144,2:84,3:4}
 assert sum(Q(k*v,256) for k,v in occupancy.items())==4*Q(3,4)**4==Q(81,64)
 checks.append('4/2：256种独立等概率投球结果全部枚举，与空盒指示变量期望81/64交叉核对；模型约定明示')
 for a,k in product([Q(1,2),Q(1),Q(2),Q(5)],[Q(1,3),Q(1),Q(4)]):
  # Simpson exact for the quadratic k*v^2/a, using exact rational values.
  integral=a/Q(6)*(0+4*k*(a/2)**2/a+k*a*a/a)
  assert integral==k*a*a/3
 checks.append('4/5：12组正参数用有理数精确二次积分检查ka²/3；a>0、k>0与有界性明示')
 for lam in [1e-8,.1,1,3,10,30,100]:
  p=math.exp(-lam);mass=p;expect=p
  for j in range(1,1000):p*=lam/j;mass+=p;expect+=p/(j+1)
  value=-math.expm1(-lam)/lam
  assert abs(mass-1)<1e-13 and abs(expect-value)<1e-13
 assert abs(-math.expm1(-1e-10)/1e-10-1)<1e-9
 checks.append('4/6(2)：7组Poisson参数由概率递推直接累加1000项核对，含小参数稳定式与λ→0极限；λ=0退化值为1')
 for n in range(1,21):
  norm_min=sum(Q(n*math.comb(n-1,j)*(-1)**j,j+1) for j in range(n))
  mean_min=sum(Q(n*math.comb(n-1,j)*(-1)**j,j+2) for j in range(n))
  assert norm_min==1 and mean_min==Q(1,n+1)
  assert Q(n,n+1)+mean_min==1
  # Different representation: survival-function polynomial integration.
  tail_mean=sum(Q(math.comb(n,j)*(-1)**j,j+1) for j in range(n+1))
  assert tail_mean==mean_min
 checks.append('4/7(2)：n=1至20的最小值密度与生存函数多项式精确积分，最大/最小期望相加为1，n=1边界通过')
 shooting_cases=0
 for p1,p2 in product([Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)],repeat=2):
  q=(1-p1)*(1-p2);D=1-q;a=bmass=Q(0);survival=Q(1)
  for _ in range(32):
   a+=survival*p1;survival*=1-p1;bmass+=survival*p2;survival*=1-p2
  assert a+bmass+survival==1 and survival==q**32
  if D:
   pa=p1/D;pb=(1-p1)*p2/D
   assert pa+pb==1 and pa==p1+q*pa and pb==(1-p1)*p2+q*pb
   assert a==pa*(1-q**32) and bmass==pb*(1-q**32)
  else:assert p1==p2==a==bmass==0 and survival==1
  shooting_cases+=1
 checks.append(f'1/40：{shooting_cases}组含0/1边界的射击概率，32轮吸收递推与几何级数部分和精确核对；两人均为0时不除以0')
 n=next(n for n in range(1,30) if 1-Q(2,5)**n>=Q(99,100))
 assert n==6 and 1-Q(2,5)**5==Q(6186,6250) and 1-Q(2,5)**6==Q(15561,15625)
 checks.append('1/42：Fraction逐个整数寻找最小n=6；n=5的0.98976不达标，n=6的0.995904达标')
 for p,N in product([Q(1,10),Q(1,4),Q(1,2),Q(3,4),Q(9,10)],range(1,31)):
  assert sum(p*(1-p)**(j-1) for j in range(1,N+1))==1-(1-p)**N
 checks.append('1/47：150组有限首次成功分解核对；可列互斥可加性及无限几何级数的一般证明另列，区分概率1与有限次保证')
 return {'ok':True,'refs':REFS,'checks':checks,'joint21':[[str(v) for v in row] for row in MATRIX],
  'sumDistribution':{str(k):str(v) for k,v in sorted(w1.items())},'productDistribution':{str(k):str(v) for k,v in sorted(w2.items())},
  'answers':{'3/21(1)':['1/3','1/2'],'3/28(1)':'1/(1-exp(-1))','3/29(2)':exceed,'4/2':'81/64','4/5':'ka^2/3',
             '4/6(2)':'(1-exp(-lambda))/lambda (lambda>0); 1 (lambda=0)','4/7(2)':['n/(n+1)','1/(n+1)'],'1/42':6,'1/47':1},
  'limits':['有限计算不替代一般证明；Poisson级数、任意正整数n的次序统计量和可列伯努利试验均给出完整推导。',
            '4/2明示每球独立等概率选盒的通常模型；1/40明示独立射击/失手后命中率恒定的通常模型；仅边缘概率不足确定有依赖模型。',
            '仅回答4/6(2)、4/7(2)两指定小问，4/7(2)内a、b均保留；两道最大值CDF含全实轴分段与0/1边界。']}
def prepare():
 assert digest(BOOK.read_bytes())==SHA,'Textbook version changed'
 exercises=[]
 for ref in REFS:
  printed=PAGES[ref];pdf=[p+11 for p in printed]
  text=f'## {ref}\n\n书页：{",".join(map(str,printed))}；PDF页：{",".join(map(str,pdf))}。\n\n'+QUESTIONS[ref]+'\n'
  keep(BANK/qfile(ref),text);exercises.append({'key':ref,'file':qfile(ref),'sha256':digest(text.encode('utf-8')),'reviewed':True,'printedPages':printed,'pdfPages':pdf})
 images=[]
 for n in [1,3,47,48,118,119,154,155]:
  file=f'images/pdf-{n:04}.png';data=(CAT/file).read_bytes();keep(BANK/file,data);images.append({'file':file,'sha256':digest(data)})
 extra=[{'file':name,'sha256':digest((BANK/name).read_bytes())} for name in ['solutions.typ','solutions.md']]
 keep(BANK/'index.json',json.dumps({'schema':1,'bookId':'probability-bupt-2021','assignment':'third','edition':'2021年1月第1版',
  'isbn':'978-7-5635-6266-4','textbook':str(BOOK),'sha256':SHA,'generator':'probability_third.py','requiredRefs':REFS,
  'requirementsCanonical':canonical(REQ),'exercises':exercises,'extraFiles':extra,'images':images,
  'scope':'第三次完整10项：3/21、28、29，4/2、5、6(2)、7(2)，1/40、42、47；指定小问和全部子问保留。'},ensure_ascii=False,indent=2)+'\n')
def build(sourcefile,out):
 source=json.loads(Path(sourcefile).read_text(encoding='utf-8'));out=Path(out)
 if source['course']!={'key':'概率论与随机过程','id':'2091774263564029955','name':'概率论与随机过程','bookId':'probability-bupt-2021'}:raise ValueError('Wrong course/textbook binding')
 if source.get('attachments') or source.get('resources'):raise ValueError('Attachments require review')
 if canonical(source['requirements'])!=canonical(REQ):raise ValueError('Changed requirements require independent review')
 index=json.loads((BANK/'index.json').read_text(encoding='utf-8'));assert digest(BOOK.read_bytes())==SHA
 for item in index['exercises']+index['extraFiles']+index['images']:assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed'
 checked=verify();shutil.copytree(BANK/'images',out/'images')
 intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}；截止：{source['due']}（北京时间）。\n"
 parts=['# 题目：'+source['title']+'\n',intro,'## 云邮真实正文\n\n'+source['requirements']+'\n',
  '无附件。北邮出版社2021年1月第1版，ISBN 978-7-5635-6266-4；教材SHA256：`'+SHA+'`；书页+11=PDF页。\n']
 for ref in REFS:parts.append((BANK/qfile(ref)).read_text(encoding='utf-8'))
 parts.append('## 原书整页及版本\n\n4/6、4/7仅指定(2)，不额外求解(1)；4/7(2)中的a、b两问均保留。PDF155为页边界保守上下文，4/7(2)实际完整位于P143/PDF154。本次无另设题图；3/21原分布表已逐格核对。\n')
 for n in [118,119,154,155,47,48,1,3]:parts.append(f'PDF第{n}页'+(f'／书页{n-11}' if n>11 else '／版本页')+f'：\n\n![原书整页](images/pdf-{n:04}.png)\n')
 keep(out/'题目.md','\n'.join(parts));keep(out/'解答.md',(BANK/'solutions.md').read_bytes());shutil.copyfile(ROOT/'templates/homework.typ',out/'layout.typ')
 date=datetime.fromisoformat(source['assignedAt']).strftime('%Y-%m-%d')
 header='#import "layout.typ": homework\n#show: homework.with(course: "概率论与随机过程", assignment: "第三次作业", assigned: '+json.dumps(date)+', due: '+json.dumps(source['due'])+')\n\n'
 keep(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
 records=['# 核对记录\n',intro,'## 来源与完整性\n',
  '本人课程与活动ID关联由本轮只读入口核实；按真实正文p107-108、p143-144、p36-37定位，未按标题猜章。全部10项和指定小问一致，无附件。\n',
  '书页107/PDF118的3/21为4行Y（0—3）×3列X（0—2），12个值逐个视觉核对；尤其1/24、1/40、1/120及三个零不能漏。书页108两题最大值CDF全部小问保留。\n',
  '第4章2、5、6(2)、7(2)都在书页143/PDF154；第6题的第(1)小问表格、第7题第(1)小问不是布置范围，原页作为上下文保留，不误作所求。4/7(2)含a、b两问。第1章40、42在P36/PDF47，47在P37/PDF48。\n',
  '## 独立推理复核\n',
  '- 3/21按互斥格点累加，不假设X、Y独立；和取0、1、2、3，积取0、1、2，零质量值不列为支持。对角和1/3，左下三格和1/2。\n',
  '- 3/28先归一化，矩形支持下证明联合密度等于两边缘乘积，再用于最大值；u≤0、0<u<1、u≥1三段含全实轴且u=1连续。\n',
  '- 3/29瑞利参数σ=2对应x/4·exp(−x²/8)，没有把2误作方差或指数率；5次独立才取五次幂，Z=4无点质量。\n',
  '- 4/2空盒指示量之间不独立，但期望线性不要求其独立；每球独立等概率选盒约定明示。4/5保留a>0、k>0，直接计算函数期望而不是k[E(V)]²。\n',
  '- 4/6(2)原π(λ)是Poisson分布；级数换指标前先要求λ>0，λ=0退化情形单列，避免除0。4/7(2)有界次序统计量期望存在，n为正整数，n=1边界一致。\n',
  '- 1/40原文未逐字写独立性，按通常独立射击/失手后命中率恒定模型给完整答案并注明；若只有边缘命中率不足确定依赖模型。p1=p2=0时永不命中，两人获胜概率均0，不能套分式。\n',
  '- 1/42取不低于0.99，严格检查相邻整数5、6；1/47用互斥首次成功事件和可列可加性证明，不将概率1误作某个固定有限次数的确定保证。\n',
  '## 程序核验\n']+['- '+s+'\n' for s in checked['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checked['limits']]+[
  '\n原生Typst、模板、原书截图、原题及完整中文解答随作业归档；由compileAnswer、archive、publishPdf统一编译归档输出。PDF所有页渲染后视觉核对。日期取真实assignmentBeginTime，旧版及人工修改保留，不向校园提交。\n']
 keep(out/'核对记录.md','\n'.join(records));keep(out/'verification.json',json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--source');p.add_argument('--out');a=p.parse_args()
 if a.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
 elif a.prepare:verify();prepare();print(json.dumps({'ok':True,'prepared':REFS}))
 elif a.source and a.out:build(a.source,a.out);print(json.dumps({'ok':True}))
 else:p.error('choose --verify, --prepare or --source FILE --out DIR')
