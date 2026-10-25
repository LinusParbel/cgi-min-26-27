from pathlib import Path
from PIL import Image,ImageDraw
import json
A=Path('RunnerGame/Art/assets/hannover_route');v=[];faces=[]
for line in (A/'out/HannoverRoute.obj').read_text().splitlines():
 p=line.split()
 if p and p[0]=='v':v.append(tuple(map(float,p[1:])))
 elif p and p[0]=='f':faces.append([v[int(i.split('/')[0])-1] for i in p[1:]])
W,H=1400,1050;lo=(-300,-500);scale=1.28
im=Image.new('RGB',(W,H),'#eeeae2');d=ImageDraw.Draw(im)
def px(v):return ((v[0]-lo[0])*scale,H-(-v[2]-(-260))*scale)
# north at top
for f in sorted(faces,key=lambda f:sum(x[1] for x in f)):
 col=int(176-min(50,max(0,sum(x[1] for x in f)/3)*.8));d.polygon([px(x) for x in f],fill=(col,col+3,col+5))
d.rectangle((10,10,1000,64),fill='white');d.text((20,20),'Official Hannover LoD2 massing | north up | E550000/N5803000 local origin | 504 buildings | no facade detail',fill='black')
im.save(A/'overview.png')
