"""Verified second assignment; isolated bank preserves the first assignment."""
import argparse,hashlib,json,math,re,shutil
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent.parent
BANK=ROOT/'题库'/'probability-bupt-2021'/'second'
CAT=ROOT/'题库'/'页面索引'/'probability-bupt-2021'
BOOK=ROOT.parent/'26fa-概率论与随机过程'/'概率论与随机过程.pdf'
SHA='80662453203acbf11f5c6b4368c649e2437ba07837dd90465d52f4cceec06200'
REFS=['1/21','supplement/inclusion-exclusion-induction-v1','1/23','1/26','3/10','3/11','3/15','3/16','3/20','3/26']
REQ='P35     21\n用数学归纳法证明p18 一般加法公式，并应用一般加法公式求解p35   23\np35  26\np105 -108  10   11  15   16    20   26'
PAGES={'1/21':[35],'supplement/inclusion-exclusion-induction-v1':[18],'1/23':[35],'1/26':[35],
 '3/10':[105],'3/11':[105,106],'3/15':[106],'3/16':[106],'3/20':[107],'3/26':[108]}
MATRIX=[[6,5,5,1,1],[7,5,1,1,1],[5,10,10,5,5],[5,2,1,1,3],[5,6,5,1,3]]
QUESTIONS={
 '1/21':r'在 $[0,1]$ 上任取两数，求两数之和小于 $\frac65$ 的概率。',
 'supplement/inclusion-exclusion-induction-v1':'用数学归纳法证明p18 一般加法公式，并应用一般加法公式求解p35   23。\n\n来源：云邮第二次作业真实正文；第23题单独列在1/23。P18原页公式首项印作ΣAᵢ，缺少P；原图保留，解答明确使用概率的加法公式，并注明这处排印问题。',
 '1/23':r'设 $A,B,C$ 是3个事件，已知 $P(A)=P(B)=P(C)=\frac14$，$P(AB)=P(BC)=0$，$P(AC)=\frac18$，求 $A,B,C$ 至少有一个发生的概率。',
 '1/26':r'设两个相互独立的事件 $A$ 与 $B$ 都不发生的概率为 $\frac19$，$A$ 发生 $B$ 不发生的概率与 $B$ 发生 $A$ 不发生的概率相等，求 $P(A)$。',
 '3/10':r'''设 $X,Y$ 都是非负的连续型随机变量，且相互独立。证明：

$$P\{X<Y\}=\int_0^{+\infty}F_X(x)f_Y(x)\,\mathrm dx,$$

其中 $F_X(x)$ 是 $X$ 的分布函数，$f_Y(y)$ 是 $Y$ 的概率密度。''',
 '3/11':'''设 $(X,Y)$ 的分布律为

| Y \\ X | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | 0.06 | 0.05 | 0.05 | 0.01 | 0.01 |
| 2 | 0.07 | 0.05 | 0.01 | 0.01 | 0.01 |
| 3 | 0.05 | 0.10 | 0.10 | 0.05 | 0.05 |
| 4 | 0.05 | 0.02 | 0.01 | 0.01 | 0.03 |
| 5 | 0.05 | 0.06 | 0.05 | 0.01 | 0.03 |

（1）求关于 $X$ 和 $Y$ 的边缘分布律；

（2）求 $X=1$ 时，$Y$ 的条件分布律。''',
 '3/15':r'''设二维随机变量 $(X,Y)$ 的概率密度为

$$f(x,y)=\begin{cases}6x,&0<x<y<1,\\0,&\text{其他},\end{cases}$$

求：（1）$X,Y$ 的边缘概率密度；

（2）当 $X=1/3$ 时，$Y$ 的条件概率密度 $f_{Y|X}(y|X=1/3)$；

（3）$P\{X+Y\le1\}$。''',
 '3/16':r'''设随机变量 $X\sim U(0,1)$，当给定 $X=x(0<x<1)$ 时，随机变量 $Y$ 的条件概率密度为

$$f_{Y|X}(y|x)=\begin{cases}x,&0<y<\frac1x,\\0,&\text{其他},\end{cases}$$

求：（1）$(X,Y)$ 的概率密度；（2）边缘概率密度 $f_Y(y)$；（3）$P\{X>Y\}$。''',
 '3/20':r'''设二维随机变量 $(X,Y)$ 的概率密度为

$$f(x,y)=\begin{cases}e^{-x},&0<y<x,\\0,&\text{其他},\end{cases}$$

求：（1）条件概率密度 $f_{Y|X}(y|x)$；（2）$P\{X\le1\mid Y\le1\}$。''',
 '3/26':r'''设随机变量 $X$ 与 $Y$ 相互独立，其概率密度分别为

$$f_X(x)=\begin{cases}1,&0\le x\le1,\\0,&\text{其他},\end{cases}\qquad
f_Y(y)=\begin{cases}e^{-y},&y>0,\\0,&\text{其他},\end{cases}$$

求 $Z=X+Y$ 的概率密度。''',
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
def exact_integral(f,a,b):
 a,b=Q(a),Q(b);return (b-a)*(f(a)+4*f((a+b)/2)+f(b))/6
def numerical(f,a,b,n=2000):
 assert n%2==0;step=(b-a)/n
 return step/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+step*i) for i in range(1,n)))
