"""Reviewed Rosen 8e 9.6/4,16,32,44; source-checked originals and native Typst.

General arguments are in solutions.typ/md. Finite exhaustive checks supplement
those arguments and independently reconstruct the visually audited Hasse graph.
"""
import argparse
import hashlib
import json
import re
import shutil
from itertools import combinations, product
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
BANK=ROOT/'题库'/'rosen-8'/'9.6'
CATALOGUE=ROOT/'题库'/'页面索引'/'rosen-8'
BOOK=ROOT.parent/'26fa-离散数学（下）'/'rosen, kenneth h - discrete mathematics and its applications (mcgraw-hill) - libgen.lc.pdf'
BOOK_SHA='e5225d3f27c87b5ec156d89c692697f049b9bfe57363e3275eec34753a405177'
REFS=['9.6/4','9.6/16','9.6/32','9.6/44']
PAGES={'4':685,'16':685,'32':686,'44':687}
VERTICES=list('abcdefghijklm')
# Visually read from P663/PDF686, oriented from lower to upper. 13 vertices,
# 15 covers. In particular b--d and d--h exist; f--h does not exist.
COVERS=[('a','d'),('b','d'),('b','e'),('c','f'),('d','i'),('d','h'),
        ('e','h'),('f','g'),('i','j'),('h','j'),('h','k'),('g','k'),
        ('j','l'),('k','l'),('k','m')]
QUESTIONS={
'4':r'''Is $(S,R)$ a poset if $S$ is the set of all people in the world
and $(a,b)\in R$, where $a$ and $b$ are people, if

a) $a$ is no shorter than $b$?

b) $a$ weighs more than $b$?

c) $a=b$ or $a$ is a descendant of $b$?

d) $a$ and $b$ do not have a common friend?''',
'16':r'''Let $S=\{1,2,3,4\}$. With respect to the lexicographic order based on the usual less than elation,

a) find all pairs in $S\times S$ less than $(2,3)$.

b) find all pairs in $S\times S$ greater than $(3,1)$.

c) draw the Hasse diagram of the poset $(S\times S,\preccurlyeq)$.

原书将“relation”排印为“elation”，此处按原文保留；字典序的含义由题干及本节定义明确。''',
'32':r'''Answer these questions for the partial order represented by this Hasse diagram.

![第32题原书Hasse图，书页663/PDF686](images/9.6-32-original.png)

a) Find the maximal elements.

b) Find the minimal elements.

c) Is there a greatest element?

d) Is there a least element?

e) Find all upper bounds of $\{a,b,c\}$.

f) Find the least upper bound of $\{a,b,c\}$, if it exists.

g) Find all lower bounds of $\{f,g,h\}$.

h) Find the greatest lower bound of $\{f,g,h\}$, if it exists.''',
'44':r'''Determine whether these posets are lattices.

a) $(\{1,3,6,9,12\},\mid)$

b) $(\{1,5,25,125\},\mid)$

c) $(\mathbb Z,\ge)$

d) $(\mathcal P(S),\supseteq)$, where $\mathcal P(S)$ is the power set of a set $S$'''
}

