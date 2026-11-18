"""Verified first assignment for BUPT Probability and Stochastic Processes (2021)."""
import argparse,hashlib,json,math,re,shutil
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations,product
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BANK=ROOT/'题库'/'probability-bupt-2021'
CATALOGUE=ROOT/'题库'/'页面索引'/'probability-bupt-2021'
BOOK=ROOT.parent/'26fa-概率论与随机过程'/'概率论与随机过程.pdf'
SHA='80662453203acbf11f5c6b4368c649e2437ba07837dd90465d52f4cceec06200'
REQUIREMENTS='''P65-68
1  3  8  13  18 23(1)    35(2);
p105
2    7     8    9
补充作业：
1 （仅）利用概率公理化定义证明不可能事件的概率是零。（要求，证明不同于p18 性质4）；
2     p35  26'''
REFS=['2/1','2/3','2/8','2/13','2/18','2/23(1)','2/35(2)','3/2','3/7','3/8','3/9','supplement/empty-axioms-v1','1/26']
PAGES={'2/1':[65],'2/3':[65],'2/8':[65],'2/13':[66],'2/18':[66],'2/23(1)':[67],'2/35(2)':[68],
 '3/2':[105],'3/7':[105],'3/8':[105],'3/9':[105],'supplement/empty-axioms-v1':[17,18],'1/26':[35]}
QUESTIONS={
 '2/1':r'''设随机变量 $X$ 的分布函数为

$$F(x)=\begin{cases}A-e^{-x},&x\ge0,\\0,&x<0,\end{cases}$$

求：（1）常数 $A$；（2）$P\{-1<X<1\}$。''',
 '2/3':r'''已知随机变量 $X$ 的分布律为

| X | -2 | 0 | 3 | 5 |
|---|---|---|---|---|
| P | 1/4 | a | 1/2 | 1/12 |

求：（1）待定系数 $a$；（2）分布函数 $F(x)$；（3）$P\{X>-\frac12\},P\{0<X<5\}$。''',
 '2/8':r'''设随机变量 $X$ 的可能取值为 $1,2,\cdots$，且 $P\{X=k\}=\frac1{2^k}\ (k=1,2,\cdots)$。令

$$Y=\begin{cases}1,&\text{如果 }X\text{ 为偶数},\\-1,&\text{如果 }X\text{ 为奇数},\end{cases}$$

试求二次方程 $2x^2+x+Y=0$ 无实根的概率。''',
 '2/13':r'''设 $X\sim\pi(\lambda)$，已知 $P\{X=1\}=P\{X=2\}$，求 $P\{X=4\}$。''',
 '2/18':r'''设连续型随机变量 $X$ 具有概率密度

$$f(x)=\begin{cases}x,&0<x<1,\\a,&1\le x<2,\\0,&\text{其他}.\end{cases}$$

求：（1）常数 $a$；（2）分布函数 $F(x)$；（3）$P\{\frac12<X<4\}$。''',
 '2/23(1)':r'''设连续型随机变量 $X$ 具有对称的概率密度，即对任意的 $x\in\mathbb R$，有 $f(-x)=f(x)$，证明：对任意的 $a>0$，有

（1）$F(-a)=1-F(a)=\frac12-\int_0^af(x)\,\mathrm dx$；

（2）$P\{|X|<a\}=2F(a)-1$；

（3）$P\{|X|>a\}=2[1-F(a)]$。

**作业范围：只要求第（1）问；第（2）（3）问为保留原题完整性列出，不额外作答。**''',
 '2/35(2)':r'''（1）设随机变量 $X\sim U((0,1))$，求 $Y=\ln X$ 的概率密度；

（2）设随机变量 $X\sim U(-1,1)$，求 $Y=|X|$ 的概率密度。

**作业范围：只要求第（2）问；第（1）问为保留原题完整性列出，不额外作答。**''',
 '3/2':r'''盒子中装有3只黑球、2只红球和2只白球，在其中任取4只球，以 $X$ 表示取到的黑球数，以 $Y$ 表示取到的红球数，求：

（1）$X$ 和 $Y$ 的联合分布律；

（2）$P\{X>Y\},P\{Y=2X\},P\{X+Y=3\},P\{X<3-Y\}$。''',
 '3/7':r'''设二维随机变量 $(X,Y)$ 的概率密度为

$$f(x,y)=\begin{cases}a(6-x-y),&0<x<2,\ 2<y<4,\\0,&\text{其他},\end{cases}$$

（1）确定常数 $a$；

（2）求 $P\{X<1,Y<3\},P\{X<1.5\},P\{X+Y\le4\}$。''',
 '3/8':r'''已知随机变量 $(X,Y)$ 的概率密度为

$$f(x,y)=\begin{cases}4xy,&0\le x\le1,\ 0\le y\le1,\\0,&\text{其他},\end{cases}$$

求 $(X,Y)$ 的分布函数。''',
 '3/9':r'''设二维连续型随机变量 $(X,Y)$ 的分布函数为

$$F(x,y)=A\left(B+\arctan\frac{x}{2}\right)\left(C+\arctan\frac{y}{3}\right),$$

求：（1）常数 $A,B,C$；（2）$(X,Y)$ 的概率密度。''',
 'supplement/empty-axioms-v1':'（仅）利用概率公理化定义证明不可能事件的概率是零。（要求，证明不同于p18 性质4）。\n\n来源：云邮真实作业正文的补充作业第1项；教材P17–18仅作公理和原书证明对照，不将其当作另一个课后题号。',
 '1/26':r'''设两个相互独立的事件 $A$ 与 $B$ 都不发生的概率为 $\frac19$，$A$ 发生 $B$ 不发生的概率与 $B$ 发生 $A$ 不发生的概率相等，求 $P(A)$。''',
}

