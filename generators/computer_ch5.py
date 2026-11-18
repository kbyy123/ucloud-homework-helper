"""Build the source-checked Chapter 5 homework without modifying the bank."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BANK = ROOT / '题库' / 'computer-organization-7' / '5'
REFS = ['5/3', '5/6', '5/8', '5/16']
REQUIREMENTS = '第五章课后习题：3、6、8、16。'
COURSE_KEY = '计算机组成原理与体系结构'
COURSE_IDS = {'2091774261634650117', '2091774263081684995'}


def verify():
    # Reconstruct the on/off sets from the transcribed source table itself.
    table = (BANK / 'questions' / '5-8.md').read_text(encoding='utf-8')
    rows = [line.split('|')[2:-1] for line in table.splitlines() if line.startswith('| I')]
    assert len(rows) == 8 and all(len(row) == 10 for row in rows)
    expected = [
        set('abcde'), set('adfg'), set('bh'), set('c'),
        set('cegi'), set('ahj'), set('cdh'), set('abh'),
    ]
    original = [{c for c, cell in zip('abcdefghij', row) if cell.strip() == '√'} for row in rows]
    assert original == expected
    codes = ('11100101', '10101010', '00000111', '01000000',
             '01011001', '10001111', '01100011', '10000111')
    for code, signals in zip(codes, original):
        direct = {c for c, bit in zip('acdi', code[:4]) if bit == '1'}
        decoded = direct | set(('', 'b', 'g', 'j')[int(code[4:6], 2)])
        decoded |= set(('', 'e', 'f', 'h')[int(code[6:8], 2)])
        assert decoded == signals
    assert all(len(code) == 8 for code in codes) and len(set(codes)) == 8

    unique_words = 1 + sum(1 for _ in range(80) for _ in range(3))
    assert (unique_words, unique_words * 32, unique_words * 4) == (241, 7712, 964)
    assert ((unique_words - 1).bit_length(), 256 - unique_words) == (8, 15)

    accesses = [
        ({'M(A)'}, {'R1'}, {'R2', 'R1'}, {'R2'}),
        ({'R3', 'R4'}, {'R3'}, {'R4', 'R5'}, {'R4'}),
        ({'M(B)'}, {'R6'}, {'R6', 'R7'}, {'R6'}),
    ]
    hazards = [(wi & rj, ri & wj, wi & wj) for ri, wi, rj, wj in accesses]
    assert hazards == [({'R1'}, set(), set()), (set(), {'R4'}, set()),
                       ({'R6'}, set(), {'R6'})]
    return {
        'ok': True, 'refs': REFS, 'controlWords': list(codes), 'controlStoreBits': 7712,
        'dependencies': [[sorted(regs) for regs in group] for group in hazards],
    }


def build(source_file, out):
    source = json.loads(source_file.read_text(encoding='utf-8'))
    course = source['course']
    if (course['key'], course['name'], course['bookId']) != (
        COURSE_KEY, '计算机组成与体系结构', 'computer-organization-7'
    ) or course['id'] not in COURSE_IDS:
        raise ValueError('Wrong course or textbook')
    if (source['chapter'] != '计组-中央处理器' or source['requirements'] != REQUIREMENTS
            or source['resources'] or source['attachments']):
        raise ValueError('Changed chapter, requirements or attachments')

    index = json.loads((BANK / 'index.json').read_text(encoding='utf-8'))
    if hashlib.sha256(Path(index['textbook']).read_bytes()).hexdigest() != index['sha256']:
        raise ValueError('Textbook changed')
    for entry in index['exercises'] + index['extraFiles'] + index['images']:
        if hashlib.sha256((BANK / entry['file']).read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Verified material changed')
    verified = verify()

    shutil.copytree(BANK / 'images', out / 'images')
    shutil.copyfile(ROOT / 'templates' / 'homework.typ', out / 'layout.typ')
    assigned = datetime.fromisoformat(source['assignedAt']).date().isoformat()
    header = '#import "layout.typ": homework\n#show: homework.with(' + ', '.join(
        f'{key}: {json.dumps(value, ensure_ascii=False)}'
        for key, value in {
            'course': COURSE_KEY, 'assignment': source['title'],
            'assigned': assigned, 'due': source['due'],
        }.items()
    ) + ')\n\n'
    intro = (
        f"课程 {course['name']}，课程 ID `{course['id']}`，待办 ID `{source['id']}`。\n\n"
        f"北京时间 {source['assignedAt']} 布置，{source['due']} 截止。\n\n"
        f"平台正文为「{source['requirements']}」，无附件。\n\n"
        "教材为戴志涛、白中英《计算机组成原理》第七版，科学出版社，2024 年 6 月，"
        "ISBN 978-7-03-078281-6。书页加 11 为 PDF 页。\n"
    )
    questions = [(BANK / exercise['file']).read_text(encoding='utf-8') for exercise in index['exercises']]
    images = '\n\n'.join(
        f"![PDF 第 {entry['pdfPage']} 页，书页 {entry['pdfPage'] - 11}]({entry['file']})"
        for entry in index['images']
    )
    record = (
        '# 核对记录\n\n' + intro + f"\n教材 SHA-256 为 `{index['sha256']}`。\n\n"
        '- 依课程活动 ID 确认归属，正文明确第 5 章第 3、6、8、16 题。对照书页 201–202，保留第 8 题原表和第 16 题三组全部指令。\n'
        '- 第 3 题对照书页 150 图 5.1、154–157 的取指及 LAD 周期、159 的寄存器输出路径，分别核对指存取指、C₂ 送地址、数存读、DR 写回四段数据通路。DBUS 上地址和数据分时。\n'
        '- 第 6 题按 80 份专用微程序和 1 份公共取指分别计数，程序复核有效 241 字和整幂配置 256 字。\n'
        '- 第 8 题按书页 174 的混合表示法划分字段，程序从原题表重建八个信号集合，再逐条译码 8 位码并比较集合，全部一致。\n'
        '- 第 16 题按书页 190 的 RAW、WAR、WAW 定义求读写集交集。程序交叉核对第三组同时存在 RAW 和 WAW。\n'
    )
    artifacts = {
        '题目.md': '# 第三次作业原题\n\n' + intro + '\n' + '\n'.join(questions)
                   + '\n## 原题页与教材依赖\n\n' + images + '\n',
        '解答.md': (BANK / 'solutions.md').read_text(encoding='utf-8'),
        '解答.typ': header + (BANK / 'solutions.typ').read_text(encoding='utf-8'),
        '核对记录.md': record,
        'verification.json': json.dumps(verified, ensure_ascii=False, indent=2) + '\n',
    }
    for name, content in artifacts.items():
        with (out / name).open('x', encoding='utf-8', newline='\n') as target:
            target.write(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.out)
