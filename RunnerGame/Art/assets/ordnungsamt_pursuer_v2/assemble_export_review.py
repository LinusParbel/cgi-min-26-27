"""Assemble actual engine renders with fixed framing and uniform GIF cadence."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
here=Path(__file__).resolve().parent; prev=here/'previews'
frames=[Image.open(prev/f'engine_run_{i:02d}_game.png').convert('RGB').crop((390,150,890,720)) for i in range(1,41)]
sheet=Image.new('RGB',(500*8,570*5))
for i,im in enumerate(frames): sheet.paste(im,((i%8)*500,(i//8)*570))
palette=sheet.quantize(colors=256)
indexed=[im.quantize(palette=palette) for im in frames]
target=prev/'engine_run.gif'
indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=20,loop=0,disposal=2,optimize=False)
gif=Image.open(target); assert gif.n_frames==40
for i in range(40): gif.seek(i); assert gif.info['duration']==20
review=Image.new('RGB',(960,510),'#20252b'); draw=ImageDraw.Draw(review)
for i,(angle,label) in enumerate(((35,'BAKED / THREE-QUARTER'),(90,'BAKED / SIDE'),(180,'BAKED / BACK'))):
    tile=Image.open(prev/f'export_01_{angle}.png').convert('RGB').crop((400,0,880,720)).resize((320,480))
    review.paste(tile,(i*320,30)); draw.text((i*320+12,9),label,fill='white')
review.save(prev/'engine_review.png')
phases=Image.new('RGB',(1600,560),'#20252b')
for i,frame in enumerate((1,6,11,16,21,26,31,36)):
    tile=frames[frame-1].resize((200,228))
    phases.paste(tile,(i*200,30)); ImageDraw.Draw(phases).text((i*200+8,8),f'ENGINE / {frame:02d}',fill='white')
phases.crop((0,0,1600,258)).save(prev/'engine_run_contact_sheet.jpg',quality=94)
(prev/'engine_review_validation.json').write_text(json.dumps({'frames':40,'frame_ms':20,'duration_ms':800,'fixed_crop':[390,150,890,720],'source':'actual OBJ+PNG in existing engine viewer'},indent=2))
print('ENGINE_REVIEW_ASSEMBLED',target)
