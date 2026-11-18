"""Check catalogue integrity and preserve the initial image checksum baseline."""
import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[1]
CATALOGUE=ROOT/'题库'/'页面索引'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_script(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def verify(book):
    directory=CATALOGUE/book;index=json.loads((directory/'index.json').read_text(encoding='utf-8'))
    assert digest(Path(index['source']))==index['sourceSha256'],'Source PDF changed'
    primary=index['questions'];questions=primary+index.get('thinkingQuestions',[]);keys={q['key'] for q in questions}
    assert len(keys)==len(questions)==index['questionCount']+index.get('thinkingQuestionCount',0)
    assert len(primary)=={'rosen-8':1335,'digital-logic-7':114}[book]
    if book=='digital-logic-7':assert len(index['thinkingQuestions'])==30
    groups=index['groups']+index.get('thinkingGroups',[])
    for group in groups:
        items=[q for q in questions if q['section']==group['key']]
        assert [q['number'] for q in items]==list(range(1,group['questionCount']+1)),group['key']
        assert set(group['pdfPages'])=={p for q in items for p in q['pdfPages']}
    pages=set()
    for q in questions:
        assert q['start']['pdfPage'] in q['pdfPages'],q['key']
        assert q['pdfPages']==sorted(set(q['pdfPages']))
        assert q['printedPages']==[p-({'rosen-8':23,'digital-logic-7':8}[book]) for p in q['pdfPages']]
        assert q['images']==[f'images/pdf-{p:04}.png' for p in q['pdfPages']]
        assert q['imageIndexed'] and not q['transcribed']
        assert all(k in keys for k in q.get('dependencies',[]))
        pages.update(q['pdfPages'])
    assert len(pages)==index['imageCount']
    images={}
    for page in sorted(pages):
        name=f'images/pdf-{page:04}.png';path=directory/name
        with Image.open(path) as image:
            image.load();assert max(image.size)==2600
            assert max(ImageStat.Stat(image.convert('L')).stddev)>10,('Blank screenshot',name)
            images[name]={'sha256':digest(path),'width':image.width,'height':image.height,'pdfPage':page}
    manifest=json.loads((directory/'.generated-files.json').read_text(encoding='utf-8'))
    for name,expected in manifest.items():assert digest(directory/name)==expected,('Edited generated file',name)
    baseline=directory/'verification.json'
    result={'schema':1,'bookId':book,'status':'passed','sourceSha256':index['sourceSha256'],
            'questionCount':len(primary),'thinkingQuestionCount':index.get('thinkingQuestionCount',0),
            'groupCount':len(groups),'imageCount':len(images),
            'checks':['unique and continuous exercise numbers','all image links exist','page-number offsets',
                      'PNG decode, dimensions and nonblank content','source and generated file fingerprints'],
            'visualReview':'Rosen exercise-page contact sheets reviewed; graph/formula and boundary pages sampled. Digital logic exercise numbering and cross-page figures checked on page images.',
            'images':images}
    if baseline.exists():
        old=json.loads(baseline.read_text(encoding='utf-8'))
        assert all(images.get(name)==data for name,data in old['images'].items()),'Existing image checksum changed; preserve edits and review manually'
    builder=load_script('build-page-index')
    builder.preserve_write(baseline,(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    return {k:result[k] for k in ['bookId','status','questionCount','thinkingQuestionCount','groupCount','imageCount']}

def verify_lookup_and_preservation():
    lookup=load_script('lookup-exercise');builder=load_script('build-page-index')
    assert lookup.lookup('rosen-8',['9.4/28'])['questions'][0]['start']['pdfPage']==661
    assert lookup.lookup('rosen-8',['9.3/32'])['questions'][0]['start']['pdfPage']==650
    for book,key,pages in [('digital-logic-7','2/7',{66,67}),('digital-logic-7','5/1',{134,135,168}),
                           ('digital-logic-7','6/14',{191,192}),('digital-logic-7','7/5',{205,206}),
                           ('rosen-8','10.3/25',{697,700,704,734})]:
        assert pages<=set(lookup.lookup(book,[key])['questions'][0]['pdfPages']),(book,key)
    assert len(lookup.lookup('digital-logic-7',['5/10'])['questions'])==2
    assert lookup.lookup('digital-logic-7',['2.thinking/2'])['questions'][0]['start']['pdfPage']==51
    try:lookup.lookup('rosen-8',['9.3/999'])
    except KeyError:pass
    else:raise AssertionError('Unknown question accepted')
    with tempfile.TemporaryDirectory(prefix='homework-index-') as temporary:
        path=Path(temporary)/'sample.md';builder.preserve_write(path,b'generated')
        builder.preserve_write(path,b'generated');path.write_bytes(b'manual edit')
        try:builder.preserve_write(path,b'new generation')
        except FileExistsError:pass
        else:raise AssertionError('Manual edit was not protected')
        assert path.read_bytes()==b'manual edit'

if __name__=='__main__':
    verify_lookup_and_preservation()
    print(json.dumps([verify(book) for book in ['rosen-8','digital-logic-7']],ensure_ascii=True))
