"""Return only the requested exercise image paths, without loading the book into a model."""
import argparse
import json
import sys
from pathlib import Path

CATALOGUE=Path(__file__).resolve().parents[1]/'题库'/'页面索引'

def lookup(book,keys,context=False):
    directory=CATALOGUE/book
    index=json.loads((directory/'index.json').read_text(encoding='utf-8'))
    records={q['key']:q for q in index['questions']+index.get('thinkingQuestions',[])}
    missing=[k for k in keys if k not in records]
    if missing:raise KeyError('Unknown exercise key(s): '+', '.join(missing))
    pending=list(keys);found=[];seen=set()
    while pending:
        key=pending.pop(0)
        if key in seen:continue
        seen.add(key);q=dict(records[key]);found.append(q)
        pending.extend(q.get('dependencies',[]))
    image_paths=[]
    for q in found:
        ordered=[q['start']['pdfPage']]+q['pdfPages']+q.get('contextPdfPages',[])
        for page in ordered:
            path=str(directory/'images'/f'pdf-{page:04}.png')
            if path not in image_paths:image_paths.append(path)
        q['absoluteImages']=[str(directory/p) for p in q['images']]
    result={'bookId':book,'title':index['title'],'edition':index['edition'],'requested':keys,
            'questions':found,'imagesToRead':image_paths,
            'notice':'截图定位不代表已转录或已作答。先读题目起始页，再读关联页；保留所有小问、共享说明与图。'}
    if context:
        sections={q['section'] for q in found}
        result['contextImages']=list(dict.fromkeys(str(directory/p) for g in index['groups']+index.get('thinkingGroups',[]) if g['key'] in sections for p in g['images']))
    for path in image_paths:
        if not Path(path).is_file():raise FileNotFoundError(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--book',choices=['rosen-8','kolman-6','digital-logic-7','probability-bupt-2021','computer-organization-7'],required=True)
    parser.add_argument('--question',action='append',default=[],help='Repeatable: 9.4/28 or 2/7')
    parser.add_argument('--context',action='store_true',help='Also list section context pages for shared instructions')
    parser.add_argument('--list',action='store_true',help='List groups/counts only')
    args=parser.parse_args()
    if args.list:
        index=json.loads((CATALOGUE/args.book/'index.json').read_text(encoding='utf-8'))
        result={'bookId':args.book,'questionCount':index['questionCount'],
                'thinkingQuestionCount':index.get('thinkingQuestionCount',0),
                'groups':[{k:g[k] for k in ['key','title','questionCount']} for g in index['groups']+index.get('thinkingGroups',[])]}
    else:
        if not args.question:parser.error('provide --question or --list')
        result=lookup(args.book,args.question,args.context)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    try:main()
    except (KeyError,FileNotFoundError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));sys.exit(2)
