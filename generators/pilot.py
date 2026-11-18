"""Audited sample materials and reproducible, independently checked calculations.

This is a solver for the five explicitly reviewed exercises, not a general model API.
New task contents must be reviewed by the agent before being approved.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT.parent / '26fa-离散数学（下）' / 'rosen, kenneth h - discrete mathematics and its applications (mcgraw-hill) - libgen.lc.pdf'
BANK = ROOT / '题库' / 'rosen-8'
LETTERS = list('abcde')
CASES = {
    'a': [('a','c'),('b','d'),('c','a'),('d','b'),('e','d')],
    'b': [('b','c'),('b','e'),('c','e'),('d','a'),('e','b'),('e','c')],
    'c': [('a','b'),('a','c'),('a','e'),('b','a'),('b','c'),('c','a'),('c','b'),('d','a'),('e','d')],
    'd': [('a','e'),('b','a'),('b','d'),('c','d'),('d','a'),('d','c'),('e','a'),('e','b'),('e','c'),('e','e')],
}
GRAPHS = {
    '26': {('a','a'),('b','b'),('c','c'),('d','d'),('a','b'),('b','a'),('c','a'),('c','d')},
    '27': set(product('abc','abc')) - {('c','c')} | {('d','d')},
    '28': set(product('ab','ab')) | set(product('cd','cd')),
}
QUESTION_TEXT = {
    '9.3/14': r'''Let $R_1$ and $R_2$ be relations on a set $A$ represented by the matrices

$$
M_{R_1}=\begin{bmatrix}0&1&0\\1&1&1\\1&0&0\end{bmatrix}
\quad\text{and}\quad
M_{R_2}=\begin{bmatrix}0&1&0\\0&1&1\\1&1&1\end{bmatrix}.
$$

Find the matrices that represent

a) $R_1\cup R_2$.  b) $R_1\cap R_2$.  c) $R_2\circ R_1$.

d) $R_1\circ R_1$.  e) $R_1\oplus R_2$.
''',
    '9.3/32': '''Determine whether the relations represented by the directed graphs shown in Exercises 26–28 are reflexive, irreflexive, symmetric, antisymmetric, asymmetric, and/or transitive.

本题依赖的原书题图（26、27、28）如下；箭头和自环均保留。

![Exercise 26](images/9.3-graph-26.png)

![Exercise 27](images/9.3-graph-27.png)

![Exercise 28](images/9.3-graph-28.png)
''',
    '9.4/26': r'''Use Algorithm 1 to find the transitive closures of these relations on $\{a,b,c,d,e\}$.

a) $\{(a,c),(b,d),(c,a),(d,b),(e,d)\}$

b) $\{(b,c),(b,e),(c,e),(d,a),(e,b),(e,c)\}$

c) $\{(a,b),(a,c),(a,e),(b,a),(b,c),(c,a),(c,b),(d,a),(e,d)\}$

d) $\{(a,e),(b,a),(b,d),(c,d),(d,a),(d,c),(e,a),(e,b),(e,c),(e,e)\}$
''',
    '9.4/28': r'''Use Warshall’s algorithm to find the transitive closures of the relations in Exercise 26.

依赖题目：上方 9.4/26 的四组关系，原书书页 638 / PDF 第 661 页。
''',
    '9.4/29': r'''Find the smallest relation containing the relation $\{(1,2),(1,4),(3,3),(4,1)\}$ that is

a) reflexive and transitive.

b) symmetric and transitive.

c) reflexive, symmetric, and transitive.
''',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_new(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(text)

def bm(vertices, relation):
    return [[int((i,j) in relation) for j in vertices] for i in vertices]

def pairs(vertices, matrix):
    return {(vertices[i],vertices[j]) for i in range(len(vertices)) for j in range(len(vertices)) if matrix[i][j]}

def boolean_product(a, b):
    n = len(a)
    return [[int(any(a[i][k] and b[k][j] for k in range(n))) for j in range(n)] for i in range(n)]

def join(a,b):
    return [[int(x or y) for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def powers(vertices, relation):
    original = bm(vertices,relation)
    result = [original]
    for _ in range(1,len(vertices)):
        result.append(boolean_product(result[-1],original))
    return result

def warshall(vertices, relation):
    result = [bm(vertices,relation)]
    for k in range(len(vertices)):
        old = result[-1]
        result.append([[int(old[i][j] or (old[i][k] and old[k][j])) for j in range(len(vertices))] for i in range(len(vertices))])
    return result

def reachable(vertices, relation, allowed=None):
    # Independent graph search. Initial frontier uses edges, never the empty path.
    closure = set()
    for start in vertices:
        seen, stack = set(), [b for a,b in relation if a == start]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            if allowed is None or current in allowed:
                stack.extend(b for a,b in relation if a == current and b not in seen)
        closure.update((start,end) for end in seen)
    return closure

def properties(vertices, relation):
    reflexive = all((a,a) in relation for a in vertices)
    irreflexive = all((a,a) not in relation for a in vertices)
    symmetric = all((b,a) in relation for a,b in relation)
    antisymmetric = all(a == b or (b,a) not in relation for a,b in relation)
    asymmetric = all((b,a) not in relation for a,b in relation)
    transitive = all((a,c) in relation for a,b in relation for x,c in relation if b == x)
    return [reflexive,irreflexive,symmetric,antisymmetric,asymmetric,transitive]

def fmt_set(relation):
    return r'\varnothing' if not relation else r'\{' + ','.join(f'({a},{b})' for a,b in sorted(relation)) + r'\}'

def matrix_tex(matrix):
    return r'\begin{bmatrix}' + r'\\'.join('&'.join(map(str,row)) for row in matrix) + r'\end{bmatrix}'

def equation(content):
    return '\n$$\n' + content + '\n$$\n\n'

def relation29():
    vertices = [1,2,3,4]
    base = {(1,2),(1,4),(3,3),(4,1)}
    identity = {(x,x) for x in vertices}
    a = reachable(vertices,base | identity)
    b = reachable(vertices,base | {(y,x) for x,y in base})
    c = b | identity
    return vertices,base,[a,b,c]

def verify():
    checks = []
    for label,edges in CASES.items():
        edges = set(edges)
        ps,ws = powers(LETTERS,edges),warshall(LETTERS,edges)
        union = set().union(*(pairs(LETTERS,m) for m in ps))
        bfs = reachable(LETTERS,edges)
        assert union == pairs(LETTERS,ws[-1]) == bfs
        assert edges <= bfs and properties(LETTERS,bfs)[5]
        for k,matrix in enumerate(ws):
            assert pairs(LETTERS,matrix) == reachable(LETTERS,edges,set(LETTERS[:k]))
        for exponent,m in enumerate(ps,1):
            # Enumerate walks independently of matrix multiplication, all 5^6 at most.
            walking = {walk for walk in product(LETTERS,repeat=exponent+1)
                       if all((walk[i],walk[i+1]) in edges for i in range(exponent))}
            assert pairs(LETTERS,m) == {(w[0],w[-1]) for w in walking}
        checks.append(f'9.4/26,28({label}): 布尔幂、Warshall、独立图搜索一致；每个 R^1..R^5 经路径枚举核验，每个 W_0..W_5 经限制内部顶点的图搜索核验')
    expected = {'26':[True,False,False,False,False,False], '27':[False,False,True,False,False,False],
                '28':[True,False,True,False,False,True]}
    for label,edges in GRAPHS.items():
        assert properties(list('abcd'),edges) == expected[label]
        checks.append(f'9.3/32 图{label}: 六种性质通过全量枚举检查（箭头转录已逐图核对）')
    vertices,base,closures=relation29()
    free=sorted(set(product(vertices,vertices))-base)
    for index,closure in enumerate(closures):
        for mask in range(1 << len(free)):
            candidate=base | {free[i] for i in range(len(free)) if mask & (1<<i)}
            p=properties(vertices,candidate)
            qualifies=[p[0] and p[5],p[2] and p[5],p[0] and p[2] and p[5]][index]
            if qualifies:
                assert closure <= candidate
        p=properties(vertices,closure)
        assert [p[0] and p[5],p[2] and p[5],p[0] and p[2] and p[5]][index]
    checks.append('9.4/29: 对全部 4096 个包含原关系的候选关系逐个验证三项答案的性质及最小性')
    # Exercise 14: relational composition independently compared to matrix operations.
    a=[[0,1,0],[1,1,1],[1,0,0]]; b=[[0,1,0],[0,1,1],[1,1,1]]
    vertices=[1,2,3]; ar=pairs(vertices,a);br=pairs(vertices,b)
    for left,right,lm,rm in [(ar,br,a,b),(ar,ar,a,a)]:
        comp={(i,k) for i,j in left for x,k in right if j==x}
        assert pairs(vertices,boolean_product(lm,rm))==comp
    assert pairs(vertices,join(a,b))==ar|br
    assert pairs(vertices,[[x&y for x,y in zip(aa,bb)] for aa,bb in zip(a,b)])==ar&br
    assert pairs(vertices,[[x^y for x,y in zip(aa,bb)] for aa,bb in zip(a,b)])==ar^br
    checks.append('9.3/14: 并、交、合成及对称差均与独立有序对集合运算一致')
    return {'ok':True,'checks':checks,'assumptions':['9.4/29 的底集按原关系出现的元素取 {1,2,3,4}；若另有底集，须补充该底集的自反项'],
            'limits':['程序验证数学计算，不替代题图箭头或题号的人工识别核对','未与教师标准答案比对']}

def prepare():
    from PIL import Image
    from pypdf import PdfReader
    reader=PdfReader(BOOK)
    assert len(reader.pages)==1118 and 'Eighth Edition' in reader.pages[0].extract_text()
    images=BANK/'images'
    images.mkdir(parents=True,exist_ok=True)
    for page in [650,661,657]:
        dest=images/f'pdf-{page}.png'
        if not dest.exists():
            subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','140','-singlefile','-png',str(BOOK),str(dest.with_suffix(''))],check=True,capture_output=True)
    page=Image.open(images/'pdf-650.png')
    for label,box in {'26':(870,490,1080,660),'27':(643,660,863,825),'28':(871,660,1080,825)}.items():
        dest=images/f'9.3-graph-{label}.png'
        if not dest.exists():
            page.crop(box).save(dest)
    manifest={'schema':1,'bookId':'rosen-8','title':'Discrete Mathematics and Its Applications','author':'Kenneth H. Rosen',
              'edition':'Eighth Edition','textbook':str(BOOK),'sha256':digest(BOOK.read_bytes()),'pages':1118,
              'scope':'仅本次作业的 5 道习题，不表示整本教材已整理','exercises':[]}
    for ref,text in QUESTION_TEXT.items():
        section,number=ref.split('/')
        printed,pdf=(627,650) if section=='9.3' else (638,661)
        question=f'## {section} Exercise {number}\n\n来源：Rosen，第 8 版，书页 {printed} / PDF 第 {pdf} 页。\n\n{text}'
        file=BANK/section/f'{number}.md'
        if not file.exists():
            write_new(file,question)
        manifest['exercises'].append({'key':ref,'file':f'{section}/{number}.md','printedPage':printed,'pdfPage':pdf,
                                     'sha256':digest(file.read_bytes()),'reviewed':True,
                                     'dependencies':['9.3/26-28 diagrams'] if ref=='9.3/32' else ['9.4/26'] if ref=='9.4/28' else []})
    if not (BANK/'index.json').exists():
        write_new(BANK/'index.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest

def solution(title='第三次作业——关系的表示及关系闭包',refs=None):
    out=['# 解答：'+title+'\n',
         '所有矩阵按题目给定元素顺序排列。合成 $S\\circ R$ 表示先走 $R$ 再走 $S$，因此 $M_{S\\circ R}=M_R\\odot M_S$；$\\odot$ 为布尔乘积。\n',
         '## 9.3 Exercise 14\n',
         '并、交、对称差分别逐项取 OR、AND、XOR。合成使用布尔乘积 $(A\\odot B)_{ij}=\\bigvee_k(a_{ik}\\land b_{kj})$。\n']
    a=[[0,1,0],[1,1,1],[1,0,0]];b=[[0,1,0],[0,1,1],[1,1,1]]
    results=[('a',r'M_{R_1\cup R_2}',join(a,b)),('b',r'M_{R_1\cap R_2}',[[x&y for x,y in zip(aa,bb)] for aa,bb in zip(a,b)]),
             ('c',r'M_{R_2\circ R_1}=M_{R_1}\odot M_{R_2}',boolean_product(a,b)),
             ('d',r'M_{R_1\circ R_1}=M_{R_1}\odot M_{R_1}',boolean_product(a,a)),
             ('e',r'M_{R_1\oplus R_2}',[[x^y for x,y in zip(aa,bb)] for aa,bb in zip(a,b)])]
    for label,name,value in results:
        out.append(f'### ({label})\n'+equation(name+'='+matrix_tex(value)))
        if label in ['c','d']:
            right=b if label=='c' else a
            for i in range(3):
                selected=[str(k+1) for k in range(3) if a[i][k]]
                out.append(f'第 {i+1} 行选取右矩阵第 {"、".join(selected)} 行逐项取 OR，得到 $({",".join(map(str,value[i]))})$。\n')
    out.extend(['## 9.3 Exercise 32\n','先按原图逐条读出关系，再检查六个定义。这里“非对称”指 asymmetric，“反对称”指 antisymmetric。\n',
                '| 原书图号 | 自反 | 反自反 | 对称 | 反对称 | 非对称 | 传递 |\n|---|---|---|---|---|---|---|\n'])
    for label,edges in GRAPHS.items():
        out.append('| '+label+' | '+' | '.join('是' if p else '否' for p in properties(list('abcd'),edges))+' |\n')
    reasons={
        '26': '四个顶点都有自环，故自反而不反自反。存在 $c\\to a$ 却没有 $a\\to c$，故不对称；$a\\leftrightarrow b$ 且 $a\\ne b$，故不反对称；自环也排除了非对称。$c\\to a\\to b$ 但没有 $c\\to b$，故不传递。',
        '27': '只有 $a,b,d$ 有自环，$c$ 没有，因此既不自反也不反自反。不同顶点之间的边都成对出现，故对称；$a\\leftrightarrow b$ 排除反对称，自环排除非对称。$c\\to a\\to c$ 但没有 $c\\to c$，故不传递。',
        '28': '关系为 $\\{a,b\\}^2\\cup\\{c,d\\}^2$，两个连通分组内所有有序对都存在，所以自反、对称、传递。存在自环，故不反自反也不非对称；存在 $a\\leftrightarrow b$，故不反对称。',
    }
    for label,edges in GRAPHS.items():
        out.append(f'### 图 {label}\n'+equation(f'R_{{{label}}}='+fmt_set(edges))+reasons[label]+'\n\n')
    out.extend(['## 9.4 Exercise 26：Algorithm 1\n',
                '按 $a,b,c,d,e$ 排列。此处 $R^*$ 是正长度路径的可达关系，不自动加入单位关系。五个顶点只需计算到 $R^5$。\n',
                equation(r'P_1=M_R,\quad B_1=P_1,\quad P_n=P_{n-1}\odot M_R,\quad B_n=B_{n-1}\lor P_n\quad(2\le n\le5).'),
                '下面每个 $P_n$ 都是 $R^n$ 的具体矩阵；同时列出加入累计关系的新有序对。\n'])
    for label,edges in CASES.items():
        out.append(f'### ({label})\n')
        cumulative=set()
        for n,m in enumerate(powers(LETTERS,set(edges)),1):
            relation=pairs(LETTERS,m)
            out.append(equation(f'P_{n}=M_{{R^{n}}}='+matrix_tex(m)))
            out.append(equation(f'R^{n}='+fmt_set(relation)))
            out.append('本步相对累计关系新增：'+equation(fmt_set(relation-cumulative)))
            cumulative |= relation
        out.append('最终传递闭包：'+equation(r'R^*=\bigcup_{n=1}^{5}R^n='+fmt_set(cumulative)))
        out.append(equation(r'M_{R^*}=B_5='+matrix_tex(bm(LETTERS,cumulative))))
    out.extend(['## 9.4 Exercise 28：Warshall 算法\n',
                '仍按 $v_1=a,v_2=b,v_3=c,v_4=d,v_5=e$ 排列。$W_0=M_R$，不预先把主对角线置为 1。\n',
                equation(r'w^{(k)}_{ij}=w^{(k-1)}_{ij}\lor\bigl(w^{(k-1)}_{ik}\land w^{(k-1)}_{kj}\bigr).'),
                '每一步只扩大允许作为内部顶点的集合；下面完整列出 $W_0$ 到 $W_5$ 以及该步新加入的边。\n'])
    for label,edges in CASES.items():
        out.append(f'### ({label})\n')
        stages=warshall(LETTERS,set(edges))
        for k,m in enumerate(stages):
            out.append(equation(f'W_{k}='+matrix_tex(m)))
            if k:
                added=pairs(LETTERS,m)-pairs(LETTERS,stages[k-1])
                out.append(f'允许中间顶点 {LETTERS[k-1]} 后新增：'+equation(fmt_set(added)))
        out.append('最终 $M_{R^*}=W_5$，与第 26 题对应小问的 $B_5$ 完全一致。\n\n')
    vertices,base,closures=relation29()
    out.extend(['## 9.4 Exercise 29\n','底集按题中出现的元素取 $A=\\{1,2,3,4\\}$。若教师另行指定更大底集，(a)、(c) 须补上额外元素的自反项。\n',
                '### (a) 自反且传递\n',
                '先补齐 $(1,1),(2,2),(4,4)$。路径 $4\\to1\\to2$ 强制加入 $(4,2)$；其余所需边已存在。\n',
                equation('T_a='+fmt_set(closures[0])),
                '这些有序对均由自反性或原关系中的路径强制产生，所得关系又自反且传递，故为最小关系。\n',
                '### (b) 对称且传递\n',
                '对称性先强制加入 $(2,1)$。顶点 $1,2,4$ 通过双向边连通；传递性强制该组三个元素之间的全部有序对，包括三个自环。$3$ 只保留原有的 $(3,3)$。\n',
                equation(r'T_b=\{1,2,4\}\times\{1,2,4\}\cup\{(3,3)\}='+fmt_set(closures[1])),
                '任意包含原关系的对称、传递关系都必须包含这些反向边及路径结果；结果自身满足两种性质，故最小。\n',
                '### (c) 自反、对称且传递\n',
                '第 (b) 问的结果在底集 $A$ 上已经自反，因此不必再添加有序对：\n',
                equation('T_c=T_b='+fmt_set(closures[2])),
                '它对应等价类 $\\{1,2,4\\}$ 和 $\\{3\\}$。最小性由 (b) 的最小性直接推出。\n'])
    text='\n'.join(out)
    if refs is not None:
        selected=[]
        for block in re.split(r'(?m)(?=^## )',text):
            heading=re.match(r'^## (\d+\.\d+) Exercise (\d+)',block)
            if not heading or f'{heading[1]}/{heading[2]}' in refs:
                selected.append(block)
        text=''.join(selected)
    return compact_markdown(text)

def compact_markdown(text):
    # A blank line would end a CommonMark table, so table rows must stay adjacent.
    return re.sub(r'(?m)(?<=\|)\n\n(?=\|)', '\n', text)

def source_references(source):
    text=source['requirements']
    headings=list(re.finditer(r'\b(\d+\.\d+)\s+Exercises?\s*[:：]',text,re.I))
    if not headings or text[:headings[0].start()].strip():
        raise ValueError('题号格式未核实')
    refs=[]
    for i,heading in enumerate(headings):
        clause=text[heading.end():headings[i+1].start() if i+1<len(headings) else len(text)]
        clause=re.sub(r'[（(][^）)]*[）)]','',clause)
        if not re.fullmatch(r'\s*\d+(?:\s*[,，、]\s*\d+)*\s*[.。]?\s*',clause):
            raise ValueError('存在无法可靠解析的题号或附加要求')
        refs.extend(f'{heading[1]}/{int(n)}' for n in re.findall(r'\d+',clause))
    refs=list(dict.fromkeys(refs))
    if any(ref not in QUESTION_TEXT for ref in refs):
        raise ValueError('题库未覆盖，不生成假定答案')
    return refs

def build(source_path,outdir):
    outdir=Path(outdir)
    source=json.loads(Path(source_path).read_text(encoding='utf-8'))
    if source['course']['bookId']!='rosen-8':
        raise ValueError('教材不符合已核对的题库')
    refs=source_references(source)
    manifest=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
    if digest(BOOK.read_bytes())!=manifest['sha256']:
        raise ValueError('教材已变更，必须重新核对版本')
    for exercise in manifest['exercises']:
        if digest((BANK/exercise['file']).read_bytes())!=exercise['sha256']:
            raise ValueError('题库文件被修改，必须重新核对')
    checks=verify()
    shutil.copytree(BANK/'images',outdir/'images')
    questions=['# 题目：'+source['title']+'\n',
               f"课程：{source['course']['name']}\n\n截止时间：{source['due']}（北京时间）\n\n待办 ID：{source['id']}\n",
               '## 云邮原始要求\n\n'+source['requirements']+'\n',
               '本次平台返回的附件列表为空。请同时遵守上方云邮正文中的附加要求。\n',
               '教材：Kenneth H. Rosen, *Discrete Mathematics and Its Applications*, Eighth Edition。原题保持英文，解答另列。\n']
    for exercise in manifest['exercises']:
        if exercise['key'] in refs:
            questions.append((BANK/exercise['file']).read_text(encoding='utf-8'))
    if '9.4/28' in refs and '9.4/26' not in refs:
        questions.append('## 第 28 题的题干依赖\n\n以下第 26 题提供四组原关系，不额外增加本次作答范围。\n\n'+(BANK/'9.4'/'26.md').read_text(encoding='utf-8'))
    questions.extend(['## 原书整页核对图\n','书页 627 / PDF 第 650 页：\n\n![原书书页627](images/pdf-650.png)\n',
                      '书页 638 / PDF 第 661 页：\n\n![原书书页638](images/pdf-661.png)\n',
                      'Algorithm 1，书页 634 / PDF 第 657 页：\n\n![Algorithm 1](images/pdf-657.png)\n'])
    write_new(outdir/'题目.md','\n'.join(questions))
    write_new(outdir/'解答.md',solution(source['title'],refs))
    record=['# 核对记录\n','状态：样本题目转录、图形核对与数学计算检查完成；未提交到云邮。\n',
            '## 来源与定位\n',f"教材 SHA-256：`{manifest['sha256']}`；共 {manifest['pages']} 页。\n",
            '课程归属由课程活动列表中的同一 activityId 确认，不根据作业标题猜测。\n',
            '作业正文和题号来自 `/ykt-site/work/detail?assignmentId=…`；课程关联来自 `/ykt-site/site/list/activity?siteId=…&type=3`。\n',
            '| 题目 | 书页 | PDF 页 | 已核对内容 |\n|---|---|---|---|\n',
            '| 9.3/14 | 627 | 650 | 两个矩阵及 a–e 五个小问；合成顺序与原书一致 |\n',
            '| 9.3/32 | 627 | 650 | 依赖图 26–28 的箭头和自环，六种关系性质全部覆盖 |\n',
            '| 9.4/26 | 638 | 661 | a–d 四组关系，全部 R¹ 到 R⁵，累计新增边与最终闭包 |\n',
            '| 9.4/28 | 638 | 661 | 复用第26题，全部 W₀ 到 W₅ 和每步新增边 |\n',
            '| 9.4/29 | 638 | 661 | a–c 三种闭包及最小性说明 |\n',
            '题库只覆盖上述五题；图 26–28 作为第 32 题的依赖保存，不标记为另行完成的作业。\n',
            '## 程序验证\n']
    record += ['- '+c+'\n' for c in checks['checks']]
    record += ['\n## 假设与质量边界\n']+['- '+c+'\n' for c in checks['assumptions']+checks['limits']]
    record += ['\n## 重跑与更新\n','相同来源和相同材料跳过生成；人工修改保留。教师要求、题库或解答器变化后进入复核流程，已核对的新版本另存 revisions，不覆盖旧答案。只有原子归档及 verification.json 检查通过后，才写入完成清单。\n']
    write_new(outdir/'核对记录.md',compact_markdown('\n'.join(record)))
    write_new(outdir/'verification.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--source')
    parser.add_argument('--out')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        prepare()
        print(json.dumps({'ok':True,'preparedExercises':list(QUESTION_TEXT)},ensure_ascii=True))
    elif args.verify:
        print(json.dumps(verify(),ensure_ascii=True,indent=2))
    elif args.source and args.out:
        build(args.source,args.out)
        print(json.dumps({'ok':True,'output':str(args.out)},ensure_ascii=True))
    else:
        parser.error('choose --prepare, --verify, or --source FILE --out DIR')
