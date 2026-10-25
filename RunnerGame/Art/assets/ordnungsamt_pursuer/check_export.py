"""Verify delivered OBJ data and assemble the engine review artifacts."""
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
PREV=ROOT/'previews'
prefix='CHR_Ordnungsamt'
baseline=None
for index in range(1,9):
    path=OUT/f'{prefix}_run_{index:02d}.obj'
    vertices=[]; uvs=[]; faces=[]; normals=[]
    for line in path.read_text().splitlines():
        fields=line.split()
        if not fields:
            continue
        if fields[0]=='v': vertices.append(tuple(map(float,fields[1:4])))
        elif fields[0]=='vt': uvs.append(tuple(map(float,fields[1:])))
        elif fields[0]=='vn': normals.append(tuple(map(float,fields[1:])))
        elif fields[0]=='f': faces.append([tuple(map(int,v.split('/'))) for v in fields[1:]])
    topology=[[(v[0],v[1]) for v in face] for face in faces]
    if baseline is None:
        baseline=(topology,uvs)
    assert (topology,uvs)==baseline, f'UV/topology mismatch: {index}'
    # OBJ deduplicates normals by direction; their count may change as joints move.
    assert normals and all(1<=v[2]<=len(normals) for face in faces for v in face)
    assert len(faces)==11542 and all(len(f)==3 for f in faces)
    expected=.035 if index in (3,7) else 0
    assert abs(min(v[1] for v in vertices)-expected)<.00001
    print(f'Pose {index}: 11542 tris; matching UV/indices, valid normals; floor OK')
with Image.open(OUT/f'{prefix}.png') as texture:
    assert texture.size==(1024,1024)
    assert texture.convert('RGBA').getchannel('A').getextrema()==(255,255)
frames=[]
for index in range(1,9):
    with Image.open(PREV/f'final_{index:02d}_35.png') as img:
        frames.append(img.convert('RGB'))
frames[0].save(PREV/'engine_run.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
sheet=Image.new('RGB',(1440,460),(34,40,49))
draw=ImageDraw.Draw(sheet)
for i,(file,label) in enumerate([('final_01_35.png','EXPORTED POSE 1'),('final_03_35.png','EXPORTED POSE 3'),('final_back_180.png','BACK LETTERING')]):
    with Image.open(PREV/file) as img:
        # Crop the fixed viewer's empty margins to show the model clearly.
        tile=img.crop((370,0,910,720)).resize((324,432))
        sheet.paste(tile,(i*480+78,28))
    draw.text((i*480+20,10),label,fill='white')
sheet.save(PREV/'engine_review.png')
files=[OUT/f'{prefix}.png',OUT/f'{prefix}_animation.json',OUT/'validation.json',OUT/'README.md']
files += [OUT/f'{prefix}_run_{i:02d}{suffix}' for i in range(1,9) for suffix in ('.obj','_parts.json')]
with zipfile.ZipFile(ROOT/'ordnungsamt_model_pack.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file,file.name)
print('PASS: 8 OBJ poses, shared 1024 atlas; engine GIF, review sheet and ZIP created')
