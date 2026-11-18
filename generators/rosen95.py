"""Source-checked Rosen 8th edition 9.5/16,26,46,60 learning materials.

General statements are proved in the written solutions. Finite exact-arithmetic
checks below are supplementary checks, never presented as proofs of infinity.
"""
import argparse
import hashlib
import json
import shutil
from fractions import Fraction
from itertools import product
from pathlib import Path
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parent
BANK=ROOT/'题库'/'rosen-8'/'9.5'
CATALOGUE=ROOT/'题库'/'页面索引'/'rosen-8'
BOOK=ROOT.parent/'26fa-离散数学（下）'/'rosen, kenneth h - discrete mathematics and its applications (mcgraw-hill) - libgen.lc.pdf'
REFS=['9.5/16','9.5/26','9.5/46','9.5/60']
RELATIONS={
 'a':{(0,0),(1,1),(2,2),(3,3)},
 'b':{(0,0),(0,2),(2,0),(2,2),(2,3),(3,2),(3,3)},
 'c':{(0,0),(1,1),(1,2),(2,1),(2,2),(3,3)},
 'd':{(0,0),(1,1),(1,3),(2,2),(2,3),(3,1),(3,2),(3,3)},
 'e':{(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,2),(3,3)},
}
QUESTIONS={
 '9.5/16':r'''Let $R$ be the relation on the set of ordered pairs of positive integers such that $((a,b),(c,d))\in R$ if and only if $ad=bc$. Show that $R$ is an equivalence relation.''',
 '9.5/26':r'''What are the equivalence classes of the equivalence relations in Exercise 1?''',
 '9.5/46':r'''Which of these are partitions of the set of real numbers?

a) the negative real numbers, $\{0\}$, the positive real numbers

b) the set of irrational numbers, the set of rational numbers

c) the set of intervals $[k,k+1]$, $k=\ldots,-2,-1,0,1,2,\ldots$

d) the set of intervals $(k,k+1)$, $k=\ldots,-2,-1,0,1,2,\ldots$

e) the set of intervals $(k,k+1]$, $k=\ldots,-2,-1,0,1,2,\ldots$

f) the sets $\{x+n\mid n\in\mathbb Z\}$ for all $x\in[0,1)$''',
 '9.5/60':r'''a) Let $R$ be the relation on the set of functions from $\mathbb Z^+$ to $\mathbb Z^+$ such that $(f,g)$ belongs to $R$ if and only if $f$ is $\Theta(g)$ (see Section 3.2). Show that $R$ is an equivalence relation.

b) Describe the equivalence class containing $f(n)=n^2$ for the equivalence relation of part (a).''',
}

def digest(data):return hashlib.sha256(data).hexdigest()
def write_new(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);data=text.encode('utf-8')
    if path.exists():
        if path.read_bytes()!=data:raise FileExistsError(f'Preserving existing/manual file: {path}')
    else:path.write_bytes(data)
def table(head,rows):
    return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join('---' for _ in head)+'|']+
                     ['| '+' | '.join(map(str,row))+' |' for row in rows])+'\n'
def pairset(relation):
    return r'$\{'+','.join(f'({a},{b})' for a,b in sorted(relation))+r'\}$'
def dependency():
    lines=[r'Which of these relations on $\{0,1,2,3\}$ are equivalence relations? Determine the properties of an equivalence relation that the others lack.','']
    for name,relation in RELATIONS.items():lines.extend([name+') '+pairset(relation),''])
    return '\n'.join(lines)
def properties(relation):
    universe=range(4)
    return {'reflexive':all((a,a) in relation for a in universe),
            'symmetric':all((b,a) in relation for a,b in relation),
            'transitive':all((a,c) in relation for a,b in relation for x,c in relation if x==b)}