def verify():
 checks=[]
 polygon=[(Q(0),Q(0)),(Q(1),Q(0)),(Q(1),Q(1,5)),(Q(1,5),Q(1)),(Q(0),Q(1))]
 area=abs(sum(x*polygon[(i+1)%len(polygon)][1]-y*polygon[(i+1)%len(polygon)][0] for i,(x,y) in enumerate(polygon)))/2
 assert area==Q(17,25)
 membership_checks=0
 for n in range(1,9):
  for mask in range(1<<n):
   total=sum((-1)**(subset.bit_count()+1) for subset in range(1,1<<n) if subset&mask==subset)
   assert total==int(mask!=0);membership_checks+=1
 masses={0:Q(3,8),1:Q(1,8),2:Q(1,4),4:Q(1,8),5:Q(1,8)}
 probability=lambda bits:sum((v for mask,v in masses.items() if mask&bits==bits),Q(0))
 assert sum(masses.values())==1 and [probability(i) for i in [1,2,4]]==[Q(1,4)]*3
 assert [probability(i) for i in [3,5,6,7]]==[Q(0),Q(1,8),Q(0),Q(0)]
 assert sum(v for k,v in masses.items() if k)!=0 and 1-masses[0]==Q(5,8)
 p=q=Q(2,3);assert (1-p)*(1-q)==Q(1,9) and p*(1-q)==q*(1-p)
 checks.append(f'1/21、补充证明、1/23、1/26：有理数鞋带面积17/25；n=1至8全部{membership_checks}种事件成员模式检查容斥符号；八原子概率模型核对5/8；独立事件四概率代回')
 comparisons=0
 for lam,mu in [(1,1),(2,1),(1,2),(3,2),(5,1)]:
  # y=-log(t)/mu converts the expectation against Exp(mu) to [0,1].
  integral=numerical(lambda t:1-t**(lam/mu),0,1,n=10000)
  assert abs(integral-lam/(lam+mu))<1e-6;comparisons+=1
 checks.append(f'3/10：{comparisons}组不同指数率用分位变量积分与lambda/(lambda+mu)交叉核对；一般式由独立密度和Tonelli完整证明')
 matrix=[[Q(x,100) for x in row] for row in MATRIX]
 rows=[sum(row) for row in matrix];cols=[sum(row[j] for row in matrix) for j in range(5)]
 assert rows==list(map(Q,['.18','.15','.35','.12','.20']))
 assert cols==list(map(Q,['.28','.28','.22','.09','.13']))
 assert sum(rows)==sum(cols)==1
 cond=[matrix[j][0]/cols[0] for j in range(5)]
 assert cond==[Q(3,14),Q(1,4),Q(5,28),Q(5,28),Q(5,28)] and sum(cond)==1
 checks.append('3/11：25个概率按整数百分数转Fraction，独立计算全部行/列和及X=1条件分布；两边缘和条件分布均归一化')
 assert exact_integral(lambda x:6*x*(1-x),0,1)==1 and exact_integral(lambda y:3*y*y,0,1)==1
 for x in [Q(i,10) for i in range(1,10)]:
  assert exact_integral(lambda y:6*x,x,1)==6*x*(1-x)
  assert exact_integral(lambda y:1/(1-x),x,1)==1
 for y in [Q(i,10) for i in range(1,10)]:assert exact_integral(lambda x:6*x,0,y)==3*y*y
 by_x=exact_integral(lambda x:6*x*(1-2*x),0,Q(1,2))
 by_y=exact_integral(lambda y:3*y*y,0,Q(1,2))+exact_integral(lambda y:3*(1-y)**2,Q(1,2),1)
 assert by_x==by_y==Q(1,4) and Q(1)/(1-Q(1,3))==Q(3,2)
 checks.append('3/15：两边缘和条件密度用精确多项式积分核对；X+Y≤1区域独立换序分成两个三角片，结果均为1/4')
 for x in [Q(i,10) for i in range(1,10)]:assert exact_integral(lambda y:x,0,1/x)==1
 for y in [Q(1,4),Q(1,2),Q(1),Q(3,2),Q(2),Q(5),Q(10)]:
  marginal=exact_integral(lambda x:x,0,min(Q(1),1/y))
  assert marginal==(Q(1,2) if y<=1 else Q(1,2)/(y*y))
 assert exact_integral(lambda x:x*x,0,1)==Q(1,3)
 assert Q(1,2)+exact_integral(lambda t:Q(1,2),0,1)==1 # tail substitution t=1/y
 checks.append('3/16：逐个x条件归一化、七个y值支持截断及y=1拼接；尾部换元归一化；P(X>Y)=1/3精确核对')
 joint_normalization=numerical(lambda x:x*math.exp(-x),0,40,n=20000)
 assert abs(joint_normalization-1)<1e-11
 num=numerical(lambda x:x*math.exp(-x),0,1);den=numerical(lambda y:math.exp(-y),0,1)
 assert abs(num-(1-2/math.e))<1e-13 and abs(den-(1-1/math.e))<1e-13
 assert abs(num/den-(math.e-2)/(math.e-1))<1e-12
 for x in [Q(1,10),Q(1,2),Q(1),Q(2),Q(5)]:assert exact_integral(lambda y:1/x,0,x)==1
 checks.append('3/20：独立数值积分联合归一化、事件分子与分母及条件比；固定x条件密度精确积分为1，0边缘点不作密度相除')
 f=lambda z:0. if z<=0 else 1-math.exp(-z) if z<=1 else (math.e-1)*math.exp(-z)
 F=lambda z:0. if z<=0 else z-1+math.exp(-z) if z<=1 else 1-(math.e-1)*math.exp(-z)
 for z in [-1,0,.01,.2,.5,.999,1,1.001,1.5,2,5,20]:
  convolution=0 if z<=0 else numerical(lambda x:math.exp(-(z-x)),0,min(1,z),n=1000)
  assert abs(convolution-f(z))<1e-12
  if z>0:
   h=min(1e-5,z/4);assert abs((F(z+h)-F(z-h))/(2*h)-f(z))<4e-6
 norm=numerical(f,0,1)+numerical(f,1,40,n=20000)
 assert abs(norm-1)<1e-11 and f(1)==(math.e-1)/math.e and F(1)==math.exp(-1)
 checks.append('3/26：12个含0/1拼接附近的z值，独立卷积积分核对分段密度；CDF差分、非负性与总质量交叉核验')
 return {'ok':True,'refs':REFS,'checks':checks,'marginalX':[str(x) for x in cols],'marginalY':[str(x) for x in rows],
  'conditionalYgivenX1':[str(x) for x in cond],'answers':{'1/21':'17/25','1/23':'5/8','1/26':'2/3','3/15(3)':'1/4','3/16(3)':'1/3','3/20(2)':'(e-2)/(e-1)'},
  'limits':['有限成员模式和数值样例不是一般证明；容斥公式有完整数学归纳证明，3/10有非负密度积分证明。',
   '3/15、3/16、3/20保留非矩形支持与全部小问；连续点条件用密度比而非除以概率0。',
   'P18一般式第一项原排印缺少P，原页完整保留并明示；推导使用概率的正确标量式。']}
