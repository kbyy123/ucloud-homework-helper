"""Visually audited chapter 9 question-to-page index; no answer-coverage claim."""
import argparse,hashlib,json,sys
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[1]
BOOK=next((ROOT.parent/'26fa-离散数学（下）').glob('Discrete mathematical structures sixth edition*.pdf'))
SHA='9e95e1abd601348e39696917e4cf1fa9252b51ffc0aa2d23bdb469b9ea48fe48'
OUT=ROOT/'题库'/'页面索引'/'kolman-6'
GROUPS=[('9.1','Binary Operations Revisited',345,349,[(1,32,348),(33,34,349)]),
        ('9.2','Semigroups',349,355,[(1,2,354),(3,36,355)]),
        ('9.3','Products and Quotients of Semigroups',356,362,[(1,28,361),(29,30,362)]),
        ('9.4','Groups',362,372,[(1,30,371),(31,39,372)]),
        ('9.5','Products and Quotients of Groups',372,377,[(1,36,376),(37,38,377)]),
        ('9.6','Other Mathematical Structures',377,382,[(1,18,381),(19,29,382)])]
def sha(data):return hashlib.sha256(data).hexdigest()
def keep(file,text):
 file.parent.mkdir(parents=True,exist_ok=True);data=text.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserve modified index: '+str(file))
 else:file.write_bytes(data)