def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(text):return re.sub(r'\s+','',text)
def preserve(file,data):
 file.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,str):data=data.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserving existing/manual file: '+str(file))
 else:file.write_bytes(data)
def qfile(ref):return 'questions/'+ref.replace('/','-').replace('(','-').replace(')','')+'.md'
def simpson(f,a,b):
 a,b=Q(a),Q(b);return (b-a)*(f(a)+4*f((a+b)/2)+f(b))/6

def verify():
 checks=[]
 assert abs((1-math.exp(-1))-0.6321205588285577)<1e-15
 probabilities={-2:Q(1,4),0:Q(1,6),3:Q(1,2),5:Q(1,12)}
 cdf=lambda x:Q(0) if x<-2 else Q(1,4) if x<0 else Q(5,12) if x<3 else Q(11,12) if x<5 else Q(1)
 for x in [Q(n,2) for n in range(-7,14)]:assert cdf(x)==sum((p for k,p in probabilities.items() if k<=x),Q(0))
 assert sum(p for k,p in probabilities.items() if k>Q(-1,2))==Q(3,4)
 assert sum(p for k,p in probabilities.items() if 0<k<5)==Q(1,2)
 checks.append('2/1、2/3：指数概率值、分布律归一化、全部跳跃与21个有理边界样点、严格端点事件核对')
 for m in range(1,31):assert sum((Q(1,4)**k for k in range(1,m+1)),Q(0))==(1-Q(1,4)**m)/3
 assert Q(2)**4/math.factorial(4)==Q(2,3)
 assert 2*math.exp(-2)==2**2*math.exp(-2)/2
 checks.append('2/8、2/13：30个几何级数部分和精确核验；泊松lambda=2代回P1=P2，P4系数为2/3；lambda>0由原书定义视觉核对')
 assert simpson(lambda x:x,0,1)+simpson(lambda x:Q(1,2),1,2)==1
 assert simpson(lambda x:x,Q(1,2),1)+simpson(lambda x:Q(1,2),1,2)==Q(7,8)
 for a in [n/2 for n in range(1,11)]:
  normal=lambda x:(1+math.erf(x/math.sqrt(2)))/2
  laplace=lambda x:math.exp(x)/2 if x<0 else 1-math.exp(-x)/2
  assert abs(normal(-a)-(1-normal(a)))<1e-14
  assert abs(laplace(-a)-(1-laplace(a)))<1e-14
 for y in [Q(n,4) for n in range(-8,9)]:
  preimage=Q(0) if y<0 else max(Q(0),min(Q(1),y)-max(Q(-1),-y))/2
  assert preimage==max(Q(0),min(Q(1),y))
 checks.append('2/18、2/23(1)、2/35(2)：精确多项式积分和端点、20个对称密度示例、17个绝对值变换原像核对；一般结论另有证明')
 colours=['black']*3+['red']*2+['white']*2
 counts=Counter((sum(colours[k]=='black' for k in subset),sum(colours[k]=='red' for k in subset)) for subset in combinations(range(7),4))
 expected=[[0,0,1],[0,6,6],[3,12,3],[2,2,0]]
 assert sum(counts.values())==35
 for i,j in product(range(4),range(3)):
  w=4-i-j;formula=math.comb(3,i)*math.comb(2,j)*math.comb(2,w) if 0<=w<=2 else 0
  assert counts[i,j]==formula==expected[i][j]
 events=[sum(v for (i,j),v in counts.items() if pred(i,j)) for pred in [lambda i,j:i>j,lambda i,j:j==2*i,lambda i,j:i+j==3,lambda i,j:i<3-j]]
 assert events==[19,6,20,10]
 checks.append('3/2：穷举35个带标签无放回组合，与组合数公式和12个单元格独立比对；四事件分子19、6、20、10')
 f=lambda x,y:6-x-y
 integrate=lambda xlo,xhi,ylo,yhi:simpson(lambda x:simpson(lambda y:f(x,y),ylo(x),yhi(x)),xlo,xhi)
 assert integrate(0,2,lambda x:2,lambda x:4)==8
 assert integrate(0,1,lambda x:2,lambda x:3)/8==Q(3,8)
 assert integrate(0,Q(3,2),lambda x:2,lambda x:4)/8==Q(27,32)
 assert integrate(0,2,lambda x:2,lambda x:4-x)/8==Q(2,3)
 H=lambda t:Q(0) if t<=0 else t*t if t<1 else Q(1)
 for x,y in product([Q(n,2) for n in range(-2,5)],repeat=2):
  upperx=max(Q(0),min(Q(1),x));uppery=max(Q(0),min(Q(1),y))
  assert simpson(lambda u:simpson(lambda v:4*u*v,0,uppery),0,upperx)==H(x)*H(y)
 checks.append('3/7、3/8：矩形及三角形积分用Fraction与对三次内多项式精确的Simpson独立核对；49个二维CDF边界样点')
 F=lambda x,y:(math.pi/2+math.atan(x/2))*(math.pi/2+math.atan(y/3))/math.pi**2
 for x,y in product([-6,-2,0,2,6],repeat=2):
  h=1e-3;mixed=(F(x+h,y+h)-F(x+h,y-h)-F(x-h,y+h)+F(x-h,y-h))/(4*h*h)
  target=6/(math.pi**2*(x*x+4)*(y*y+9))
  assert abs(mixed-target)<1e-7
 assert F(-1e12,0)<1e-10 and F(0,-1e12)<1e-10 and abs(F(1e12,1e12)-1)<1e-10
 p=q=Q(2,3);assert (1-p)*(1-q)==Q(1,9) and p*(1-q)==q*(1-p)
 checks.append('3/9、1/26：25组CDF混合差分核对密度、无穷远边界近似检查；独立事件条件和四互斥概率以有理数代回')
 return {'ok':True,'refs':REFS,'checks':checks,'jointCounts':expected,'jointEventCounts':events,
  'limits':['程序只交叉检查有限样例和可计算结果；对称密度与概率公理的一般结论由完整推理核验，不以样例代替证明。',
   '补充证明仅用非负性、规范性和可列可加性；不引用原书依赖P(empty)=0的有限可加性。',
   '第23题只解(1)，第35题只解(2)；不擅自改变泊松参数lambda>0或无放回抽样条件。']}