def prepare():
 assert digest(BOOK.read_bytes())==SHA
 exercises=[]
 for ref in REFS:
  printed=PAGES[ref];pdf=[p+11 for p in printed]
  text=f'## {ref}\n\n书页：{",".join(map(str,printed))}；PDF页：{",".join(map(str,pdf))}。\n\n'+QUESTIONS[ref]+'\n'
  keep(BANK/qfile(ref),text);exercises.append({'key':ref,'file':qfile(ref),'sha256':digest(text.encode()),'reviewed':True,'printedPages':printed,'pdfPages':pdf})
 images=[]
 for n in [1,3,28,29,46,116,117,118,119]:
  file=f'images/pdf-{n:04}.png';data=(CAT/file).read_bytes();keep(BANK/file,data);images.append({'file':file,'sha256':digest(data)})
 extra=[{'file':n,'sha256':digest((BANK/n).read_bytes())} for n in ['solutions.typ','solutions.md']]
 keep(BANK/'index.json',json.dumps({'schema':1,'bookId':'probability-bupt-2021','assignment':'second','title':'概率论与随机过程','edition':'2021年1月第1版',
  'isbn':'978-7-5635-6266-4','textbook':str(BOOK),'sha256':SHA,'generator':'probability_second.py','requiredRefs':REFS,
  'requirementsCanonical':canonical(REQ),'exercises':exercises,'extraFiles':extra,'images':images,
  'scope':'第二次完整10项；1/23强制按一般加法公式，第1章重复26重新保留；第3章11表跨页，全部小问完整。'},ensure_ascii=False,indent=2)+'\n')