def build():
 assert sha(BOOK.read_bytes())==SHA,'Textbook version changed'
 image_dir=OUT/'images';image_dir.mkdir(parents=True,exist_ok=True)
 doc=pdfium.PdfDocument(str(BOOK));images=[]
 for pdf in [1,5,24,25]+list(range(369,411)):
  file=image_dir/f'pdf-{pdf:04}.png'
  if not file.exists():
   page=doc[pdf-1];bitmap=page.render(scale=2600/max(page.get_size()))
   bitmap.to_pil().save(file,optimize=True);bitmap.close();page.close()
  images.append({'file':'images/'+file.name,'pdfPage':pdf,'printedPage':pdf-25 if pdf>=369 else None,'sha256':sha(file.read_bytes())})
 doc.close()
 questions=[];groups=[]
 def add(group,number,printed,kind='exercises'):
  pages=[printed]
  if group=='9.5' and number==36:pages=[376,377]
  if group=='9-experiment':pages=[384,385] # shared five-group definitions and tables
  context=[347] if group=='9.1' and number==32 else []
  questions.append({'key':f'{group}/{number}','section':group,'number':number,'kind':kind,
   'start':{'pdfPage':printed+25,'y':None},'printedPages':pages,'pdfPages':[p+25 for p in pages],
   'images':[f'images/pdf-{p+25:04}.png' for p in pages],
   'contextPdfPages':[p+25 for p in context],
   'imageIndexed':True,'transcribed':False,'dependencies':[],
   'notice':'页码与题号范围已视觉核对；原页保留所有小问、共享题干和题图。截图索引不表示答案核验；引用其他题、定义或定理时按context回查。'})
 for key,title,start,end,ranges in GROUPS:
  for lo,hi,page in ranges:
   for number in range(lo,hi+1):add(key,number,page)
  groups.append({'key':key,'title':title,'questionCount':sum(hi-lo+1 for lo,hi,_ in ranges),
                 'printedPages':list(range(start,end+1)),'images':[f'images/pdf-{p+25:04}.png' for p in range(start,end+1)]})
 assert len(questions)==206
 for number in range(1,18):add('9-self-test',number,383 if number<=10 else 384,'self-test')
 for number in range(1,8):add('9-experiment',number,384 if number<=2 else 385,'experiment')
 groups.extend([{'key':'9-self-test','title':'Chapter 9 Self-Test','questionCount':17,'printedPages':[382,383,384],
                 'images':[f'images/pdf-{p+25:04}.png' for p in [382,383,384]]},
                {'key':'9-experiment','title':'Experiment 9','questionCount':7,'printedPages':[384,385],
                 'images':[f'images/pdf-{p+25:04}.png' for p in [384,385]]}])
 index={'schema':1,'bookId':'kolman-6','title':'Discrete Mathematical Structures','authors':['Bernard Kolman','Robert C. Busby','Sharon Cutler Ross'],
        'edition':'Sixth Edition；高等教育出版社2010年11月第1版英文影印本','isbn':'978-7-04-031045-0',
        'originalIsbn':'9780132297516','textbook':str(BOOK),'sha256':SHA,'pdfPageCount':567,'printedToPdfOffset':25,
        'scope':'Chapter 9 Semigroups and Groups，9.1—9.6全部206道节后习题；另含17道自测、7项实验及完整定义/图表页。第11章Groups and Coding不计入本章索引。',
        'questionCount':len(questions),'exerciseCount':206,'selfTestCount':17,'experimentCount':7,
        'groups':groups,'questions':questions,'images':images,'imageIndexed':True,'answersVerified':False}
 keep(OUT/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')
 lines=['# Kolman第六版：第9章半群与群截图索引\n',
        '教材：Discrete Mathematical Structures, Sixth Edition；Kolman / Busby / Ross。高教社2010英文影印版，ISBN 978-7-04-031045-0。\n',
        f'PDF：`{BOOK}`\n\n教材SHA256：`{SHA}`。本章书页344—385，对应PDF369—410，书页+25=PDF页。\n',
        '9.1—9.6共206道节后题，另有17道章自测、7项实验，共230个题号入口。图片共46页，含版本、目录及本章42个完整页面。截图覆盖不表示已解答或答案已验证。第11章“群与编码”属于后续应用，未混入本章。\n',
        '查询：`scripts/lookup-exercise.py --book kolman-6 --question 9.1/32`；加`--context`返回所在节的定义、定理与图表。9.1/32自动附带Example 16原页；9.5/36保留跨页(b)；实验题均附共享五群定义及表。\n',
        '|题号|书页|PDF页|原书截图|\n|---|---|---|---|']
 for q in questions:lines.append('|'+q['key']+'|'+','.join(map(str,q['printedPages']))+'|'+','.join(map(str,q['pdfPages']))+'|'+'、'.join(f'[PDF{p}](images/pdf-{p:04}.png)' for p in q['pdfPages'])+'|')
 keep(OUT/'index.md','\n'.join(lines)+'\n')
 keys={q['key'] for q in questions};assert len(keys)==230
 for group in groups:
  assert [q['number'] for q in questions if q['section']==group['key']]==list(range(1,group['questionCount']+1))
 for q in questions:
  assert q['start']['pdfPage'] in q['pdfPages']
  assert q['pdfPages']==[p+25 for p in q['printedPages']]
  assert all((OUT/f'images/pdf-{p:04}.png').exists() for p in q['pdfPages']+q['contextPdfPages'])
 for item in images:
  with Image.open(OUT/item['file']) as im:
   im.load();assert max(im.size)==2600
   assert ImageStat.Stat(im.convert('L')).stddev[0]>10,'Blank image'
 keep(OUT/'verification.json',json.dumps({'schema':1,'bookId':'kolman-6','ok':True,'sourceSha256':SHA,'exerciseCount':206,
  'selfTestCount':17,'experimentCount':7,'questionCount':230,'imageCount':46,
  'checks':['全部题号唯一且各节连续','全部图片路径、PNG解码、尺寸、非空白与教材SHA核验','书页+25=PDF页及9.5/36跨页小问保留',
            '9.1/32附Example16；章自测和实验共享定义页保留','题号起止与跨页边界已逐页视觉核对，未声称全题逐字转录或作答'],
  'images':images},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'ok':True,'bookId':'kolman-6','exerciseCount':206,'totalQuestions':230,'images':len(images)}))
if __name__=='__main__':build()
