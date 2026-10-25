"""Regenerate the woven ID label and rasterize the incorporated public-domain SVG."""
from pathlib import Path
import random
from PIL import Image,ImageDraw,ImageFont
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import pymupdf

p=Path(__file__).resolve().parent/'source'
im=Image.new('RGB',(1024,324),(18,25,36)); pix=im.load(); rng=random.Random(6)
for y in range(324):
    for x in range(1024): pix[x,y]=tuple(max(0,c+rng.randint(-3,3)) for c in (18,25,36))
d=ImageDraw.Draw(im); font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',102)
for y,word in [(85,'Stadt Hannover'),(237,'Ordnungsdienst')]:
    d.text((512,y),word,font=font,anchor='mm',fill=(221,226,230))
d.rounded_rectangle((7,7,1016,316),radius=8,outline=(35,43,54),width=3)
im.save(p/'identification_patch.png')
label=Image.new('RGB',(1024,200),(12,18,27))
text=Image.new('RGBA',(1600,180)); draw=ImageDraw.Draw(text)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',160)
draw.text((800,90),'ORDNUNGSAMT',font=font,anchor='mm',fill=(215,220,226))
text=text.crop(text.getbbox()).resize((920,130))
label.paste(text,(52,35),text); label.save(p/'ordnungsamt_patch.png')
drawing=svg2rlg(str(p/'hannover-arms.svg'))
doc=pymupdf.open(stream=renderPDF.drawToString(drawing),filetype='pdf')
doc[0].get_pixmap(alpha=True).save(str(p/'hannover-arms.png'))
print('OFFICER_TEXTURES_READY')
