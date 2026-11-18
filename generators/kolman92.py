"""Reproduce the source-verified seventh assignment: Kolman 6e, 9.2/16,20,30."""
import argparse
import base64
import hashlib
import json
import re
import shutil
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / '题库/kolman-6/9.2'
CAT = ROOT / '题库/页面索引/kolman-6'
CAPTURE = ROOT / '.inbox/2121152547941277697/e1e53bbf97a29c43dc18445990fdf93dec92efcfbc841f376a72fbbaf7007a5a'
SHA = '9e95e1abd601348e39696917e4cf1fa9252b51ffc0aa2d23bdb469b9ea48fe48'
REFS = ['9.2/16', '9.2/20', '9.2/30']
GIVENS = [2, 3, 0, 1, None, 0, 1, None, None, None, 2, None, 1, None, 3, 0]
COMPLETE = [2, 3, 0, 1, 3, 0, 1, 2, 0, 1, 2, 3, 1, 2, 3, 0]
QUESTIONS = {
    '16': r'''In Exercises 4 through 16, determine whether the set together with the binary operation is a semigroup, a monoid, or neither. If it is a monoid, specify the identity. If it is a semigroup or a monoid, determine if it is commutative.

16. The set of integers of the form $3k+1,k\in\mathbb Z^+$, where $*$ is ordinary multiplication.

教师另要求：给出具体判断依据。''',
    '20': r'''20. Complete the following table so that it defines a monoid.

| $*$ | $a$ | $b$ | $c$ | $d$ |
|---|---|---|---|---|
| $a$ | $c$ | $d$ | $a$ | $b$ |
| $b$ |  | $a$ | $b$ |  |
| $c$ |  |  | $c$ |  |
| $d$ | $b$ |  | $d$ | $a$ |

空格为原题待填项，行元素为左操作数、列元素为右操作数。''',
    '30': r'''30. An element $x$ in a monoid is called an **idempotent** if $x^2=x*x=x$. Show that the set of all idempotents in a commutative monoid $S$ is a submonoid of $S$.'''
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def keep(file, data):
    file.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode('utf8')
    if file.exists():
        if file.read_bytes() != data:
            raise FileExistsError('Preserve existing file: ' + str(file))
    else:
        with file.open('xb') as target:
            target.write(data)


def identities(table, n):
    return [e for e in range(n)
            if all(table[e*n+x] == x == table[x*n+e] for x in range(n))]


def associative(table, n):
    return all(table[table[x*n+y]*n+z] == table[x*n+table[y*n+z]]
               for x, y, z in product(range(n), repeat=3))


def verify():
    # Integer arithmetic verifies the symbolic closure certificate on samples.
    for m, n in product(range(1, 101), repeat=2):
        value = (3*m+1)*(3*n+1)
        k = 3*m*n+m+n
        assert k >= 1 and value == 3*k+1 and value % 3 == 1
    assert (1-1)//3 == 0 and 4 > 1
    # Exhaust every completion of the six original blanks, testing the monoid
    # definition directly, without assuming commutativity or the derived table.
    blanks = [i for i, value in enumerate(GIVENS) if value is None]
    assert len(blanks) == 6
    solutions = []
    for values in product(range(4), repeat=len(blanks)):
        table = GIVENS[:]
        for i, value in zip(blanks, values):
            table[i] = value
        if identities(table, 4) and associative(table, 4):
            solutions.append(table)
    assert solutions == [COMPLETE]
    assert identities(COMPLETE, 4) == [2]
    labels = [2, 1, 0, 3]  # a,b,c,d -> residues modulo 4
    assert all(labels[COMPLETE[x*4+y]] == (labels[x]+labels[y]) % 4
               for x, y in product(range(4), repeat=2))
    assert all(COMPLETE[x*4+y] == COMPLETE[y*4+x] for x, y in product(range(4), repeat=2))
    # Exhaust all operations on 1,2,3 labelled elements. For each commutative
    # monoid, independently identify its idempotents and check submonoid axioms.
    counts = {}
    tested = 0
    for n in range(1, 4):
        count = 0
        for table in product(range(n), repeat=n*n):
            tested += 1
            es = identities(table, n)
            if not es or not all(table[x*n+y] == table[y*n+x] for x, y in product(range(n), repeat=2)):
                continue
            if not associative(table, n):
                continue
            count += 1
            assert len(es) == 1
            e = es[0]
            idem = {x for x in range(n) if table[x*n+x] == x}
            assert e in idem
            assert all(table[x*n+y] in idem for x, y in product(idem, repeat=2))
            assert all(table[e*n+x] == x == table[x*n+e] for x in idem)
            assert all(table[table[x*n+y]*n+z] == table[x*n+table[y*n+z]]
                       for x, y, z in product(idem, repeat=3))
        counts[n] = count
    assert tested == 19700
    return {'ok': True, 'refs': REFS, 'checks': [
        '9.2/16：10000组正整数参数乘积核对封闭表达式；k≥1且最小元素4，单位元候选1对应k=0。',
        '9.2/20：六空共4096张候选表逐张按单位元及64组三元组检查，唯一解为归档完整表，单位元c；16个有序对均与模4加法对应。',
        f'9.2/30：穷举1、2、3元素集的全部{tested}个运算表；筛出的交换幺半群均检查幂等元集合含原单位元、封闭及继承结合律。'],
        'completionCandidates': 4096, 'completionSolutions': 1,
        'completedTable': [COMPLETE[i:i+4] for i in range(0, 16, 4)],
        'identity': 'c', 'commutativeMonoidCounts': counts,
        'proofReview': [
            '第16题非空、封闭、结合、单位元和交换性逐项判断；正整数参数从1开始。',
            '第20题先由单位元及结合律强制确定填法，再用模4加法证明该填法确实成立。',
            '第30题的一般证明先用e*e=e确保非空和包含原单位元，再用交换律与结合律证明乘积仍幂等。']}


def prepare():
    old = json.loads((ROOT / '题库/kolman-6/9.1/index.json').read_text('utf8'))
    book = Path(old['textbook'])
    assert digest(book.read_bytes()) == SHA
    images = []
    for page in [1, 5, 24, 374, 375, 380]:
        name = f'images/pdf-{page:04}.png'
        data = (CAT / name).read_bytes()
        keep(BANK / name, data)
        images.append({'file': name, 'sha256': digest(data)})
    source = json.loads((CAPTURE / 'source.json').read_text('utf8'))
    raw = re.findall(r'<img\b[^>]*src="data:image/png;base64,([A-Za-z0-9+/=]+)"', source['html'])
    assert len(raw) == 1
    data = base64.b64decode(raw[0])
    assert digest(data) == 'd3919d3744f2ec3c1c3cfa6fcb03580fb89b5c8dcc99d43df48a1fba1c798917'
    name = 'images/inline-01.png'
    keep(BANK / name, data)
    images.append({'file': name, 'sha256': digest(data)})
    keep(BANK / 'source-reference.json', (CAPTURE / 'source.json').read_bytes())
    exercises = []
    for number, text in QUESTIONS.items():
        text = f'## 9.2 Exercise {number}\n\n来源：Kolman第六版，书页355 / PDF380。\n\n' + text + '\n'
        name = number + '.md'
        keep(BANK / name, text)
        exercises.append({'key': '9.2/' + number, 'file': name, 'sha256': digest(text.encode('utf8')),
                          'reviewed': True, 'printedPage': 355, 'pdfPage': 380,
                          'dependencies': ['images/pdf-0374.png', 'images/pdf-0375.png']})
    keep(BANK / 'index.json', json.dumps({
        'schema': 1, 'bookId': 'kolman-6', 'section': '9.2', 'edition': 'Sixth Edition',
        'isbn': '978-7-04-031045-0', 'textbook': str(book), 'sha256': SHA,
        'generator': 'kolman92.py', 'requiredRefs': REFS, 'exercises': exercises, 'images': images,
        'inlineImageHashes': [images[-1]['sha256']],
        'extraFiles': [{'file': name, 'sha256': digest((BANK / name).read_bytes())}
                       for name in ['solutions.typ', 'solutions.md', 'source-reference.json']],
        'scope': '第七次完整16、20、30三题；按第六版分支；保留正整数公式、六空原表和全部判断要求。'
    }, ensure_ascii=False, indent=2) + '\n')


def build(source_file, out):
    source = json.loads(Path(source_file).read_text('utf8'))
    baseline = json.loads((BANK / 'source-reference.json').read_text('utf8'))
    assert source['course'] == baseline['course'] and source['chapter'] == 'Group Theory'
    assert source['html'] == baseline['html'] and source['requirements'] == baseline['requirements']
    assert not source['resources'] and not source['attachments']
    index = json.loads((BANK / 'index.json').read_text('utf8'))
    assert digest(Path(index['textbook']).read_bytes()) == SHA
    for item in index['exercises'] + index['extraFiles'] + index['images']:
        assert digest((BANK / item['file']).read_bytes()) == item['sha256']
    checks = verify()
    out = Path(out)
    shutil.copytree(BANK / 'images', out / 'images')
    intro = (f"课程：{source['course']['name']}；待办ID：{source['id']}。\n\n"
             f"北京时间{source['assignedAt']}布置，{source['due']}截止。\n\n"
             f"教材：Kolman/Busby/Ross第六版，高教社2010英文影印版，ISBN978-7-04-031045-0。"
             f"教材SHA256：{SHA}。书页+25=PDF页。\n")
    questions = ['# ' + source['title'] + '原题\n', intro, '## 平台真实正文\n\n' + source['requirements'],
                 '\n正文公式：![3k+1，k属于正整数](images/inline-01.png)\n',
                 '采用Sixth Edition分支9.2/16、20、30；Fourth Edition的18、26及下方第16题为替代版本材料。第六版第16题与内嵌公式一致。\n']
    questions += [(BANK / (number + '.md')).read_text('utf8') for number in QUESTIONS]
    questions += ['\n## 原书及依赖\n'] + [f'![原书PDF第{p}页](images/pdf-{p:04}.png)\n' for p in [380, 374, 375, 1, 5, 24]]
    keep(out / '题目.md', '\n'.join(questions))
    keep(out / '解答.md', (BANK / 'solutions.md').read_bytes())
    shutil.copyfile(ROOT / 'templates/homework.typ', out / 'layout.typ')
    header = '#import "layout.typ": homework\n#show: homework.with(course: "离散数学", assignment: "第七次作业：半群", assigned: '
    header += json.dumps(source['assignedAt']) + ', due: ' + json.dumps(source['due']) + ')\n\n'
    keep(out / '解答.typ', header + (BANK / 'solutions.typ').read_text('utf8'))
    record = '# 核对记录\n\n' + intro
    record += '\n## 来源与完整性\n\n本人课程活动关联及Group Theory章节由只读入口核实；正文、内嵌公式与空附件列表核对。采用用户提供第六版的16、20、30三题；英文原题及共享要求完整。教师对16题要求给具体依据，已逐项给出。\n\n'
    record += '书页355/PDF380为三题原页，第20题10个已知格与6空逐格核对。书页349/PDF374定义半群，书页350/PDF375定义单位元、幺半群和子幺半群，且Example9明确正整数加法没有单位元，正整数从1开始。内嵌公式与第16题一致。\n\n'
    record += '## 一般推理复核\n\n' + '\n'.join('- ' + s for s in checks['proofReview'])
    record += '\n\n## 程序独立核对\n\n' + '\n'.join('- ' + s for s in checks['checks'])
    record += '\n\n原生Typst、模板、源截图及内嵌公式随作业归档；正式PDF的逐页核对记录关联pdf-visual-reviews.json。日期取真实assignmentBeginTime。\n'
    keep(out / '核对记录.md', record)
    keep(out / 'verification.json', json.dumps(checks, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--source')
    parser.add_argument('--out')
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify(), ensure_ascii=True, indent=2))
    elif args.prepare:
        verify()
        prepare()
        print(json.dumps({'ok': True, 'refs': REFS}))
    elif args.source and args.out:
        build(args.source, args.out)
    else:
        parser.error('choose --verify, --prepare or --source FILE --out DIR')
