"""Combine rendered views without modifying the source images."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
p=Path(__file__).resolve().parent/'previews'
detail='vest_front' if (p/'vest_front.png').exists() else 'face'
sheet=Image.new('RGB',(1700,1120),'#20252b')
d=ImageDraw.Draw(sheet); font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for name,box,label in [
    ('three_quarter',(0,60,550,1060),'ORDNUNGSAMT / DARK CARRIER V2' if detail=='vest_front' else 'HANNOVER ORDNUNGSDIENST / V2'),
    ('back',(550,60,1100,1060),'BACK / IDENTIFICATION'),
    (detail,(1100,60,1700,660),'VEST / FRONT DETAILS' if detail=='vest_front' else 'FACE / COLLAR'),
    ('shoes',(1100,710,1700,1060),'BLACK DUTY BOOTS')]:
    im=Image.open(p/f'{name}.png').convert('RGB')
    if name=='face': im=im.crop((0,int(im.height*.13),im.width,int(im.height*.93)))
    if name=='shoes': im=im.crop((0,int(im.height*.28),im.width,int(im.height*.84)))
    im=ImageOps.contain(im,(box[2]-box[0],box[3]-box[1]))
    sheet.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))
    d.text((box[0]+14,box[1]-36),label,fill='white',font=font)
d.text((15,1080),'Neutral-pose appearance preview / packed Blender source / runtime v1 unchanged',fill='#b2becb',font=font)
sheet.save(p/'review_sheet.jpg',quality=93)
