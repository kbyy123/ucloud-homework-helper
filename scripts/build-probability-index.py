"""Reproducible, conservative exercise-page catalogue for the supplied scan."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT.parent/'26fa-概率论与随机过程'/'概率论与随机过程.pdf'
OUT=ROOT/'题库'/'页面索引'/'probability-bupt-2021'
SHA='80662453203acbf11f5c6b4368c649e2437ba07837dd90465d52f4cceec06200'
# chapter -> (printed page, first number, last number). Boundary questions also
# include the next exercise page to retain formulas/figures continuing there.
MAP={1:[(33,1,7),(34,8,17),(35,18,32),(36,33,44),(37,45,47)],
 2:[(65,1,9),(66,10,22),(67,23,31),(68,32,38)],
 3:[(105,1,11),(106,12,17),(107,18,24),(108,25,33)],
 4:[(143,1,7),(144,8,18),(145,19,27),(146,28,38)],
 5:[(157,1,11),(158,12,18)],6:[(173,1,10),(174,11,22)],
 7:[(190,1,10),(191,11,11)],8:[(206,1,8),(207,9,15)],
 9:[(225,1,7),(226,8,15),(227,16,25),(228,26,26)],
 10:[(257,1,7),(258,8,11),(259,12,15),(260,16,16)],11:[(271,1,6)]}
TITLES=['概率论的基本概念','随机变量及其分布','多维随机变量及其分布','随机变量的数字特征','大数定律与中心极限定理','随机过程的概念及其统计特性','泊松过程','平稳过程','平稳过程的谱分析','离散时间马尔可夫链','连续时间马尔可夫链']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def preserve(p,data):
 if p.exists():
  if p.read_bytes()!=data:raise FileExistsError('Preserving existing/manual file: '+str(p))
 else:p.write_bytes(data)
def main():
 assert digest(BOOK)==SHA
 groups=[];questions=[]
 for chapter,pages in MAP.items():
  all_pages=[p+11 for p,_,_ in pages]
  for i,(printed,lo,hi) in enumerate(pages):
   for n in range(lo,hi+1):
    pdf=[printed+11]
    if n==hi and i+1<len(pages):pdf.append(pages[i+1][0]+11)
    # Retain previous-page context for the first number at a scan page boundary.
    if n==lo and i>0:pdf.insert(0,pages[i-1][0]+11)
    questions.append({'key':f'{chapter}/{n}','section':str(chapter),'number':n,'kind':'exercises',
      'start':{'pdfPage':printed+11,'y':None},'printedPages':[p-11 for p in pdf],'pdfPages':pdf,
      'images':[f'images/pdf-{p:04}.png' for p in pdf],'imageIndexed':True,'transcribed':False,
      'dependencies':[],'notice':'章末题号按原书页组定位；边界题保守补相邻页。仅本次作业已逐字核对，其余题目须读图核实全部小问和外部引用。'})
  groups.append({'key':str(chapter),'title':TITLES[chapter-1],'questionCount':pages[-1][2],
    'pdfPages':all_pages,'images':[f'images/pdf-{p:04}.png' for p in all_pages]})
 assert len(questions)==270 and len({q['key'] for q in questions})==270
 # Add the textbook definition pages actually checked for this assignment.
 for q in questions:
  extra={'1/26':[28,29],'2/3':[50],'2/13':[57]}.get(q['key'],[])
  for p in extra:
   q['pdfPages']=sorted(set(q['pdfPages']+[p]));q['printedPages']=[n-11 for n in q['pdfPages']]
   q['images']=[f'images/pdf-{n:04}.png' for n in q['pdfPages']]
 images={}
 for p in sorted((OUT/'images').glob('*.png')):
  with Image.open(p) as im:
   im.load();assert max(im.size)==2600 and ImageStat.Stat(im.convert('L')).stddev[0]>10
   images['images/'+p.name]={'sha256':digest(p),'width':im.width,'height':im.height}
 index={'schema':1,'bookId':'probability-bupt-2021','title':'概率论与随机过程','edition':'2021年1月第1版','isbn':'978-7-5635-6266-4',
  'editors':['北京邮电大学数学系概率教学组'],'source':str(BOOK),'sourceSha256':SHA,'sourcePdfPageCount':321,
  'scope':{'chapters':list(MAP),'names':['全书11章章末习题；本次相关定义页'],'excludes':['课文例题及未被本次题目引用的课内图表']},
  'pageOffset':11,'questionCount':len(questions),'imageCount':len(images),'groups':groups,'questions':questions,
  'notice':'截图及题号定位不代表已验证答案；当前完整作答范围在解答题库index.json。'}
 preserve(OUT/'index.json',(json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode())
 lines=['# 概率论与随机过程题目图片索引','', '北邮出版社，2021年1月第1版，ISBN 978-7-5635-6266-4。全书11章270题，书页+11=PDF页。',
  '', '页边界题保守附相邻页，防止续题、表格或图漏读。未逐字转录全书，图片覆盖不等于解答核验。','', '|题号|书页|PDF页|图片|','|---|---|---|---|']
 for q in questions:lines.append('|'+q['key']+'|'+','.join(map(str,q['printedPages']))+'|'+','.join(map(str,q['pdfPages']))+'|'+' / '.join(f'[PDF{p}](images/pdf-{p:04}.png)' for p in q['pdfPages'])+'|')
 preserve(OUT/'索引.md',('\n'.join(lines)+'\n').encode())
 result={'schema':1,'bookId':index['bookId'],'sourceSha256':SHA,'questionCount':270,'imageCount':len(images),'status':'passed',
  'checks':['教材SHA-256','11章连续题号及全体图片链接','PNG解码/尺寸/非空白','目录书页与PDF偏移','页边界补图'],
  'visualReview':'封面版权、目录、本次题目及参考定义逐页视觉核对；其余题号按页组与OCR及边界复核，未声称全书逐字校对。','images':images}
 for q in questions:
  assert all((OUT/p).exists() for p in q['images'])
 preserve(OUT/'verification.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({'ok':True,'questions':270,'chapters':11,'images':len(images)}))
if __name__=='__main__':main()
