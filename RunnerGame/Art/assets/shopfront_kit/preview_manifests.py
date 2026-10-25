import json
from pathlib import Path
here=Path(__file__).resolve().parent
out=here/'out';info=json.loads((out/'AR_Shopfront_parts.json').read_text())
stack={'texture':info['texture'],'parts':[{**p,'pivot':[0,0,i*3.2]} for i,p in enumerate(info['parts'])]}
(out/'preview_stack.json').write_text(json.dumps(stack,indent=2))
for p in info['parts']:
 (out/('preview_'+p['name']+'.json')).write_text(json.dumps({'texture':info['texture'],'parts':[p]},indent=2))
