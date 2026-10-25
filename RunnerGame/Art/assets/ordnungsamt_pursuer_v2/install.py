"""Install the engine-view-approved export using existing runtime asset names."""
from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[3]
OUT=HERE/'out'; TARGET=REPO/'RunnerGame/Assets/Models/Charakter/Ordnungsamt'
OLD='CHR_Ordnungsamt'; NEW='CHR_OrdnungsamtV2'
BACKUP=HERE/'checkpoints/runtime_v1_before_v2_install'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
checks=json.loads((OUT/'export_checks.json').read_text())
assert checks['matching_topology_uv'] and checks['source_hashes_unchanged']
if not BACKUP.exists():
    BACKUP.mkdir(parents=True)
    originals=list(TARGET.glob('*'))
    for p in originals:
        if p.is_file(): shutil.copy2(p,BACKUP/p.name)
    (BACKUP/'backup_hashes.json').write_text(json.dumps({p.name:digest(p) for p in originals if p.is_file()},indent=2))
for name,sha in json.loads((BACKUP/'backup_hashes.json').read_text()).items(): assert digest(BACKUP/name)==sha
TARGET.mkdir(parents=True,exist_ok=True)
installed={}
for suffix in ['.png']+[f'_run_{i:02d}.obj' for i in range(1,41)]:
    source=OUT/(NEW+suffix); destination=TARGET/(OLD+suffix)
    shutil.copy2(source,destination)
    assert digest(source)==digest(destination)
    installed[destination.name]=digest(destination)
manifest=json.loads((OUT/(NEW+'_animation.json')).read_text())
manifest['texture']=OLD+'.png'
for frame in manifest['frames']: frame['obj']=frame['obj'].replace(NEW,OLD)
path=TARGET/(OLD+'_animation.json'); path.write_text(json.dumps(manifest,indent=2))
installed[path.name]=digest(path)
assert len(manifest['frames'])==40 and sum(f['duration_ms'] for f in manifest['frames'])==800
assert {p.name for p in TARGET.iterdir() if p.is_file()}==set(installed)
report={'approved_engine_view':True,'runtime_directory':str(TARGET),'files':installed,'triangles_per_pose':73710,'frames':40,'duration_ms':800,'previous_runtime_backup':str(BACKUP),'gameplay_pose_switching_implemented':False}
(HERE/'previews/runtime_installation.json').write_text(json.dumps(report,indent=2))
print('INSTALLED_VERIFIED',len(installed),'files; 40 poses / opaque atlas / manifest; v1 backup verified')