def prepare():
 assert digest(BOOK.read_bytes())==SHA
 exercises=[]
 for ref in REFS:
  printed=PAGES[ref];pages=[p+11 for p in printed]
  text=f'## {ref}\n\n书页：{",".join(map(str,printed))}；PDF页：{",".join(map(str,pages))}。\n\n'+QUESTIONS[ref]+'\n'
  preserve(BANK/qfile(ref),text)
  exercises.append({'key':ref,'file':qfile(ref),'sha256':digest(text.encode()),'reviewed':True,'printedPages':printed,'pdfPages':pages})
 images=[];target=BANK/'images';target.mkdir(parents=True,exist_ok=True)
 for n in [1,3,28,29,46,50,57,76,77,78,79,116]:
  p=CATALOGUE/'images'/f'pdf-{n:04}.png';dest=target/p.name
  preserve(dest,p.read_bytes());images.append({'file':'images/'+p.name,'sha256':digest(p.read_bytes())})
 extra=[{'file':name,'sha256':digest((BANK/name).read_bytes())} for name in ['solutions.typ','solutions.md']]
 index={'schema':1,'bookId':'probability-bupt-2021','title':'概率论与随机过程','edition':'2021年1月第1版','isbn':'978-7-5635-6266-4',
  'textbook':str(BOOK),'sha256':SHA,'generator':'probability_first.py','requiredRefs':REFS,'requirementsCanonical':canonical(REQUIREMENTS),
  'exercises':exercises,'extraFiles':extra,'images':images,'scope':'本次完整13项；页面索引另覆盖全书11章270题，未核验答案不能直接复用。'}
 preserve(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')

def build(sourcefile,out):
 source=json.loads(Path(sourcefile).read_text(encoding='utf-8'));out=Path(out)
 if source['course']!={'key':'概率论与随机过程','id':'2091774263564029955','name':'概率论与随机过程','bookId':'probability-bupt-2021'}:raise ValueError('Wrong course/textbook binding')
 if source.get('resources') or source.get('attachments'):raise ValueError('Attachments need additional review')
 if canonical(source['requirements'])!=canonical(REQUIREMENTS):raise ValueError('Requirements changed; do not reuse this solved set')
 index=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
 assert digest(BOOK.read_bytes())==SHA
 for item in index['exercises']+index['extraFiles']+index['images']:
  assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed, review before reusing'
 checked=verify();shutil.copytree(BANK/'images',out/'images')
 intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}；截止：{source['due']}（北京时间）。\n"
 parts=['# 题目：'+source['title']+'\n',intro,'## 云邮真实要求\n\n'+source['requirements']+'\n',
  '无附件。教材为北京邮电大学数学系概率教学组编著，北邮出版社2021年1月第1版，ISBN 978-7-5635-6266-4；共321个PDF页。书页+11=PDF页。\n']
 for ref in REFS:parts.append((BANK/qfile(ref)).read_text(encoding='utf-8'))
 parts.append('## 原书题目页及必要定义\n')
 for n in [76,77,78,79,116,46,28,29,50,57,1,3]:parts.append(f'PDF第{n}页'+(f' / 书页{n-11}' if n>11 else ' / 封面或版权')+f'：\n\n![原书PDF第{n}页](images/pdf-{n:04}.png)\n')
 preserve(out/'题目.md','\n'.join(parts));preserve(out/'解答.md',(BANK/'solutions.md').read_bytes())
 shutil.copyfile(ROOT/'templates'/'homework.typ',out/'layout.typ')
 from datetime import datetime
 date=datetime.fromisoformat(source['assignedAt']).strftime('%Y-%m-%d')
 header='#import "layout.typ": homework\n#show: homework.with(course: "概率论与随机过程", assignment: "第一次作业", assigned: '+json.dumps(date)+', due: '+json.dumps(source['due'])+')\n\n'
 preserve(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
 record=['# 核对记录\n',intro,'## 来源与范围\n',f'教材SHA-256：`{SHA}`。课程通过本人学生课程列表和activityId关联确认；未根据标题猜题号。老师标题“第一次”仅补充作业后缀命名为“第一次作业”。\n',
  '共13项：习题2的1、3、8、13、18、23(1)、35(2)，习题3的2、7、8、9，补充公理证明和习题1/26。原题中文、所有被指定的小问、分布表、公式和原书整页全部保留。\n',
  '## 独立推理复核\n',
  '- 第2章3题按F(x)=P(X≤x)保留右连续性，严格不等号事件不包含原子端点；18题密度归一化且拼接处连续。\n',
  '- 第13题查P46/ PDF57确认lambda>0，不额外引入退化参数0；第23题只要求(1)，第35题只要求(2)。原书其余小问仅为完整性保留。\n',
  '- 第3章2题按35种无放回组合枚举，并与组合数公式独立核对，未误用独立二项分布。\n',
  '- 第3章7题三角形区域上界为4-x；第8题CDF覆盖全平面和全部边界；第9题先用负无穷边界确定B、C，再由双正无穷确定A，密度非负且可归一化。\n',
  '- 补充证明采用E1=Omega、En=空集(n≥2)及1≥1+P(空集)，区别于P18全取空集的证明；未使用P18性质5，避免循环。补充26题排除不属于[0,1]的根。\n',
  '## 程序交叉检查\n']+['- '+s+'\n' for s in checked['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checked['limits']]+[
  '\n原生Typst解答、模板及PDF随作业归档。统一入口编译并检查PDF后才记完成；按真实assignmentBeginTime命名。相同指纹跳过，人工修改和历史版本保留。只生成本地学习材料，不提交作业。\n']
 preserve(out/'核对记录.md','\n'.join(record));preserve(out/'verification.json',json.dumps(checked,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');parser.add_argument('--prepare',action='store_true');parser.add_argument('--source');parser.add_argument('--out');args=parser.parse_args()
 if args.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
 elif args.prepare:verify();prepare();print(json.dumps({'ok':True,'prepared':REFS}))
 elif args.source and args.out:build(args.source,args.out);print(json.dumps({'ok':True}))
 else:parser.error('choose --verify, --prepare or --source FILE --out DIR')