def sha(data):return hashlib.sha256(data).hexdigest()
def write_new(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=text.encode('utf-8') if isinstance(text,str) else text
    if path.exists():
        if path.read_bytes()!=data:raise FileExistsError(f'Preserving existing/manual file: {path}')
    else:path.write_bytes(data)
def closure(vertices,edges):
    # Independent implementation A: graph search, including zero-length paths.
    successors={v:{v} for v in vertices}
    for start in vertices:
        todo=[start]
        while todo:
            current=todo.pop()
            for a,b in edges:
                if a==current and b not in successors[start]:
                    successors[start].add(b);todo.append(b)
    return {(a,b) for a in vertices for b in successors[a]}
def matrix_closure(vertices,edges):
    # Implementation B: Boolean Warshall, not based on the search result.
    m=[[i==j or (i,j) in edges for j in vertices] for i in vertices]
    for k in range(len(vertices)):
        for i in range(len(vertices)):
            for j in range(len(vertices)):m[i][j]=m[i][j] or (m[i][k] and m[k][j])
    return {(a,b) for i,a in enumerate(vertices) for j,b in enumerate(vertices) if m[i][j]}
def properties(v,r):
    return {'reflexive':all((a,a) in r for a in v),
            'antisymmetric':all(a==b or (b,a) not in r for a,b in r),
            'transitive':all((a,c) in r for a,b in r for x,c in r if x==b)}
def bounds(v,r,subset,upper):
    return {x for x in v if all(((a,x) if upper else (x,a)) in r for a in subset)}
def extremum(v,r,subset,greatest):
    return {x for x in subset if all(((a,x) if greatest else (x,a)) in r for a in subset)}
def verify():
    v=VERTICES;r=closure(v,COVERS);assert r==matrix_closure(v,COVERS)
    assert all(properties(v,r).values())
    actual_covers={(a,b) for a,b in r if a!=b and not any(z not in (a,b) and (a,z) in r and (z,b) in r for z in v)}
    assert actual_covers==set(COVERS)
    maximal={a for a in v if not any((a,b) in r for b in v if b!=a)}
    minimal={a for a in v if not any((b,a) in r for b in v if b!=a)}
    ub=bounds(v,r,'abc',True);lb=bounds(v,r,'fgh',False)
    assert maximal=={'l','m'} and minimal=={'a','b','c'}
    assert not extremum(v,r,v,True) and not extremum(v,r,v,False)
    assert ub=={'k','l','m'} and extremum(v,r,ub,False)=={'k'} and not lb
    assert bounds(v,r,'f',False)=={'c','f'}
    assert bounds(v,r,'h',False)=={'a','b','d','e','h'}
    pairs=list(product(range(1,5),repeat=2));lex={(a,b) for a,b in product(pairs,repeat=2) if a<=b}
    rank=lambda x:4*(x[0]-1)+x[1]
    assert all(((a,b) in lex)==(rank(a)<=rank(b)) for a,b in product(pairs,repeat=2))
    smaller=[x for x in pairs if x<(2,3)];greater=[x for x in pairs if x>(3,1)]
    assert smaller==[(1,1),(1,2),(1,3),(1,4),(2,1),(2,2)]
    assert greater==[(3,2),(3,3),(3,4),(4,1),(4,2),(4,3),(4,4)]
    covers={(a,b) for a,b in lex if a!=b and not any(a<z<b for z in pairs)}
    assert covers==set(zip(pairs,pairs[1:])) and len(covers)==15
    height={0:170,1:170,2:180};hr={(a,b) for a,b in product(height,repeat=2) if height[a]>=height[b]}
    assert properties(list(height),hr)=={'reflexive':True,'antisymmetric':False,'transitive':True}
    wr={(a,b) for a,b in product(height,repeat=2) if height[a]>height[b]}
    assert properties(list(height),wr)=={'reflexive':False,'antisymmetric':True,'transitive':True}
    friends={'a':{'u'},'b':set(),'c':{'u'},'u':{'a','c'}}
    fr={(a,b) for a,b in product(friends,repeat=2) if not friends[a]&friends[b]}
    assert properties(list(friends),fr)=={'reflexive':False,'antisymmetric':False,'transitive':False}
    # All 64 forward-edge DAGs on four generations: ancestry plus equality.
    dag_edges=list(combinations(range(4),2))
    for mask in range(1<<len(dag_edges)):
        dag=[edge for i,edge in enumerate(dag_edges) if mask>>i&1]
        assert all(properties(range(4),closure(range(4),dag)).values())
    finite_a=[1,3,6,9,12];ra={(a,b) for a,b in product(finite_a,repeat=2) if b%a==0}
    assert not bounds(finite_a,ra,[6,9],True)
    chain=[1,5,25,125];rc={(a,b) for a,b in product(chain,repeat=2) if b%a==0}
    for a,b in product(chain,repeat=2):
        assert extremum(chain,rc,bounds(chain,rc,[a,b],True),False)=={max(a,b)}
        assert extremum(chain,rc,bounds(chain,rc,[a,b],False),True)=={min(a,b)}
    integers=list(range(-20,21));ri={(a,b) for a,b in product(integers,repeat=2) if a>=b}
    for a,b in product(integers,repeat=2):
        assert extremum(integers,ri,bounds(integers,ri,[a,b],True),False)=={min(a,b)}
        assert extremum(integers,ri,bounds(integers,ri,[a,b],False),True)=={max(a,b)}
    set_pairs=0
    for n in range(6):
        sets=[frozenset(i for i in range(n) if mask>>i&1) for mask in range(1<<n)]
        rs={(a,b) for a,b in product(sets,repeat=2) if a>=b}
        for a,b in product(sets,repeat=2):
            assert extremum(sets,rs,bounds(sets,rs,[a,b],True),False)=={a&b}
            assert extremum(sets,rs,bounds(sets,rs,[a,b],False),True)=={a|b};set_pairs+=1
    return {'ok':True,'checks':[
        '9.6/4：身高相等反例、严格体重关系及四人无共同好友关系逐项检查；64个四顶点DAG验证后裔加相等关系',
        '9.6/16：16个有序对全部256组比较与秩4(i-1)+j交叉核对；6个较小对、7个较大对、15条覆盖边',
        '9.6/32：原图13顶点15条覆盖边经BFS与Boolean Warshall独立求闭包，反求覆盖边及全部8问',
        f'9.6/44：有限整除反例、16组链元素、1681组逆序整数样例、含空集的{set_pairs}组逆包含幂集样例'],
        'hasse32':{'vertices':v,'coversLowerToUpper':COVERS,'maximal':sorted(maximal),'minimal':sorted(minimal),
                   'upperBoundsABC':sorted(ub),'leastUpperBoundABC':'k','lowerBoundsFGH':sorted(lb)},
        'lex16':{'lessThan23':smaller,'greaterThan31':greater,'chainBottomToTop':pairs},
        'limits':['无限集合及一般S的结论由中文解答中的定义和一般证明给出；有限程序检查不是一般证明。',
                  '第4题后裔采用通常无祖先环的含义；身高相等不代表同一人。第44题所有上下确界均在指定底集和指定序内计算。']}

def prepare():
    assert sha(BOOK.read_bytes())==BOOK_SHA,'Textbook version changed'
    images=BANK/'images';images.mkdir(parents=True,exist_ok=True)
    for n in [685,686,687]:write_new(images/f'pdf-{n:04}.png',(CATALOGUE/'images'/f'pdf-{n:04}.png').read_bytes())
    # Pixel box in the indexed 2105x2600 whole page; retains every vertex label.
    import io
    original=Image.open(images/'pdf-0686.png');assert original.size==(2105,2600)
    buf=io.BytesIO();original.crop((365,1710,620,2135)).save(buf,format='PNG',optimize=True)
    write_new(images/'9.6-32-original.png',buf.getvalue())
    pairs=list(product(range(1,5),repeat=2))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="180" height="620" viewBox="0 0 180 620">',
         '<rect width="180" height="620" fill="white"/>',
         '<path d="M50 25V595" stroke="black" stroke-width="1.5"/>']
    for i,pair in enumerate(reversed(pairs)):
        y=25+38*i
        svg.extend([f'<circle cx="50" cy="{y}" r="3.5" fill="black"/>',
                    f'<text x="68" y="{y+5}" font-family="serif" font-size="17">({pair[0]}, {pair[1]})</text>'])
    svg.append('</svg>');write_new(images/'9.6-16-chain.svg','\n'.join(svg)+'\n')
    exercises=[]
    for number,question in QUESTIONS.items():
        page=PAGES[number]
        content=f'## 9.6 Exercise {number}\n\n来源：Rosen第8版，书页{page-23} / PDF第{page}页。\n\n'+question+'\n'
        write_new(BANK/(number+'.md'),content)
        exercises.append({'key':'9.6/'+number,'file':number+'.md','sha256':sha(content.encode('utf-8')),'reviewed':True,
                          'printedPage':page-23,'pdfPage':page,'subparts':{'4':'a–d','16':'a–c','32':'a–h','44':'a–d'}[number]})
    index={'schema':1,'bookId':'rosen-8','section':'9.6','edition':'Eighth Edition','textbook':str(BOOK),'sha256':BOOK_SHA,
           'generator':'rosen96.py','requiredRefs':REFS,'scope':'第五次偏序作业四题全部小问；原图与逆序上下确界已核验',
           'exercises':exercises,'extraFiles':[{'file':name,'sha256':sha((BANK/name).read_bytes())} for name in ['solutions.md','solutions.typ']],
           'images':[{'file':'images/'+p.name,'sha256':sha(p.read_bytes())} for p in sorted(images.iterdir())],
           'figure32':{'sourcePage':'images/pdf-0686.png','sourceSize':[2105,2600],'cropPixels':[365,1710,620,2135],
                       'coversLowerToUpper':COVERS,'visuallyChecked':True}}
    write_new(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')

def build_reviewed(source_path,out):
    source=json.loads(Path(source_path).read_text(encoding='utf-8'));out=Path(out)
    if source['course']['bookId']!='rosen-8' or source['course']['key']!='离散数学':raise ValueError('Wrong textbook/course binding')
    if source.get('attachments') or source.get('resources'):raise ValueError('Attachments require separate review')
    match=re.fullmatch(r'9\.6\s+Exercises?:\s*(\d+(?:\s*[,，、]\s*\d+)*)\s*',source['requirements'].strip())
    if not match:raise ValueError('Unrecognized or additional requirements; do not guess')
    refs=['9.6/'+str(int(n)) for n in re.findall(r'\d+',match[1])]
    if len(refs)!=len(REFS) or set(refs)!=set(REFS):raise ValueError('Only the complete reviewed group can be reproduced')
    index=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
    assert sha(BOOK.read_bytes())==index['sha256'],'Textbook changed'
    for item in index['exercises']+index['extraFiles']+index['images']:
        assert sha((BANK/item['file']).read_bytes())==item['sha256'],'Material changed; independent review required'
    checks=verify();shutil.copytree(BANK/'images',out/'images')
    intro=f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n布置：{source['assignedAt']}\n\n截止：{source['due']}（北京时间）\n"
    questions=[f"# 题目：{source['title']}\n",intro,'## 云邮真实要求\n\n'+source['requirements']+'\n',
               '附件和资源列表均为空。教材：Kenneth H. Rosen, Discrete Mathematics and Its Applications, Eighth Edition。原题保持英文。\n']
    questions.extend((BANK/(ref.split('/')[1]+'.md')).read_text(encoding='utf-8') for ref in REFS)
    for n in [685,686,687]:questions.append(f'## 原书书页{n-23} / PDF第{n}页\n\n![原书整页](images/pdf-{n:04}.png)\n')
    write_new(out/'题目.md','\n'.join(questions))
    write_new(out/'解答.md',(BANK/'solutions.md').read_text(encoding='utf-8'))
    shutil.copyfile(ROOT/'templates'/'homework.typ',out/'layout.typ')
    header='#import "layout.typ": homework\n#show: homework.with(course: '+json.dumps(source['course']['key'],ensure_ascii=False)+', assignment: '+json.dumps(source['title'],ensure_ascii=False)+', assigned: '+json.dumps(source['assignedAt'],ensure_ascii=False)+', due: '+json.dumps(source['due'],ensure_ascii=False)+')\n\n'
    write_new(out/'解答.typ',header+(BANK/'solutions.typ').read_text(encoding='utf-8'))
    records=['# 核对记录\n',intro,'状态：原题逐字与三张原页视觉核对，所有小问、一般推理和辅助计算已核验；仅本地学习材料，未向云邮提交。\n',
             '## 来源和完整性\n',f"教材SHA-256：`{BOOK_SHA}`。书页+23=PDF页；真实正文为9.6 Exercises: 4, 16, 32, 44，无额外要求或附件。\n",
             '|题号|书页/PDF页|全部小问|\n|---|---|---|\n|9.6/4|662/685|a–d；人而非身高数值为底集|\n|9.6/16|662/685|a–c；完整16顶点Hasse链|\n|9.6/32|663/686|a–h；原书13顶点15边图|\n|9.6/44|664/687|a–d；整数≥、幂集⊇均为逆序|\n',
             '## 独立推理复核\n',
             '- 4(a)双向等高只能推出身高相等，不能推出两人相同；(b)严格大于不自反；(c)后裔关系的无环性保证反对称，串接世代保证传递；(d)只要有朋友即不自反，另给四人对称友谊图反例，不假设具体真人关系。\n',
             '- 16的字典序等价于秩4(i−1)+j的通常顺序，覆盖边只连接相邻秩。原题“elation”为排印缺r，原文保留并注记，不误改为分量序。\n',
             '- 32原图逐边读取，下到上覆盖边：'+', '.join(a+'→'+b for a,b in COVERS)+'。确认b→d、d→h存在，f→h不存在；顶点i、j、l分别存在。闭包采用两种独立算法，并反求覆盖关系与原图对照。\n',
             '- 32上界k、l、m中k最小；f的下集{c,f}与h的下集{a,b,d,e,h}不交，故f、g、h根本没有公共下界，不能把c当下确界。极大与最大、极小与最小分别核对。\n',
             '- 44(a)不能把不在底集内的18作为上确界；(c)逆数值序交换min/max；(d)逆包含序交换交/并，按任意集合S证明，并检查S为空的边界。格不要求有全局最大/最小元素。\n',
             '## 程序辅助检查\n']+['- '+s+'\n' for s in checks['checks']]+['\n## 验证边界\n']+['- '+s+'\n' for s in checks['limits']]+[
             '\n## 图片与排版\n','第32题原图直接由原页像素框[365,1710,620,2135]裁取，未重绘连线；整页另存。第16题为新绘解答图，与原题来源分开。原生Typst保留完整原题、中文过程和结论，所有页需渲染视觉核对后记录pdf-visual-reviews.json。\n',
             '\n## 归档与重跑\n','使用archive()和publishPdf()统一归档与集中输出。第9.6节独立指纹，不更改9.3/9.4/9.5及其他课程材料。相同来源/材料跳过，人工修改保留，更新另存revisions。\n']
    write_new(out/'核对记录.md','\n'.join(records));write_new(out/'verification.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--verify',action='store_true');parser.add_argument('--source');parser.add_argument('--out');args=parser.parse_args()
    if args.prepare:prepare();print(json.dumps({'ok':True,'prepared':REFS}))
    elif args.verify:print(json.dumps(verify(),ensure_ascii=True,indent=2))
    elif args.source and args.out:build_reviewed(args.source,args.out);print(json.dumps({'ok':True}))
    else:parser.error('choose --prepare, --verify, or --source FILE --out DIR')
