"""Fetch official route tiles with HTTP byte ranges; no full city ZIP required.
Run from repository root. curl and Python standard library only.
"""
import pathlib,subprocess,struct,zlib,json,hashlib,datetime
R=pathlib.Path('.model-research/hannover_route/source');R.mkdir(parents=True,exist_ok=True)
URL='https://opengeodata.hannover-stadt.de/Stadtmodell_Hannover_CityGML_LOD2.zip'
NAMES={'5490_5802.gml','5490_5803.gml','5500_5802.gml','5500_5803.gml','5510_5802.gml','5510_5803.gml'}
def fetch(a,b,path):subprocess.run(['curl.exe','-L','--fail','--retry','2','-r',f'{a}-{b}','-o',str(path),URL],check=True)
fetch('','131072',R/'zip_tail.bin') if not (R/'zip_tail.bin').exists() else None
raw=(R/'zip_tail.bin').read_bytes();p=0;items=[]
while (p:=raw.find(b'PK\x01\x02',p))>=0:
 h=struct.unpack_from('<4s6H3I5H2I',raw,p);name=raw[p+46:p+46+h[10]].decode()
 if name in NAMES:
  it=dict(name=name,method=h[4],crc=h[7],compressed=h[8],uncompressed=h[9],offset=h[16]);items.append(it)
 p+=46+h[10]+h[11]+h[12]
assert len(items)==len(NAMES)
for it in items:
 path=R/it['name']
 if not path.exists():
  record=R/(it['name']+'.record');fetch(it['offset'],it['offset']+it['compressed']+1023,record)
  data=record.read_bytes();h=struct.unpack_from('<4s5H3I2H',data);start=30+h[-2]+h[-1]
  path.write_bytes(zlib.decompress(data[start:start+it['compressed']],-15))
 data=path.read_bytes();assert len(data)==it['uncompressed'] and zlib.crc32(data)==it['crc']
 it['sha256']=hashlib.sha256(data).hexdigest()
(R/'tile_manifest.json').write_text(json.dumps(items,indent=2))
(R/'download_log.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':URL,'method':'HTTP byte ranges from official ZIP central directory; individual extracted files verified by ZIP CRC32 and SHA256','tiles':items},indent=2))
