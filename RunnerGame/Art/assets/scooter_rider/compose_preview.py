from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent/'previews'
names=['export_ride_side','export_duck_side','export_ride_hands','export_ride_feet']
canvas=Image.new('RGB',(1300,1500),(30,30,30))
for i,name in enumerate(names):
    canvas.paste(Image.open(HERE/(name+'.png')),(650*(i%2),750*(i//2)))
draw=ImageDraw.Draw(canvas)
for xy,label in [((16,15),'RIDE: actual exported OBJ + shared atlas'),((666,15),'DUCK: actual exported OBJ + same atlas'),((16,765),'Grip contact: opaque mesh and atlas'),((666,765),'Tandem sole/deck contact')]: draw.text(xy,label,fill=(255,255,255),stroke_width=1,stroke_fill=(0,0,0))
canvas.save(HERE/'final_export_board.png')
