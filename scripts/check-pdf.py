"""Validate a compiled learning PDF; optionally render every page for visual QA."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
import pypdfium2 as pdfium

def inspect(filename, previews=None):
    filename=Path(filename)
    if not filename.read_bytes().startswith(b'%PDF-'):raise ValueError('Not a PDF')
    reader=PdfReader(filename)
    if not reader.pages:raise ValueError('PDF has no pages')
    texts=[]
    for page in reader.pages:
        text=page.extract_text() or ''
        if not text.strip():raise ValueError('PDF has an empty text page')
        if '\ufffd' in text:raise ValueError('PDF contains replacement characters')
        texts.append(text)
    rendered=[]
    if previews:
        destination=Path(previews);destination.mkdir(parents=True,exist_ok=True)
        document=pdfium.PdfDocument(str(filename))
        for i in range(len(document)):
            page=document[i];bitmap=page.render(scale=1.5)
            image=destination/f'page-{i+1:02}.png'
            bitmap.to_pil().save(image);bitmap.close();page.close();rendered.append(str(image))
        document.close()
    return {'ok':True,'pages':len(texts),'characters':sum(map(len,texts)),'previews':rendered,
            'visualReview':'Rendered pages must also be inspected by the agent before reporting delivery.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('pdf');parser.add_argument('--previews');args=parser.parse_args()
    print(json.dumps(inspect(args.pdf,args.previews),ensure_ascii=True))
