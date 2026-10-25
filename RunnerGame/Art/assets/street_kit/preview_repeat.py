"""Make a review-only two-module manifest; does not duplicate exported meshes."""
import json,copy
from pathlib import Path
p=Path(__file__).resolve().parent/'out'
d=json.loads((p/'ST_Street_parts.json').read_text())
extra=copy.deepcopy(d['parts'])
for part in extra:
    part['name']+='__repeat'
    part['pivot']=[0,20,0]
d['parts']+=extra
(p/'ST_Street_repeat_parts.json').write_text(json.dumps(d,indent=2))
