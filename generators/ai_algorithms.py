"""Reproduce agent-reviewed data-structures materials for an exact source."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BOOK = 'ai-algorithms-2026'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(source_file, out):
    # Match workflow.mjs hash(JSON.stringify(source)), including attachment hashes.
    source = json.loads(source_file.read_text(encoding='utf-8'))
    source_hash = digest(json.dumps(source, ensure_ascii=False, separators=(',', ':')).encode())
    if source['course']['id'] != '2091774261898891268' or source['course']['bookId'] != BOOK:
        raise ValueError('Wrong own course')
    bank = ROOT / '题库' / BOOK / source['id'] / source_hash
    index = json.loads((bank / 'index.json').read_text(encoding='utf-8'))
    if index['sourceHash'] != source_hash or index['assignmentId'] != source['id']:
        raise ValueError('Source or attachments changed')
    review = index['requirementsReview']
    if not review['reviewed'] or not review['allAttachmentsRead']:
        raise ValueError('Assignment requirements not reviewed')
    files = {entry['file']: entry for entry in index['files']}
    required = {'题目.md', '解答.md', '解答.typ', '核对记录.md', 'verification.json'}
    if review['narrationRequired']:
        required.add('讲解文稿.md')
    if not required.issubset(files) or not any(name.endswith('.cpp') for name in files):
        raise ValueError('Missing answers, C++ or narration')
    for name, entry in files.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Material path escapes bank')
        data = (bank / relative).read_bytes()
        if digest(data) != entry['sha256']:
            raise ValueError('Reviewed material changed')
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(data)
    verification = json.loads((out / 'verification.json').read_text(encoding='utf-8'))
    if verification.get('ok') is not True or verification.get('codeCompiled') is not True or verification.get('testCases', 0) <= 0:
        raise ValueError('Code not compiled and tested')
    shutil.copyfile(ROOT / 'templates' / 'homework.typ', out / 'layout.typ')
    inbox = ROOT / '.inbox' / source['id'] / source_hash / 'attachments'
    for entry in source['attachments']:
        name = entry['filename']
        if Path(name).name != name:
            raise ValueError('Unsafe attachment name')
        data = (inbox / name).read_bytes()
        if digest(data) != entry['sha256']:
            raise ValueError('Captured attachment changed')
        (out / 'attachments').mkdir(exist_ok=True)
        with (out / 'attachments' / name).open('xb') as target:
            target.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.out)
