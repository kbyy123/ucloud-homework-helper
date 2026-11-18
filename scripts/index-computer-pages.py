"""Index the ten end-of-chapter exercise sets in the verified 7th edition."""
import hashlib,json,re,sys
from pathlib import Path
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT.parent/'26fa-computer_architecture'/'计算机组成原理.pdf'
DEST=ROOT/'题库'/'页面索引'/'computer-organization-7'
SHA='2ba7dedba8de7135c5a748163c9aed1ac45c455bf2eff28c715f65be868d748c'
SETS=[(21,21,16),(68,69,16),(122,124,30),(147,148,17),(201,202,17),(229,230,21),(254,255,15),(290,291,16),(328,329,9),(346,347,11)]
def keep(file,data):
 file.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,str):data=data.encode('utf-8')
 if file.exists():
  if file.read_bytes()!=data:raise FileExistsError('Preserve existing file: '+str(file))
 else:file.write_bytes(data)
def main():
 assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==SHA
 reader=PdfReader(BOOK);assert len(reader.pages)==409
 document=pdfium.PdfDocument(str(BOOK));questions=[];groups=[];allpages=set()
 for ch,(a,b,total) in enumerate(SETS,1):
  starts=[]
  for printed in range(a,b+1):
   text=reader.pages[printed+10].extract_text()
   for m in re.finditer(r'^\s*(\d+)\s*[.．]\s',text,re.M):starts.append((int(m[1]),printed+11))
  assert [n for n,p in starts]==list(range(1,total+1)),(ch,starts)
  pages=list(range(a+11,b+12));allpages.update(pages)
  groups.append({'key':str(ch),'title':f'第{ch}章章末习题','questionCount':total,'printedPages':list(range(a,b+1)),'pdfPages':pages,'images':[f'images/pdf-{p:04}.png' for p in pages]})
  for i,(n,p) in enumerate(starts):
   # Include a following page up to the next question's start. At a page
   # boundary include the preceding page as context rather than cut a figure.
   end=starts[i+1][1] if i+1<len(starts) else b+11
   related=list(range(max(a+11,p-1),end+1))
   questions.append({'key':f'{ch}/{n}','section':str(ch),'number':n,'kind':'exercises','start':{'pdfPage':p,'y':None},
    'printedPages':[v-11 for v in related],'pdfPages':related,'images':[f'images/pdf-{v:04}.png' for v in related],
    'imageIndexed':True,'transcribed':False,'dependencies':[]})
 # Supporting definitions for the current instruction-system assignment.
 extra=[1,2,3,139,140,141,146,148,149,153,154]
 allpages.update(extra)
 (DEST/'images').mkdir(parents=True,exist_ok=True)
 for n in sorted(allpages):
  target=DEST/'images'/f'pdf-{n:04}.png'
  if not target.exists():
   page=document[n-1];bitmap=page.render(scale=2600/max(page.get_size()));bitmap.to_pil().save(target);bitmap.close();page.close()
 assert len(questions)==168
 idx={'schema':1,'bookId':'computer-organization-7','title':'计算机组成原理','edition':'第七版（2024年6月）',
  'authors':['戴志涛','白中英'],'isbn':'978-7-03-078281-6','source':str(BOOK),'sourceSha256':SHA,
  'sourcePdfPageCount':409,'printedPageOffset':11,'questionCount':168,'imageCount':len(allpages),'groups':groups,'questions':questions,
  'scope':'覆盖第1—10章全部168道章末习题；第11、12章为课程设计，无同类章末习题。只定位截图，不代表已转录或作答。相邻页用于保留跨页小问、表格、题图。',
  'supportingPdfPages':extra,'images':[{'file':f'images/pdf-{n:04}.png','sha256':hashlib.sha256((DEST/'images'/f'pdf-{n:04}.png').read_bytes()).hexdigest()} for n in sorted(allpages)]}
 keep(DEST/'index.json',json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
 lines=['# 计算机组成原理第七版：习题截图索引','书页+11=PDF页。第1—10章168题；截图定位不等于逐题转录或核验解答。','|章节|题数|书页|PDF页|','|---|---:|---|---|']
 for ch,(a,b,total) in enumerate(SETS,1):lines.append(f'|{ch}|{total}|{a}–{b}|{a+11}–{b+11}|')
 lines+=['','查询：`scripts/lookup-exercise.py --book computer-organization-7 --question 4/8`。','当前解答覆盖另见 `题库/computer-organization-7/index.json`。']
 keep(DEST/'index.md','\n'.join(lines)+'\n');document.close()
 for item in idx['images']:
  file=DEST/item['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256']
  with Image.open(file) as im:
   assert max(im.size)==2600 and min(im.size)>1000
   assert ImageStat.Stat(im.convert('L')).stddev[0]>5,'Blank screenshot'
 for q in questions:assert all((DEST/p).is_file() for p in q['images'])
 keep(DEST/'verification.json',json.dumps({'ok':True,'bookSha256':SHA,'chapters':10,'questions':168,'images':31,
  'checks':['各章题号连续且无重复；对照目录确定章末范围','168条题目路径全部存在','31张图片解码、2600长边、非空白及SHA256通过'],
  'images':idx['images'],'limits':'章节定位不是全书逐字转录；本次七题已视觉核对，后续题目引用课文图表须补查。'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'ok':True,'chapters':10,'questions':168,'images':len(allpages)}))
if __name__=='__main__':main()