def build(sourcefile,out):
 source=json.loads(Path(sourcefile).read_text(encoding='utf-8'));out=Path(out)
 if source['course']!={'key':'概率论与随机过程','id':'2091774263564029955','name':'概率论与随机过程','bookId':'probability-bupt-2021'}:raise ValueError('Wrong course/textbook binding')
 if source.get('attachments') or source.get('resources'):raise ValueError('Attachments need review')
 if canonical(source['requirements'])!=canonical(REQ):raise ValueError('Changed requirements need full review')
 index=json.loads((BANK/'index.json').read_text(encoding='utf-8'));assert digest(BOOK.read_bytes())==SHA
 for item in index['exercises']+index['extraFiles']+index['images']:assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed'
 checked=verify();shutil.copytree(BANK/'images',out/'images')
 intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}；截止：{source['due']}（北京时间）。\n"
 parts=['# 题目：'+source['title']+'\n',intro,'## 云邮真实正文\n\n'+source['requirements']+'\n',
  '无附件。北邮出版社2021年1月第1版，ISBN 978-7-5635-6266-4；教材SHA256：`'+SHA+'`；书页+11=PDF页。\n']
 for ref in REFS:parts.append((BANK/qfile(ref)).read_text(encoding='utf-8'))
 parts.append('## 原书整页、版本及公式依据\n\n本次题目没有另设题图；第3章11题原分布表跨P105—106，两页一并保留。\n')
 for n in [46,116,117,118,119,28,29,1,3]:parts.append(f'PDF第{n}页'+(f'／书页{n-11}' if n>11 else '／封面或版权页')+f'：\n\n![原书PDF第{n}页](images/pdf-{n:04}.png)\n')
 keep(out/'题目.md','\n'.join(parts));keep(out/'解答.md',(BANK/'solutions.md').read_bytes());shutil.copyfile(ROOT/'templates/homework.typ',out/'layout.typ')
 date=datetime.fromisoformat(source['assignedAt']).strftime('%Y-%m-%d')
 header='#import "layout.typ": homework\n#show: homework.with(course: "概率论与随机过程", assignment: "第二次作业", assigned: '+json.dumps(date)+', due: '+json.dumps(source['due'])+')\n\n'
 keep(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
 records=['# 核对记录\n',intro,'## 来源与完整性\n',
  '本人学生课程与活动ID关联已由只读入口核实；正文不按标题猜题号。P35的21、23、26以及P105—108的10、11、15、16、20、26逐项对照。另有P18公式的数学归纳证明，共10项；无附件。\n',
  '第3章11题题干在P105，表及两问在P106，25个概率已按行Y列X逐个视觉转录；15、16各三问、20两问全部作答，26的两密度与独立条件完整。原题和原书整页、版本页全部保留。\n',
  'P18原书一般式首项缺少P，原截图未改；解答明确注记排印问题，并由同页两事件式归纳证明正确的概率公式。未使用该公式本身证明基础。\n',
  '## 独立推理复核\n',
  '- 1/21采用独立均匀的几何概率模型，补三角形与鞋带面积核对；边界线为零面积。\n',
  '- 容斥归纳步骤分别处理包含与不包含最后指标的交集，系数符号反转正确。1/23先以单调性得三重交概率0，再应用已证公式，不把零概率事件武断当空集。1/26保留独立性并排除4/3伪根。\n',
  '- 3/10用非负联合密度与独立性证明，连续性确保严格不等号无边界原子。3/11所有行列和及X=1条件分布用Fraction核对。\n',
  '- 3/15三角支持0<x<y<1，X+Y≤1的x上限1/2；连续点条件使用密度比。3/16支持0<y<1/x，边缘在y=1分段，不假定独立。\n',
  '- 3/20先求边缘xe^-x和e^-y；Y<X使X≤1蕴含Y≤1，分母非零；不将事件条件替换为Y=1。\n',
  '- 3/26卷积交集为0<x<min(1,z)，在z=0、1处分段且密度连续，CDF、尾部与归一化复核。\n',
  '## 程序核验\n']+['- '+s+'\n' for s in checked['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checked['limits']]+[
  '\n原生Typst、本地模板、原题、解答、原书截图与核对结果随作业归档；PDF由统一入口编译并逐页视觉检查。命名日期来自真实assignmentBeginTime，不是截止日或抓取日。相同指纹跳过，人工修改与历史版本保留，不自动提交。\n']
 keep(out/'核对记录.md','\n'.join(records));keep(out/'verification.json',json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--source');p.add_argument('--out');a=p.parse_args()
 if a.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
 elif a.prepare:verify();prepare();print(json.dumps({'ok':True,'prepared':REFS}))
 elif a.source and a.out:build(a.source,a.out);print(json.dumps({'ok':True}))
 else:p.error('choose --verify, --prepare or --source FILE --out DIR')