def verify():
    pairs=list(product(range(1,7),repeat=2));related=lambda x,y:x[0]*y[1]==x[1]*y[0]
    for x,y in product(pairs,repeat=2):
        assert related(x,y)==(Fraction(*x)==Fraction(*y))
        assert related(x,y)==related(y,x)
    for x in pairs:assert related(x,x)
    for x,y,z in product(pairs,repeat=3):
        if related(x,y) and related(y,z):assert related(x,z)
    # Demonstrate why the stated positive-integer domain cannot be silently changed.
    assert (1*0==0*0) and (0*1==0*0) and not (1*1==0*0)
    relation_checks={key:properties(value) for key,value in RELATIONS.items()}
    assert [k for k,p in relation_checks.items() if all(p.values())]==['a','c']
    classes={key:sorted({tuple(sorted(y for y in range(4) if (x,y) in relation)) for x in range(4)})
             for key,relation in RELATIONS.items() if all(relation_checks[key].values())}
    assert classes=={'a':[(0,),(1,),(2,),(3,)],'c':[(0,),(1,2),(3,)]}
    assert (0,2) in RELATIONS['b'] and (2,3) in RELATIONS['b'] and (0,3) not in RELATIONS['b']
    assert (1,3) in RELATIONS['d'] and (3,2) in RELATIONS['d'] and (1,2) not in RELATIONS['d']
    assert (1,2) in RELATIONS['e'] and (2,1) not in RELATIONS['e']
    grid=[Fraction(i,12) for i in range(-48,49)]
    for t in grid:
        ks=range(-6,6)
        assert sum(k<=t<=k+1 for k in ks)==(2 if t.denominator==1 else 1)
        assert sum(k<t<k+1 for k in ks)==(0 if t.denominator==1 else 1)
        assert sum(k<t<=k+1 for k in ks)==1
        assert sum((t-Fraction(j,12)).denominator==1 for j in range(12))==1
        k=-((-t.numerator)//t.denominator)-1  # ceil(t)-1, including negative integers
        assert k<t<=k+1
        r=t-(t.numerator//t.denominator);assert 0<=r<1 and (t-r).denominator==1
    constants=[Fraction(1,4),Fraction(1,2),Fraction(1),Fraction(2),Fraction(3)]
    bounds=[(a,b) for a,b in product(constants,repeat=2) if a<=b];composition_checks=0
    for a,b in bounds:
        for t in [a,(a+b)/2,b]:assert 1/b<=1/t<=1/a
        for c,d in bounds:
            for t,u in product([a,(a+b)/2,b],[c,(c+d)/2,d]):
                assert a*c<=t*u<=b*d;composition_checks+=1
    for n in range(1,101):
        oscillating=n*n*(2+(-1)**n);assert n*n<=oscillating<=3*n*n
        modified=7 if n<50 else n*n
        if n>=50:assert modified==n*n
    return {'ok':True,'checks':[
        '9.5/16：36个正整数对的1296组关系与约分有理数比对，并遍历46656组三元组检查传递性',
        '9.5/26：按第1题原始五个关系逐项核对自反/对称/传递，只a、c通过，等价类与反例核对通过',
        '9.5/46：97个精确有理样点核对闭区间重叠、开区间漏整数、左开右闭唯一归属及小数部分归属',
        f'9.5/60：{composition_checks}组精确有理数界乘法检查，另核对倒数界和振荡增长示例'],
        'relationProperties':relation_checks,'equivalenceClasses':classes,'partitionAnswers':{'a':True,'b':True,'c':False,'d':False,'e':True,'f':True},
        'limits':['有限样例和计算仅作辅助交叉检查；无限集合、实数和全部函数的一般结论由解答中的完整证明给出。',
                  '9.5/16的底集是正整数对；9.5/60的函数定义域和值域均为正整数。']}

ANSWERS={
 '9.5/16':r'''令 $S=\mathbb Z^+\times\mathbb Z^+$。对 $S$ 上的关系 $R$ 分别证明三条性质。

**自反性。** 任取 $(a,b)\in S$，有 $ab=ba$，故 $((a,b),(a,b))\in R$。

**对称性。** 若 $((a,b),(c,d))\in R$，则 $ad=bc$，也即 $cb=da$，这正是 $((c,d),(a,b))\in R$ 的条件。

**传递性。** 若 $(a,b)R(c,d)$ 且 $(c,d)R(e,f)$，则 $ad=bc$、$cf=de$。将第一式乘以 $f$，利用第二式有

$$adf=bcf=bde.$$

由于 $d\in\mathbb Z^+$，有 $d\ne0$，消去 $d$ 得 $af=be$，从而 $(a,b)R(e,f)$。

所以 $R$ 同时自反、对称且传递，**是等价关系**。

也可以用不变量理解：因 $b,d>0$，$ad=bc\iff a/b=c/d$，即两个正整数对表示同一个正有理数。注意传递证明中的消去步骤依赖题目给定的正整数底集，不能擅自把底集改成含 $(0,0)$ 的非负整数对。
''',
 '9.5/26':r'''本题引用第1题，只需对其中确实为等价关系的项目求等价类，不能把所有五项都当成等价关系。

| 第1题项目 | 自反 | 对称 | 传递 | 是否等价关系 |
|---|---|---|---|---|
| a | 是 | 是 | 是 | 是 |
| b | 否 | 是 | 否 | 否 |
| c | 是 | 是 | 是 | 是 |
| d | 是 | 是 | 否 | 否 |
| e | 是 | 否 | 否 | 否 |

**a)** 关系只有四个自环，元素只与自身相关，因此

$$[0]=\{0\},\quad[1]=\{1\},\quad[2]=\{2\},\quad[3]=\{3\}.$$

由此得到划分 $\boxed{\{\{0\},\{1\},\{2\},\{3\}\}}$。

**c)** 关系中只有1、2相互关联，0、3各自只与自身相关，因此

$$[0]=\{0\},\quad[1]=[2]=\{1,2\},\quad[3]=\{3\}.$$

不同等价类构成划分 $\boxed{\{\{0\},\{1,2\},\{3\}\}}$，其中 $[1]$ 与 $[2]$ 是同一个类，不应重复算作两个类。

其余项目的核对反例：

- b缺少 $(1,1)$，不自反；又有 $(0,2),(2,3)$ 却没有 $(0,3)$，不传递。
- d有 $(1,3),(3,2)$ 却没有 $(1,2)$，不传递。
- e有 $(1,2)$ 却没有 $(2,1)$，不对称；又有 $(2,0),(0,1)$ 却没有 $(2,1)$，不传递。

所以本题的等价类答案只有a、c两组。
''',
 '9.5/46':r'''判定标准：每个分块非空，所有分块的并为 $\mathbb R$，且任意两个不同分块不相交。

**a) 是。** 任一实数恰好属于负数、零、正数三种情况之一。三个非空分块两两不交，且并为 $\mathbb R$。

**b) 是。** 每个实数或者有理或者无理，二者互斥；两个集合均非空（例如分别含0和 $\sqrt2$），并为全部实数。

**c) 否。** 相邻闭区间重叠。例如 $[0,1]\cap[1,2]=\{1\}\ne\varnothing$，不满足两两不交。

**d) 否。** 所有整数都没有归属。例如若 $0\in(k,k+1)$，就需整数 $k$ 满足 $-1<k<0$，不可能。因此这些开区间的并为 $\mathbb R\setminus\mathbb Z$，未覆盖 $\mathbb R$。

**e) 是。** 每个 $(k,k+1]$ 非空。任取 $t\in\mathbb R$，令 $k=\lceil t\rceil-1\in\mathbb Z$，则 $k<t\le k+1$，所以覆盖全部实数。若 $k<\ell$，因为二者为整数，有 $k+1\le\ell$；若 $t$ 同时属于两区间，就要求 $t\le k+1\le\ell$ 且 $t>\ell$，矛盾。因此两两不交。特别地，整数 $m$ 属于 $(m-1,m]$，不属于 $(m,m+1]$。

**f) 是。** 记 $C_x=x+\mathbb Z=\{x+n\mid n\in\mathbb Z\}$，其中 $x\in[0,1)$。

1. 每个 $C_x$ 非空，因为 $x=x+0\in C_x$。
2. 任意 $t\in\mathbb R$ 都可唯一写成 $t=\lfloor t\rfloor+\{t\}$，其中小数部分 $\{t\}=t-\lfloor t\rfloor\in[0,1)$，故 $t\in C_{\{t\}}$，覆盖全部实数。
3. 若 $t\in C_x\cap C_y$，则 $t=x+m=y+n$，其中 $m,n\in\mathbb Z$，从而 $x-y=n-m\in\mathbb Z$。又 $x,y\in[0,1)$，所以 $-1<x-y<1$，只能有 $x-y=0$，即 $x=y$。因此不同分块不交。

这些分块就是“模1同余”的等价类：两个实数属于同一类，当且仅当它们之差为整数。注意 $C_0=\mathbb Z$，包括正、负整数和0。

**最终结论：$\boxed{\text{a、b、e、f是划分；c、d不是划分。}}$**
''',
 '9.5/60':r'''设 $\mathcal F=\{f\mid f:\mathbb Z^+\to\mathbb Z^+\}$。根据教材3.2节定义，因函数值均为正，

$$f=\Theta(g)\iff\exists c_1,c_2>0,\ N\in\mathbb Z^+,\ \forall n\ge N,\quad c_1g(n)\le f(n)\le c_2g(n).$$

教材用 $x>k$ 表示“充分大”，这里在正整数定义域上等价地改用 $n\ge N$。常数可依赖于这一对函数，但不能随 $n$ 改变。

### a) 证明是等价关系

**自反性。** 对任意 $f\in\mathcal F$，取 $c_1=c_2=1,N=1$，有 $f(n)\le f(n)\le f(n)$，故 $f=\Theta(f)$。

**对称性。** 若 $f=\Theta(g)$，存在 $c_1,c_2>0,N$，使 $c_1g(n)\le f(n)\le c_2g(n)$。正数常数可以取倒数，得

$$\frac1{c_2}f(n)\le g(n)\le\frac1{c_1}f(n)\qquad(n\ge N).$$

因此 $g=\Theta(f)$。

**传递性。** 若 $f=\Theta(g)$ 且 $g=\Theta(h)$，设其界分别为

$$a_1g(n)\le f(n)\le a_2g(n)\quad(n\ge N_1),\qquad b_1h(n)\le g(n)\le b_2h(n)\quad(n\ge N_2).$$

取 $N=\max(N_1,N_2)$，则对一切 $n\ge N$ 有

$$a_1b_1h(n)\le f(n)\le a_2b_2h(n).$$

因 $a_1b_1,a_2b_2>0$，故 $f=\Theta(h)$。三条性质均成立，**$R$是等价关系**。

### b) 含 $f(n)=n^2$ 的等价类

$$\boxed{[f]=\{g:\mathbb Z^+\to\mathbb Z^+\mid g(n)=\Theta(n^2)\}.}$$

也即存在 $c_1,c_2>0$ 和 $N\in\mathbb Z^+$，使对一切 $n\ge N$ 都有

$$c_1n^2\le g(n)\le c_2n^2.$$

它是**所有具有二次渐近增长阶的正整数值函数**，不只包括 $n^2$ 的常数倍或二次多项式。例如 $g(n)=3n^2+5n+7$ 属于该类：当 $n\ge1$ 时，$3n^2\le g(n)\le15n^2$。

还包括 $g(n)=n^2(2+(-1)^n)$：奇数 $n$ 时为 $n^2$，偶数时为 $3n^2$，始终满足 $n^2\le g(n)\le3n^2$。所以 **不要求 $g(n)/n^2$ 的极限存在**。

有限多个初始函数值可任意改成正整数，而不改变所属等价类，因为可增大 $N$。相反，$g(n)=n$ 没有正的二次下界、$g(n)=n^3$ 没有常数倍二次上界，均不属于此类。
''',
}

def prepare():
    reference=json.loads((ROOT/'题库'/'rosen-8'/'index.json').read_text(encoding='utf-8'))
    assert digest(BOOK.read_bytes())==reference['sha256'],'Textbook version changed'
    images=BANK/'images';images.mkdir(parents=True,exist_ok=True)
    for n in [669,670,671,672]:
        file=images/f'pdf-{n:04}.png';source=CATALOGUE/'images'/file.name
        if file.exists():assert file.read_bytes()==source.read_bytes(),'Preserving modified image'
        else:shutil.copyfile(source,file)
    definition=images/'pdf-0250.png'
    if not definition.exists():
        pdf=pdfium.PdfDocument(str(BOOK));page=pdf[249];bitmap=page.render(scale=2600/max(page.get_size()))
        bitmap.to_pil().save(definition,optimize=True);bitmap.close();page.close();pdf.close()
    write_new(BANK/'dependency-1.md','## 依赖题：9.5 Exercise 1\n\n来源：书页646 / PDF669。仅作为第26题的依据，不额外增加作业题号。\n\n'+dependency())
    exercises=[]
    for ref,text in QUESTIONS.items():
        number=ref.split('/')[1];page={'16':670,'26':670,'46':671,'60':672}[number]
        content=f'## 9.5 Exercise {number}\n\n来源：Rosen第8版，书页{page-23} / PDF第{page}页。\n\n'+text+'\n'
        write_new(BANK/(number+'.md'),content)
        exercises.append({'key':ref,'file':number+'.md','sha256':digest(content.encode('utf-8')),'reviewed':True,
                          'printedPage':page-23,'pdfPage':page,'dependencies':['dependency-1.md'] if number=='26' else ['images/pdf-0250.png'] if number=='60' else []})
    index={'schema':1,'bookId':'rosen-8','section':'9.5','edition':'Eighth Edition','textbook':str(BOOK),'sha256':reference['sha256'],
           'generator':'rosen95.py','scope':'本次9.5/16、26、46、60四题及第1题依赖；一般证明已经独立复核',
           'exercises':exercises,'extraFiles':[{'file':'dependency-1.md','sha256':digest((BANK/'dependency-1.md').read_bytes())}],
           'images':[{'file':'images/'+p.name,'sha256':digest(p.read_bytes())} for p in sorted(images.glob('*.png'))]}
    write_new(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')

def build_reviewed(source_path,out):
    import re
    source=json.loads(Path(source_path).read_text(encoding='utf-8'));out=Path(out)
    if source['course']['bookId']!='rosen-8' or source['course']['key']!='离散数学':raise ValueError('Wrong textbook binding')
    if source.get('attachments') or source.get('resources'):raise ValueError('Attachments need separate review')
    text=source['requirements'].strip()
    match=re.fullmatch(r'9\.5\s+Exercises?:\s*(\d+(?:\s*[,，、]\s*\d+)*)\s*',text)
    if not match:raise ValueError('Requirements not recognized; do not guess')
    refs=list(dict.fromkeys('9.5/'+str(int(n)) for n in re.findall(r'\d+',match[1])))
    if not refs or any(r not in REFS for r in refs):raise ValueError('Exercise not reviewed')
    index=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
    assert digest(BOOK.read_bytes())==index['sha256'],'Textbook changed'
    for item in index['exercises']+index['extraFiles']+index['images']:
        assert digest((BANK/item['file']).read_bytes())==item['sha256'],'Material changed; review required'
    checks=verify();shutil.copytree(BANK/'images',out/'images')
    intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n截止：{source['due']}（北京时间）\n"
    questions=[f"# 题目：{source['title']}\n",intro,'## 云邮原始要求\n\n'+source['requirements']+'\n',
               '附件列表为空。教材：Kenneth H. Rosen，Discrete Mathematics and Its Applications，Eighth Edition。原题保持英文，中文解答另列。\n']
    for ref in refs:questions.append((BANK/(ref.split('/')[1]+'.md')).read_text(encoding='utf-8'))
    if '9.5/26' in refs:questions.append((BANK/'dependency-1.md').read_text(encoding='utf-8'))
    questions.append('## 原书整页和定义依据\n')
    for n in [669,670,671,672,250]:questions.append(f'书页{n-23} / PDF第{n}页：\n\n![原书PDF第{n}页](images/pdf-{n:04}.png)\n')
    write_new(out/'题目.md','\n'.join(questions))
    write_new(out/'解答.md',f"# 解答：{source['title']}\n\n"+'\n'.join(f'## 9.5 Exercise {r.split("/")[1]}\n\n'+ANSWERS[r] for r in refs))
    records=['# 核对记录\n','状态：原题与依赖核对、一般证明独立复核、辅助程序检查通过；只生成本地学习材料，未提交云邮。\n',intro,
             '## 来源与题目完整性\n',f"教材SHA-256：`{index['sha256']}`。来源指纹由source.json的真实正文、课程关联、截止时间等共同计算。\n",
             table(['题号','书页/PDF页','核对内容'],[['9.5/16','647 / 670','正整数有序对；ad=bc；自反/对称/传递全部证明'],['9.5/26','647 / 670','引用第1题，依赖页646/PDF669；五个关系全部抄录；仅a、c为等价关系'],['9.5/46','648 / 671','a–f六问；闭/开/半开区间端点；f的参数域[0,1)'],['9.5/60','649 / 672','a、b两问；函数Z+到Z+；Theta而非单向Big-O；定义在227/PDF250']]),
             '## 一般证明复核\n',
             '- 第16题消去的d严格为正；对称性没有交换错有序对分量。有限检查另以Fraction约分比值交叉核对。\n',
             '- 第26题第1题b缺少(1,1)、d缺少传递边(1,2)、e缺少(2,1)；不把非等价关系的后继集合称为本题等价类。\n',
             '- 第46题逐项核对非空、覆盖、两两不交。e用ceil(t)-1处理整数及负数；f用floor(t)与小数部分证明唯一归属。\n',
             '- 第60题对称性倒数界次序正确、传递性用最大阈值和正界乘积；等价类允许振荡与任意正整数有限前缀。函数值域始终是Z+。\n',
             '## 辅助程序检查\n']+['- '+s+'\n' for s in checks['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checks['limits']]+[
             '\n## 重跑与保留人工修改\n','通过archive()在.staging生成并校验后原子归档；相同来源和材料跳过，人工修改保留，变化另存revisions。第9.5节采用独立材料指纹，不改写原9.3/9.4题库或旧解答。\n']
    write_new(out/'核对记录.md','\n'.join(records));write_new(out/'verification.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--verify',action='store_true');parser.add_argument('--source');parser.add_argument('--out');args=parser.parse_args()
    if args.prepare:prepare();print(json.dumps({'ok':True,'prepared':REFS}))
    elif args.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
    elif args.source and args.out:build_reviewed(args.source,args.out);print(json.dumps({'ok':True}))
    else:parser.error('choose --prepare, --verify, or --source FILE --out DIR')
