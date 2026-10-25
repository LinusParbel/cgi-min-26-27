"""Assemble synchronized three-quarter and side views with a shared GIF palette."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image,ImageDraw,ImageFont,ImageOps

HERE=Path(__file__).resolve().parent; p=HERE/'previews/run'
data=json.loads((p/'motion.json').read_text()); count=data['frames']; fps=data['fps']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
frames=[]
for frame in range(1,count+1):
    canvas=Image.new('RGB',(960,640),'#20252b'); d=ImageDraw.Draw(canvas)
    for i,view in enumerate(('three_quarter','side')):
        im=Image.open(p/f'{view}_{frame:02d}.png').convert('RGB')
        canvas.paste(im,(i*480,32))
    d.text((15,7),'OFFICER V2 / RUN PREVIEW',fill='white',font=font)
    d.text((495,7),'SIDE / FOOT CONTACT',fill='white',font=font)
    frames.append(canvas)
palette_sheet=Image.new('RGB',(480*8,320*((count+7)//8)))
for i,im in enumerate(frames): palette_sheet.paste(im.resize((480,320)),((i%8)*480,(i//8)*320))
palette=palette_sheet.quantize(colors=256)
indexed=[im.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
target=HERE/'previews/officer_v2_run_natural_hands.gif'
frame_ms=round(1000/fps)
assert frame_ms%10==0, 'Choose a frame rate with exact GIF timing'
indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=[frame_ms]*count,loop=0,disposal=2,optimize=False)
shutil.copyfile(target,HERE/'previews/officer_v2_run.gif')
shutil.copyfile(target,HERE/'previews/officer_v2_run_smooth.gif')
gif=Image.open(target); durations=[]
for i in range(gif.n_frames): gif.seek(i); durations.append(gif.info['duration'])
assert gif.n_frames==count and sum(durations)==800 and len(set(durations))==1
assert hashlib.sha256((HERE/'officer_v2.blend').read_bytes()).hexdigest()==data['neutral_source_sha256']
sheet=Image.new('RGB',(1440,664),'#20252b')
for j,view in enumerate(('three_quarter','side')):
    for i,frame in enumerate(1+round(i*count/6) for i in range(6)):
        im=Image.open(p/f'{view}_{frame:02d}.png').convert('RGB').resize((240,300))
        sheet.paste(im,(i*240,j*332+28)); ImageDraw.Draw(sheet).text((i*240+8,j*332+5),f'{view} / {frame:02d}',font=font,fill='white')
sheet.save(HERE/'previews/run_contact_sheet.jpg',quality=92)
report={'gif':str(target),'frames':gif.n_frames,'duration_ms':sum(durations),'bytes':target.stat().st_size,'neutral_source_unchanged':True}
(p/'gif_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
