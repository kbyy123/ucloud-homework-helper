"""Build a page-image catalogue; deliberately separate from solved/transcribed questions."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
CATALOGUE=ROOT/'题库'/'页面索引'
ROSEN=ROOT.parent/'26fa-离散数学（下）'/'rosen, kenneth h - discrete mathematics and its applications (mcgraw-hill) - libgen.lc.pdf'
DIGITAL=ROOT.parent/'26fa-数字逻辑与数字系统'/'数字逻辑.pdf'
KINDS={'Exercises':'exercises','Review Questions':'review','Supplementary Exercises':'supplementary',
       'Computer Projects':'computer-projects','Computations and Explorations':'explorations','Writing Projects':'writing-projects'}

def sha(data):return hashlib.sha256(data).hexdigest()

def save_json(file,data):
    file.parent.mkdir(parents=True,exist_ok=True)
    content=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if file.name=='index.json' and file.parent.parent==CATALOGUE:preserve_write(file,content)
    else:file.write_bytes(content)

def preserve_write(file,content):
    """Only replace untouched generated files; human edits stop a rebuild."""
    manifest=file.parent/'.generated-files.json'
    hashes=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    if file.exists():
        actual=sha(file.read_bytes())
        if actual==sha(content) or file.read_text(encoding='utf-8')==content.decode('utf-8'):
            hashes[file.name]=actual
            manifest.write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            return
        if hashes.get(file.name)!=actual:
            raise FileExistsError(f'Preserving existing or manually edited file: {file}')
    file.write_bytes(content);hashes[file.name]=sha(content)
    manifest.write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def character_position(page,tp,index):
    box=tp.get_charbox(index)
    bounds=page.get_bbox()
    return {'x':round(box[0]-bounds[0],2),'y':round(bounds[3]-box[3],2)}

def rosen_inventory():
    reader=PdfReader(ROSEN)
    sections={}
    def walk(items):
        for item in items:
            if isinstance(item,list):walk(item)
            elif re.match(r'^(9|10|11)\.\d+ ',item.title):
                sections[item.title.split(' ')[0]]={'title':item.title,'page':reader.get_destination_page_number(item)+1}
    walk(reader.outline)
    pdf=pdfium.PdfDocument(str(ROSEN));groups=[];active=None;section=None;chapter=None
    page_texts={};warnings=[]
    for number in range(622,871):
        if number in [696,804,870]:
            if active:active['end']={'pdfPage':number,'offset':0,'x':0,'y':0}
            active=None;section=None
        page=pdf[number-1];tp=page.get_textpage()
        # Preserve the PDF character index exactly (ligatures/supplementary characters can
        # make an extracted string's offsets differ from the underlying glyph offsets).
        text=''.join(chr(pdfium.raw.FPDFText_GetUnicode(tp.raw,i) or 0xfffd) for i in range(tp.count_chars()))
        page_texts[number]=text
        events=[]
        for key,meta in sections.items():
            if number==meta['page']:
                match=re.search(r'(?m)^'+re.escape(meta['title'])+r'\s*\r?$',text)
                if not match:raise ValueError(f'Cannot locate section title: {meta}')
                events.append((match.start(),'section',key,match.start()))
        for match in re.finditer(r'(?m)^(Exercises|Review Questions|Supplementary Exercises|Computer Projects|Computations and Explorations|Writing Projects)\s*\r?$',text):
            events.append((match.start(),'group',match[1],match.start()))
        for match in re.finditer(r'(?m)^Key Terms and Results\s*\r?$',text):
            events.append((match.start(),'end',None,match.start()))
        for match in re.finditer(r'(?<![\w\d])(\d{1,3})\.(?!\d)',text):
            if pdfium.raw.FPDFText_GetFontWeight(tp.raw,match.start(1))>=400:
                events.append((match.start(),'question',int(match[1]),match.start(1)))
        for offset,kind,value,charindex in sorted(events,key=lambda e:e[0]):
            pos=character_position(page,tp,charindex)
            loc={'pdfPage':number,'offset':offset,**pos}
            if kind=='end':
                if active:active['end']=loc
                active=None
            elif kind=='section':
                if active:active['end']=loc
                active=None;section=value;chapter=int(section.split('.')[0])
            elif kind=='group':
                if number>=870:continue
                chapter=9 if number<696 else 10 if number<804 else 11
                if active:active['end']=loc
                key=section if value=='Exercises' else f'{chapter}.{KINDS[value]}'
                active={'key':key,'chapter':chapter,'title':sections.get(section,{}).get('title',str(chapter)) if value=='Exercises' else value,
                        'kind':KINDS[value],'start':loc,'questions':[]}
                groups.append(active)
            elif active and number<870:
                expected=len(active['questions'])+1
                if value==expected:
                    active['questions'].append({'number':value,**loc})
                else:
                    # The continuity check makes missed or out-of-order labels reviewable.
                    warnings.append({'group':active['key'],'expected':expected,'candidate':value,**loc})
        tp.close();page.close()
    if active and 'end' not in active:active['end']={'pdfPage':870,'x':0,'y':0,'offset':0}
    pdf.close()
    for group in groups:
        group.setdefault('end',{'pdfPage':870,'offset':0,'x':0,'y':0})
        if not group['questions']:raise ValueError('Empty exercise group: '+group['key'])
    return groups,warnings,page_texts

def render_pages(book,out,pages,max_side=2600):
    pdf=pdfium.PdfDocument(str(book));out.mkdir(parents=True,exist_ok=True)
    baseline=out.parent/'verification.json'
    known=json.loads(baseline.read_text(encoding='utf-8')).get('images',{}) if baseline.exists() else {}
    for i,n in enumerate(sorted(set(pages)),1):
        dest=out/f'pdf-{n:04}.png'
        old=known.get(f'images/{dest.name}')
        if dest.exists() and old and sha(dest.read_bytes())!=old['sha256']:
            raise FileExistsError(f'Preserving modified image: {dest}')
        if not dest.exists():
            page=pdf[n-1];bitmap=page.render(scale=max_side/max(page.get_size()))
            bitmap.to_pil().save(dest,optimize=True)
            bitmap.close();page.close()
        if i%20==0:print(f'Rendered/verified {i} pages',flush=True)
    pdf.close()

def question_pages(question,end):
    first=question['pdfPage'];last=end['pdfPage']
    # Do not append a page when the next question/section begins at its first body line.
    if last>first and end.get('x',0)<290 and end.get('y',0)<72:last-=1
    return list(range(first,max(first,last)+1))

def build_rosen(dry_run=False):
    groups,warnings,texts=rosen_inventory()
    save_json(ROOT/'tmp'/'exercise-index'/'rosen-numbering-diagnostics.json',{'groups':groups,'ignoredCandidates':warnings})
    print(json.dumps({'groups':[{'key':g['key'],'questions':len(g['questions']),'firstPage':g['start']['pdfPage'],'lastQuestionPage':g['questions'][-1]['pdfPage']} for g in groups],
                      'ignoredCandidateCount':len(warnings),'ignoredCandidates':warnings[:15]},ensure_ascii=True),flush=True)
    if dry_run:return
    out=CATALOGUE/'rosen-8';records=[];pages=set();group_records=[]
    support=rosen_support_pages()
    for group in groups:
        context=set()
        for i,q in enumerate(group['questions']):
            end=group['questions'][i+1] if i+1<len(group['questions']) else group['end']
            primary=question_pages(q,end)
            primary=[p for p in primary if p in texts and len(texts[p].strip())>30]
            key=f"{group['key']}/{q['number']}"
            extra=support.get(key,[]);exercise_pages=primary[:]
            primary=sorted(set(primary+extra))
            context.update(primary);pages.update(primary)
            records.append({'key':f"{group['key']}/{q['number']}",'chapter':group['chapter'],'section':group['key'],
                            'number':q['number'],'kind':group['kind'],'pdfPages':primary,'printedPages':[p-23 for p in primary],
                            'images':[f'images/pdf-{p:04}.png' for p in primary],
                            'start':{k:q[k] for k in ['pdfPage','x','y']},'imageIndexed':True,'transcribed':False,
                            'exercisePdfPages':exercise_pages,'supportingPdfPages':extra,
                            'notes':['附所引用课文图、表、例题或定理页'] if extra else [],
                            'reviewStatus':'text-layer numbering and continuous sequence checked; rendered page boundaries sampled'})
        group_records.append({'key':group['key'],'title':group['title'],'kind':group['kind'],'questionCount':len(group['questions']),
                              'pdfPages':sorted(context),'images':[f'images/pdf-{p:04}.png' for p in sorted(context)]})
    render_pages(ROSEN,out/'images',pages)
    index={'schema':1,'bookId':'rosen-8','title':'Discrete Mathematics and Its Applications','edition':'Eighth Edition',
           'source':str(ROSEN),'sourceSha256':sha(ROSEN.read_bytes()),'sourcePdfPageCount':1118,
           'scope':{'chapters':[9,10,11],'names':['关系','图论','树'],'groupTheory':'deferred_by_user; no chapter in this source'},
           'imageCount':len(pages),'questionCount':len(records),'groups':group_records,'questions':records,
           'notes':['This is an image locator, not a solved or fully transcribed question bank.','Read all images for cross-page questions; consult group context pages for shared instructions, figures and referenced exercises.'],
           'warnings':warnings}
    save_json(out/'index.json',index);write_markdown(out,index)
    print(json.dumps({'bookId':index['bookId'],'questions':len(records),'pages':len(pages)},ensure_ascii=True),flush=True)

def rosen_support_pages():
    # References checked against source captions, not guessed from exercise titles.
    result={}
    def add(section,numbers,pages):
        for n in numbers:result.setdefault(f'{section}/{n}',[]).extend(pages)
    add('9.1',[2],[624]);add('9.1',[40],[630])
    add('9.2',[3,5,11,13,16,17],[639]);add('9.2',[4],[637,638,639])
    add('9.2',[6,10],[638]);add('9.2',[12],[641]);add('9.2',[19,28,29],[644]);add('9.2',[30,31],[634])
    add('9.5',[34,52,53],[663]);add('9.5',[57],[662]);add('9.5',[65,66],[668])
    add('9.6',[30],[682]);add('9.6',[53],[675]);add('9.6',[63],[683]);add('9.6',[65],[684])
    add('9.supplementary',[49,50],[125,126])
    add('10.1',range(1,10),[699]);add('10.1',[14],[704]);add('10.1',[18],[700]);add('10.1',[34],[702])
    add('10.2',[11],[710]);add('10.2',[15,16],[701]);add('10.2',range(21,26),[713])
    add('10.3',[25],[697,700,704]);add('10.3',[26],[719,720])
    add('10.4',[9,10],[700,701]);add('10.4',[26,57],[738]);add('10.4',[41],[700])
    add('10.4',[56,57,58,61],[746]);add('10.4',[62],[740])
    add('10.5',[9],[752]);add('10.5',[50],[754])
    add('10.6',[8,9,10],[767]);add('10.6',[11,12,13],[768]);add('10.6',[20,21],[771])
    add('10.supplementary',[55],[768]);add('10.7',[10,11],[777])
    add('10.8',[37],[787]);add('10.8',[46],[383,384])
    add('11.1',[29],[812]);add('11.4',[17,19],[712])
    add('11.5',[20,25],[858]);add('11.5',[21,25],[859])
    return {key:sorted(set(pages)) for key,pages in result.items()}

def write_markdown(out,index):
    scope='、'.join(index['scope'].get('names',[]))
    lines=[f"# {index['title']}：题目到图片索引",'',f"范围：{scope}。共 {index['questionCount']} 个题号，{index['imageCount']} 张整页截图。",'',
           '本索引仅表示题目已定位到图片，不表示题干已完整转录或已有答案。跨页题请读取全部关联图片；引用其他题目或共用说明时，按题号继续查询。','']
    for warning in index.get('ambiguities',[]):
        lines.extend([f"- **{warning['key']} 待核对**：{warning['note']}",''])
    for group in index['groups']:
        lines.extend([f"## {group['key']} — {group['title']}",'',f"题号范围：1–{group['questionCount']}。",'',
                      '| 题号 | 原书页码 | PDF 页码 | 图片 |','|---|---|---|---|'])
        for q in index['questions']:
            if q['section']!=group['key']:continue
            links=' · '.join(f'[第 {p} 页]({img})' for p,img in zip(q['pdfPages'],q['images']))
            note='；'.join(q.get('notes',[]))
            if q.get('dependencies'):note+='；关联题：'+', '.join(q['dependencies'])
            if note:links+='。'+note.lstrip('；')
            lines.append(f"| {q['key']} | {', '.join(map(str,q['printedPages']))} | {', '.join(map(str,q['pdfPages']))} | {links} |")
        lines.append('')
    if index.get('thinkingQuestions'):
        lines.extend(['## 课内思考题','',f"共 {len(index['thinkingQuestions'])} 道。原书未编号，以下编号为按章节和出现顺序建立的定位号，不是原书题号。",'',
                      '| 定位号 | 原书页码 | PDF 页码 | 图片 |','|---|---|---|---|'])
        for q in index['thinkingQuestions']:
            links=' · '.join(f'[第 {p} 页]({img})' for p,img in zip(q['pdfPages'],q['images']))
            lines.append(f"| {q['key']} | {', '.join(map(str,q['printedPages']))} | {', '.join(map(str,q['pdfPages']))} | {links} |")
        lines.append('')
    preserve_write(out/'索引.md', ('\n'.join(lines)+'\n').encode('utf-8'))

def build_digital():
    # Visually checked against every exercise page. Coordinates refer to the
    # 1871 x 2600 rendered page, measured from its top left; they are locators,
    # never cropping boundaries. Keep whole pages to retain all subparts/figures.
    inventory={
        1:('开关理论基础',[(39,1,[1397,1508,1619,1731,1842,1951,2008,2286]),(40,9,[402,568,846,1068,1124,1602])]),
        2:('组合逻辑',[(65,1,[1981]),(66,2,[283,338,1053,1107,1790]),(67,7,[283,394,505,672,727,783,838,894,950,1059,1172,1227,1947])]),
        3:('时序逻辑',[(111,1,[517,990,1102,1752,2163,2218]),(112,7,[577,688,1148,1205,1259,1370,2083,2195,2250]),(113,16,[756,1463,2255,2311])]),
        4:('存储逻辑',[(133,1,[1286,1397,1452,1508,1564,1619,1675,1730,1786,1841,1897,1952,2008,2064,2119])]),
        5:('可编程逻辑',[(168,1,[2193,2249]),(169,3,[338,611,733,788,844,895,955,1010,1066,1120,1177,1233,1288,1344,1400,1455,1510,1566,1677])]),
        6:('数字系统',[(190,1,[2227,2335,2390]),(191,4,[339,450,783,1005,1061,1116,1649,1705,1760,1816,1872,1928,1983,2039,2205])]),
        7:('A/D转换、D/A转换',[(204,1,[451,506,1725]),(205,4,[829,2027,2138]),(206,7,[878,1100])]),
    }
    extras={
        '1/8':([40],'小问延续至下一页'),
        '2/7':([66],'题图 P2.7 位于前一页'),
        '3/5':([112],'题图 P3.5 位于下一页'),
        '3/13':([113],'题图 P3.10 位于下一页'),
        '3/14':([113],'题图 P3.11 位于下一页'),
        '5/1':([134,135],'引用课文例1及图5.2，附对应课文页'),
        '5/2':([169],'末句延续至下一页'),
        '5/9':([164],'引用课文例8及图5.35，附对应课文页'),
        '5/10':([164],'条件同第9题，包含图5.35'),
        '6/3':([191],'题干延续至下一页'),
        '6/14':([192],'共用图 P6.1 位于下一页'),
        '6/15':([192],'共用图 P6.1 位于下一页'),
        '6/16':([192],'共用图 P6.1 位于下一页'),
        '7/3':([205],'共用表 P7.2 位于下一页'),
        '7/5':([206],'题图 P7.4 位于下一页'),
    }
    dependencies={'5/10':['5/9'],'6/7':['6/6'],'6/8':['6/6'],'6/11':['6/10']}
    ambiguities=[{'key':'6/10','note':'原书写“根据题10的条件”，构成自引用；需核对教师说明，未擅自改为题9。'},
                 {'key':'6/11','note':'引用第10题，其条件受第10题自引用歧义影响，作答前需确认。'}]
    records=[];groups=[];all_pages=set()
    for chapter,(title,page_groups) in inventory.items():
        group_pages=set();expected=1
        for page,first,ys in page_groups:
            assert first==expected,(chapter,first,expected)
            for number,y in enumerate(ys,first):
                key=f'{chapter}/{number}';pages={page};notes=[]
                if key in extras:
                    more,note=extras[key];pages.update(more);notes.append(note)
                notes.extend(a['note'] for a in ambiguities if a['key']==key)
                pages=sorted(pages);all_pages.update(pages);group_pages.update(pages)
                records.append({'key':key,'chapter':chapter,'section':str(chapter),'number':number,'kind':'exercises',
                    'pdfPages':pages,'printedPages':[p-8 for p in pages],
                    'images':[f'images/pdf-{p:04}.png' for p in pages],
                    'start':{'pdfPage':page,'x':275,'y':y,'units':'pixels','referenceSize':[1871,2600]},
                    'imageIndexed':True,'transcribed':False,'dependencies':dependencies.get(key,[]),'notes':notes,
                    'reviewStatus':'exercise numbering, cross-page continuation and referenced figures visually checked'})
            expected+=len(ys)
        assert expected-1==[14,19,19,15,21,18,8][chapter-1]
        groups.append({'key':str(chapter),'title':title,'kind':'exercises','questionCount':expected-1,
                       'pdfPages':sorted(group_pages),'images':[f'images/pdf-{p:04}.png' for p in sorted(group_pages)]})
    thinking,thinking_groups=build_digital_thinking()
    all_pages.update(p for q in thinking for p in q['pdfPages'])
    out=CATALOGUE/'digital-logic-7';render_pages(DIGITAL,out/'images',all_pages)
    index={'schema':1,'bookId':'digital-logic-7','title':'数字逻辑','edition':'第七版·立体化教材','editors':['白中英','朱立东'],
           'source':str(DIGITAL),'sourceSha256':sha(DIGITAL.read_bytes()),'sourcePdfPageCount':209,
           'scope':{'chapters':list(inventory),'names':['全书七章章末习题、课内思考题'],'excludes':['课文中的非习题例题（被习题明确引用者已附图）']},
           'imageCount':len(all_pages),'exercisePageCount':17,'supportingPdfPages':[134,135,164],
           'questionCount':len(records),'groups':groups,'questions':records,'ambiguities':ambiguities,
           'thinkingQuestionCount':len(thinking),'thinkingQuestions':thinking,'thinkingGroups':thinking_groups,
           'notes':['整页截图保留全部小问、表格和电路图；按题号只读取所需图片。','原书页码=PDF页码-8，均采用从1开始的页码。'], 'warnings':[]}
    save_json(out/'index.json',index);write_markdown(out,index)
    print(json.dumps({'bookId':index['bookId'],'questions':len(records),'pages':len(all_pages)}),flush=True)

def build_digital_thinking():
    # Unnumbered “思考题”, discovered with local Windows OCR over PDF9–207,
    # then visually checked. Y is the blue label at rendering height1600.
    labels={2:[(50,1445),(51,915),(51,1418),(52,543),(54,944),(55,1298),(59,1449),(61,1177),(62,744),(63,930),(65,562)],
            3:[(71,1139),(84,169),(90,1279),(96,444),(102,921),(105,1255),(106,976)],
            4:[(115,1093),(116,868),(117,442),(126,896),(130,169),(131,1347),(133,169)],
            5:[(135,954),(136,305),(165,368),(167,307)],6:[(171,750)]}
    # Extra pages retain the referenced context rather than copying OCR text.
    support={'2.thinking/9':[61], '3.thinking/1':[69,70], '3.thinking/4':[95],
             '3.thinking/6':[103,104], '4.thinking/2':[115], '4.thinking/3':[116],
             '4.thinking/5':[129], '4.thinking/7':[132], '5.thinking/1':[134]}
    records=[];groups=[]
    for chapter,items in labels.items():
        pages=set()
        for n,(page,y) in enumerate(items,1):
            key=f'{chapter}.thinking/{n}';selected=sorted({page,*support.get(key,[])})
            pages.update(selected)
            records.append({'key':key,'chapter':chapter,'section':f'{chapter}.thinking','number':n,'kind':'thinking',
                'pdfPages':selected,'printedPages':[p-8 for p in selected],
                'images':[f'images/pdf-{p:04}.png' for p in selected],
                'start':{'pdfPage':page,'x':int(170*2600/1600),'y':round(y*2600/1600),'units':'pixels','referenceSize':[1871,2600]},
                'imageIndexed':True,'transcribed':False,'originalNumber':None,
                'notes':['原书无题号；定位号按本章出现顺序编制，不得当作原书题号'],
                'reviewStatus':'local OCR discovery followed by visual check of all 30 labels and prompts'})
        groups.append({'key':f'{chapter}.thinking','title':f'第{chapter}章课内思考题（人工定位号）','kind':'thinking',
                       'questionCount':len(items),'pdfPages':sorted(pages),'images':[f'images/pdf-{p:04}.png' for p in sorted(pages)]})
    assert len(records)==30
    return records,groups

def write_overview():
    books=[]
    for book in ['rosen-8','digital-logic-7']:
        path=CATALOGUE/book/'index.json'
        if path.exists():books.append(json.loads(path.read_text(encoding='utf-8')))
    lines=['# 教材题目图片索引','',
           '按题号定位原书整页图片，保留小问、公式、电路图、图论图形和表格。长边2600像素的无损PNG只保存一次，多道题共享同一页。','',
           '| 教材 | 范围 | 题目记录数 | 图片数 | 索引 |','|---|---|---:|---:|---|']
    for book in books:
        scope='、'.join(book['scope']['names']);id=book['bookId']
        count=str(book['questionCount'])+(f" + {book['thinkingQuestionCount']}思考题" if book.get('thinkingQuestionCount') else '')
        lines.append(f"| {book['title']}（{book['edition']}） | {scope} | {count} | {book['imageCount']} | [打开]({id}/索引.md) |")
    lines.extend(['','群论按用户要求暂缓。Rosen 数量包含各节习题、章末复习题、补充题、计算机项目、探索与写作项目；一个题号下的所有小问共用记录，不拆散计数。',
        '', '## 按题号读取','',
        '使用项目 runtime.json 指定的 Python 运行下面的查询。结果仅返回所选题、依赖题和图片路径；不要把整份索引反复送入模型。','',
        '```powershell',
        "$taskPython = (Get-Content -LiteralPath 'D:\\BUPT\\作业助手\\runtime.json' -Raw | ConvertFrom-Json).python",
        "& $taskPython 'D:\\BUPT\\作业助手\\scripts\\lookup-exercise.py' --book rosen-8 --question '9.4/28'",
        "& $taskPython 'D:\\BUPT\\作业助手\\scripts\\lookup-exercise.py' --book digital-logic-7 --question '2/7'",
        '```','',
        '`--question` 可重复指定；`--list` 只列出章节及数量；`--context` 额外列出所在节的上下文图片，供查找共享说明和间接引用。Rosen 章末题键示例：`10.supplementary/55`。数字逻辑无编号思考题键示例：`2.thinking/1`，是本索引按章内出现顺序编制的定位号。',
        '', '## 核对和维护','',
        '- 每个教材目录内：`index.json` 供程序查询，`索引.md` 供阅读，`images/` 存截图，`verification.json` 存图片校验值和完整性检查结果。',
        '- 页码均从1开始；原书页码和PDF页码同时保留。题目起始坐标仅用于定位，图片不按坐标裁切。',
        '- 已关联跨页题和明确引用的课文图、表、例题。读取时先看题干起始页，再看其余关联页；间接引用或共享说明仍应按原书要求继续核对。',
        '- 数字逻辑6/10存在原书自引用；6/11受其影响，已标记待确认。不得猜测教师意图或擅自修改题号。',
        '- 已做题号连续性、全部图片链接、图片解码/尺寸/非空白、教材指纹及查询验证；Rosen缩略图全面浏览并抽查边界，数字逻辑逐页核对题号与跨页图。这不等于已逐字人工校对全部题干。',
        '- 重建复用图片；生成文件的人工修改会触发保护并停止覆盖。保留人工改动后另存修订，不删除保护清单来强行重建。',
        '', '**页面覆盖与解答覆盖分开记录。** 本轮仅建立题目到图片的索引；现有五题已核验解答仍在原题库中，新作业需要读取原题、作答并核验后才能归档。','',
        '校验命令：','', '```powershell',
        "& $taskPython 'D:\\BUPT\\作业助手\\scripts\\verify-page-index.py'",'```',''])
    preserve_write(CATALOGUE/'README.md','\n'.join(lines).encode('utf-8'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--rosen',action='store_true');parser.add_argument('--digital',action='store_true');parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    if args.rosen:build_rosen(args.dry_run)
    if args.digital:
        if args.dry_run:parser.error('--dry-run currently only supports --rosen')
        build_digital()
    if (args.rosen or args.digital) and not args.dry_run:write_overview()
