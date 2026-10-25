from pathlib import Path
import tempfile,json,shutil,subprocess,sys
A=Path(__file__).resolve().parent
code=(A/'verify.py').read_text();results={}
for kind in ['bad_index','zero_area','bad_normal','floating_wheel']:
 with tempfile.TemporaryDirectory() as td:
  d=Path(td);shutil.copytree(A/'out',d/'out');part=d/'out/VEH_DeliveryVan_front_left.obj';lines=part.read_text().splitlines()
  if kind=='bad_index':
   i=next(i for i,l in enumerate(lines) if l.startswith('f '));lines[i]='f 999999/1/1 1/1/1 2/2/2'
  if kind=='zero_area':
   i=next(i for i,l in enumerate(lines) if l.startswith('f '));t=lines[i].split();lines[i]='f '+ ' '.join([t[1]]*3)
  if kind=='bad_normal':
   i=next(i for i,l in enumerate(lines) if l.startswith('vn '));lines[i]='vn 0 0 0'
  if kind=='floating_wheel':
   lines=['v '+ ' '.join([l.split()[1],str(float(l.split()[2])+.05),l.split()[3]]) if l.startswith('v ') else l for l in lines]
  part.write_text('\n'.join(lines));v=d/'fixture_verify.py';v.write_text(code.replace('A=Path(__file__).resolve().parent',f'A=Path({str(d)!r})'))
  r=subprocess.run([sys.executable,str(v)],capture_output=True,text=True);assert r.returncode!=0,kind;assert 'AssertionError' in r.stderr, r.stderr;results[kind]='correctly rejected'
(A/'negative-fixtures.json').write_text(json.dumps(results,indent=2));print(results)
