"""Reproduce the reviewed fourth probability assignment and its checks."""
import argparse
import hashlib
import json
import math
import re
import shutil
from datetime import datetime
from fractions import Fraction as Q
from itertools import permutations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / '题库' / 'probability-bupt-2021' / 'fourth'
CAT = ROOT / '题库' / '页面索引' / 'probability-bupt-2021'
BOOK = ROOT.parent / '26fa-概率论与随机过程' / '概率论与随机过程.pdf'
SHA = '80662453203acbf11f5c6b4368c649e2437ba07837dd90465d52f4cceec06200'
REFS = ['4/9', '4/14', '4/19', '4/22(2)', '4/26', '4/27', '4/28', '4/34',
        'supplement/bivariate-normal-correlation-v1']
REQ = 'p144-146\n9  14   19  22(2)   26   27  28  34\n\n证明二维正态分布的两个随机分量得相关系数是第五个参数\\rho'
PAGES = {'4/9': [144], '4/14': [144], '4/19': [145], '4/22(2)': [145],
         '4/26': [145], '4/27': [145], '4/28': [146], '4/34': [146],
         REFS[-1]: [75, 128]}
QUESTIONS = {
    '4/9': r'''设随机变量 $(X,Y)$ 的概率密度为
$$f(x,y)=\begin{cases}12y^2,&0\le y\le x\le1,\\0,&\text{其他},\end{cases}$$
求 $E(X),E(Y),E(XY),E(X^2+Y^2)$。''',
    '4/14': r'将 $n$ 封不同的信的 $n$ 张信笺与 $n$ 个信封随机配对，求匹配成对的信数 $X$ 的数学期望和方差。',
    '4/19': r'''设随机变量 $X$ 的概率密度为
$$f(x)=\begin{cases}2x,&0<x<1,\\0,&\text{其他}.\end{cases}$$
（1）求 $P\{|X-E(X)|\ge2\sqrt{D(X)}\}$；
（2）求 $E(1/X)$。''',
    '4/22(2)': r'''（2）设随机变量 $X,Y$ 相互独立，且 $X\sim N(720,30^2),Y\sim N(640,25^2)$，求 $Z_1=2X+Y,Z_2=X-Y$ 的分布，并求 $P\{X>Y\},P\{X+Y>1400\}$。''',
    '4/26': r'''随机变量 $X$ 的概率密度为 $f(x)=\frac12 e^{-|x|}$。
（1）求 $E(X),D(X)$；
（2）求 $X$ 与 $|X|$ 的协方差，并说明 $X$ 与 $|X|$ 是否不相关；
（3）$X$ 与 $|X|$ 是否相互独立，并说明原因。''',
    '4/27': r'''设 $(X,Y)$ 的分布律为

| $Y\backslash X$ | $-1$ | $0$ | $1$ |
|---|---|---|---|
| $-1$ | $1/8$ | $1/8$ | $1/8$ |
| $0$ | $1/8$ | $0$ | $1/8$ |
| $1$ | $1/8$ | $1/8$ | $1/8$ |

求 $X,Y$ 的相关系数，并讨论 $X,Y$ 的独立性。''',
    '4/28': r'''设 $X,Y$ 相互独立，且都服从 $N(\mu,\sigma^2)$，已知 $\xi=\alpha X+\beta Y,\eta=\alpha X-\beta Y$，$\alpha,\beta$ 为常数，求 $\xi$ 与 $\eta$ 的相关系数。''',
    '4/34': r'''设 $X,Y$ 相互独立，且都服从 $N(a,\sigma^2)$，证明：
$$E[\max(X,Y)]=a+\frac{\sigma}{\sqrt\pi},\qquad E[\min(X,Y)]=a-\frac{\sigma}{\sqrt\pi}.$$''',
    REFS[-1]: r'证明二维正态分布的两个随机分量得相关系数是第五个参数 $\rho$。',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(text):
    return re.sub(r'\s+', '', text)


def qfile(ref):
    return 'questions/' + ref.replace('/', '-').replace('(', '-').replace(')', '') + '.md'


def keep(file, data):
    if isinstance(data, str):
        data = data.encode('utf8')
    file.parent.mkdir(parents=True, exist_ok=True)
    if file.exists():
        if file.read_bytes() != data:
            raise FileExistsError(str(file))
    else:
        with file.open('xb') as target:
            target.write(data)


def verify():
    checks = []
    nodes, weights = np.polynomial.legendre.leggauss(128)

    def integrate(fun, left, right):
        x = (nodes + 1) * (right - left) / 2 + left
        return float(np.dot(weights, fun(x)) * (right - left) / 2)

    x = (nodes + 1) / 2
    y = x[:, None] * (nodes[None, :] + 1) / 2
    w = weights[:, None] * weights[None, :] * x[:, None] / 4
    moments = {(0, 0): Q(1), (1, 0): Q(4, 5), (0, 1): Q(3, 5),
               (1, 1): Q(1, 2), (2, 0): Q(2, 3), (0, 2): Q(2, 5)}
    for (a, b), expected in moments.items():
        exact = Q(12, (b + 3) * (a + b + 4))
        numeric = float(np.sum(w * 12 * y ** (b + 2) * x[:, None] ** a))
        assert exact == expected and abs(numeric - float(expected)) < 2e-13
    checks.append('4/9：六个三角形区域积分的有理数结果与128阶二维数值积分一致，二阶矩之和为16/15。')
    matched_permutations = 0
    for n in range(1, 9):
        values = [sum(i + 1 == value for i, value in enumerate(p))
                  for p in permutations(range(1, n + 1))]
        mean = Q(sum(values), len(values))
        variance = Q(sum(value * value for value in values), len(values)) - mean * mean
        assert mean == 1 and variance == (0 if n == 1 else 1)
        matched_permutations += len(values)
    checks.append(f'4/14：穷举n=1至8的{matched_permutations}个配对，期望均为1，n=1方差0，n≥2方差1。')
    mean, variance = Q(2, 3), Q(1, 18)
    low = float(mean) - 2 * math.sqrt(float(variance))
    probability19 = low * low
    assert abs(probability19 - (6 - 4 * math.sqrt(2)) / 9) < 1e-15
    assert abs(integrate(lambda t: 2 * t, 0, low) - probability19) < 1e-14
    assert integrate(lambda t: np.full_like(t, 2.0), 0, 1) == 2
    checks.append('4/19：偏差事件下端点积分得0.038127305612；倒数期望积分为2。')
    phi = lambda z: np.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    Phi = lambda z: (1 + math.erf(z / math.sqrt(2))) / 2
    p_greater = Phi(80 / math.sqrt(1525))
    p_sum = 1 - Phi(40 / math.sqrt(1525))
    assert abs(integrate(phi, -80 / math.sqrt(1525), 10) - p_greater) < 1e-13
    assert abs(integrate(phi, 40 / math.sqrt(1525), 10) - p_sum) < 1e-13
    assert 2 * 720 + 640 == 2080 and 4 * 900 + 625 == 65 ** 2
    checks.append('4/22(2)：线性变换均值、方差直接核算，两个标准正态积分分别为0.979748892209和0.152847970122。')
    assert abs(integrate(lambda t: t ** 2 * np.exp(-t), 0, 50) - 2) < 1e-12
    assert abs(integrate(lambda t: t * np.exp(-t), 0, 50) - 1) < 1e-12
    assert math.exp(-1) / 2 > math.exp(-2) / 2
    checks.append('4/26：Laplace绝对一阶矩1和二阶矩2经数值积分核对；对称奇函数矩为0，独立性事件概率明确不等。')
    table = [[Q(0) if i == j == 1 else Q(1, 8) for j in range(3)] for i in range(3)]
    assert sum(map(sum, table)) == 1
    ex = sum(Q(j - 1) * table[i][j] for i, j in product(range(3), repeat=2))
    ey = sum(Q(i - 1) * table[i][j] for i, j in product(range(3), repeat=2))
    exy = sum(Q((i - 1) * (j - 1)) * table[i][j] for i, j in product(range(3), repeat=2))
    ex2 = sum(Q((j - 1) ** 2) * table[i][j] for i, j in product(range(3), repeat=2))
    assert ex == ey == exy == 0 and ex2 == Q(3, 4)
    assert sum(table[1]) * sum(row[1] for row in table) == Q(1, 16)
    checks.append('4/27：九格分布和为1，均值与混合矩为0，方差3/4；中心格概率0与边缘乘积1/16区分。')
    coefficient_checks = 0
    for a, b in product(range(-2, 3), repeat=2):
        xi = [a * u + b * v for u, v in product([-1, 1], repeat=2)]
        eta = [a * u - b * v for u, v in product([-1, 1], repeat=2)]
        vx = Q(sum(t * t for t in xi), 4)
        cov = Q(sum(u * v for u, v in zip(xi, eta)), 4)
        assert vx == a * a + b * b and cov == a * a - b * b
        coefficient_checks += 1
    checks.append(f'4/28：{coefficient_checks}组系数用独立零均值离散变量核对二阶矩代数，覆盖正、负、零系数。')
    def cdf_array(z):
        return np.array([Phi(float(value)) for value in z])
    maximum_checks = 0
    for a, sigma in product([-3, 0, 2], [.5, 1, 4]):
        maximum = integrate(lambda z: (a + sigma * z) * 2 * phi(z) * cdf_array(z), -10, 10)
        minimum = integrate(lambda z: (a + sigma * z) * 2 * phi(z) * (1 - cdf_array(z)), -10, 10)
        assert abs(maximum - (a + sigma / math.sqrt(math.pi))) < 1e-12
        assert abs(minimum - (a - sigma / math.sqrt(math.pi))) < 1e-12
        maximum_checks += 1
    checks.append(f'4/34：{maximum_checks}组位置和尺度参数，以次序统计量密度数值积分交叉核对最大值、最小值期望。')
    u = 9 * nodes[:, None]
    v = 9 * nodes[None, :]
    ww = 81 * weights[:, None] * weights[None, :]
    gaussian_checks = 0
    for rho in [-.9, -.5, 0, .4, .8, .9]:
        density = np.exp(-(u * u - 2 * rho * u * v + v * v) / (2 * (1 - rho * rho)))
        density /= 2 * math.pi * math.sqrt(1 - rho * rho)
        mass = float(np.sum(ww * density))
        covariance = float(np.sum(ww * density * u * v))
        vx = float(np.sum(ww * density * u * u))
        vy = float(np.sum(ww * density * v * v))
        assert abs(mass - 1) < 2e-12
        assert abs(vx - 1) < 2e-12 and abs(vy - 1) < 2e-12
        assert abs(covariance / math.sqrt(vx * vy) - rho) < 2e-12
        gaussian_checks += 1
    checks.append(f'补充证明：{gaussian_checks}个正负ρ参数的原始二维正态密度直接二维积分，归一化、方差和相关系数一致；一般参数另有完整变量变换证明。')
    return {'ok': True, 'refs': REFS, 'checks': checks, 'matchingPermutations': matched_permutations,
            'p19': probability19, 'p22': [p_greater, p_sum],
            'answers': {'4/9': ['4/5', '3/5', '1/2', '16/15'], '4/14': 'E=1; D=1 (n>=2), D=0 (n=1)',
                        '4/19': ['(6-4*sqrt(2))/9', '2'], '4/22(2)': ['N(2080,65^2)', 'N(80,1525)'],
                        '4/26': ['E=0', 'D=2', 'Cov(X,abs(X))=0', 'dependent'],
                        '4/27': ['correlation=0', 'dependent'], '4/28': '(alpha^2-beta^2)/(alpha^2+beta^2)',
                        '4/34': ['a+sigma/sqrt(pi)', 'a-sigma/sqrt(pi)'], REFS[-1]: 'rho'}}


def prepare():
    assert digest(BOOK.read_bytes()) == SHA
    exercises = []
    for ref in REFS:
        printed = PAGES[ref]
        text = '## ' + ref + '\n\n书页 ' + ','.join(map(str, printed)) + '；PDF页 ' + ','.join(str(p + 11) for p in printed) + '。\n\n'
        text += QUESTIONS[ref] + '\n'
        keep(BANK / qfile(ref), text)
        exercises.append({'key': ref, 'file': qfile(ref), 'sha256': digest(text.encode()),
                          'reviewed': True, 'printedPages': printed, 'pdfPages': [p + 11 for p in printed]})
    images = []
    for n in [1, 3, 86, 139, 155, 156, 157]:
        file = f'images/pdf-{n:04}.png'
        source = CAT / file if n not in [86, 139] else ROOT / 'tmp/pdfs/probability-fourth' / Path(file).name
        keep(BANK / file, source.read_bytes())
        images.append({'file': file, 'sha256': digest(source.read_bytes())})
    extra = [{'file': name, 'sha256': digest((BANK / name).read_bytes())}
             for name in ['solutions.typ', 'solutions.md']]
    keep(BANK / 'index.json', json.dumps({
        'schema': 1, 'bookId': 'probability-bupt-2021', 'assignment': 'fourth',
        'edition': '2021年1月第1版', 'isbn': '978-7-5635-6266-4',
        'textbook': str(BOOK), 'sha256': SHA, 'generator': 'probability_fourth.py',
        'requiredRefs': REFS, 'requirementsCanonical': canonical(REQ),
        'exercises': exercises, 'extraFiles': extra, 'images': images,
        'scope': '第四次完整9项；4/22指定(2)，4/19两问、4/26三问及二维正态补充证明完整。'},
        ensure_ascii=False, indent=2) + '\n')


def build(source_file, out):
    source = json.loads(Path(source_file).read_text(encoding='utf8'))
    out = Path(out)
    if source['course'] != {'key': '概率论与随机过程', 'id': '2091774263564029955',
                            'name': '概率论与随机过程', 'bookId': 'probability-bupt-2021'}:
        raise ValueError('Course binding changed')
    if source['resources'] or source['attachments'] or canonical(source['requirements']) != canonical(REQ):
        raise ValueError('Requirements changed')
    index = json.loads((BANK / 'index.json').read_text(encoding='utf8'))
    assert digest(BOOK.read_bytes()) == SHA
    for item in index['exercises'] + index['extraFiles'] + index['images']:
        assert digest((BANK / item['file']).read_bytes()) == item['sha256']
    verification = verify()
    shutil.copytree(BANK / 'images', out / 'images')
    intro = (f"课程 {source['course']['name']}，待办ID {source['id']}。\n\n"
             f"北京时间 {source['assignedAt']} 布置，{source['due']} 截止。\n\n"
             f"平台正文\n\n{source['requirements']}\n\n"
             f"教材为北邮出版社2021年1月第1版，ISBN978-7-5635-6266-4，SHA-256为{SHA}，书页+11=PDF页。\n")
    questions = ['# 第四次作业原题\n\n', intro]
    questions.extend((BANK / qfile(ref)).read_text(encoding='utf8') for ref in REFS)
    questions.append('\n## 原书页与依赖\n\n补充题原文保留“得”字；证明使用书页75定义3.1.6及书页128相关系数定义。4/22按指定第(2)问作答。\n')
    for n in [155, 156, 157, 86, 139, 1, 3]:
        questions.append(f'\n![原书PDF第{n}页](images/pdf-{n:04}.png)\n')
    keep(out / '题目.md', '\n'.join(questions))
    keep(out / '解答.md', (BANK / 'solutions.md').read_bytes())
    shutil.copyfile(ROOT / 'templates/homework.typ', out / 'layout.typ')
    date = datetime.fromisoformat(source['assignedAt']).date().isoformat()
    header = '#import "layout.typ": homework\n#show: homework.with(course: "概率论与随机过程", assignment: "第四次作业", assigned: '
    header += json.dumps(date) + ', due: ' + json.dumps(source['due']) + ')\n\n'
    keep(out / '解答.typ', header + (BANK / 'solutions.typ').read_text(encoding='utf8'))
    record = '# 核对记录\n\n' + intro + '\n## 来源和完整性\n\n'
    record += ('本人课程活动ID与本轮只读详情核实。书页144/PDF155的9、14题，145/PDF156的19、22(2)、26、27题，'
               '146/PDF157的28、34题逐项核对。4/19两小问、4/26三小问、4/27九格分布及补充证明均完整保留。\n\n'
               '## 推理复核\n\n'
               '- 第9题按三角形支持积分；第14题随机配对采用等可能排列，一般指标变量推导与枚举一致。\n'
               '- 第19题精确化简偏差事件；第22题按独立正态线性组合计算，方差分别4225及1525。\n'
               '- 第26、27题先算协方差，再用事件/格点检验独立性；第28题写明相关系数的正方差条件。\n'
               '- 第34题由最大/最小的绝对值恒等式和正态绝对矩证明。\n'
               '- 补充证明从书页75的密度参数出发，变换为独立标准正态后求协方差，再代入书页128定义；计算链条自洽。\n\n'
               '## 程序核验\n\n')
    record += '\n'.join('- ' + check for check in verification['checks'])
    record += '\n\nTypst及本地模板随作业归档，正式PDF逐页视觉核对结果记录于pdf-visual-reviews.json。\n'
    keep(out / '核对记录.md', record)
    keep(out / 'verification.json', json.dumps(verification, ensure_ascii=False, indent=2) + '\n')


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
