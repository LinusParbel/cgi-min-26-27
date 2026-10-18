"""Copy the finished models (OBJ + PNG + mounts.json) from the scratch build folders into the game.

Build scripts write to tools/asset-spike/out/ (git-ignored scratch: previews, screenshots, ...).
This script publishes only what the game needs to RunnerGame/Assets/Models/<Category>/<Asset>/.
Run with plain Python:  python tools/asset-spike/publish_models.py
"""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "RunnerGame", "Assets", "Models")

# (scratch folder under out/, target Category/Asset, file prefixes that are published)
SETS = [
    ("baustelle/leitbake",        "Baustelle/Leitbake",        ["PROP_Leitbake_"]),
    ("baustelle/absperrschranke", "Baustelle/Absperrschranke", ["PROP_Absperrschranke_"]),
    ("baustelle/leitkegel",       "Baustelle/Leitkegel",       ["PROP_Leitkegel_"]),
    ("baustelle/schild123",       "Baustelle/Schild123",       ["PROP_Schild_Zeichen123"]),
    ("baustelle/warnleuchte",     "Baustelle/Warnleuchte",     ["PROP_Warnleuchte_"]),
    ("mull",                      "Mull/Tonne",                ["PROP_WheelieBin_120L_"]),
]

n = 0
for src, dst, prefixes in SETS:
    src_dir, dst_dir = os.path.join(HERE, "out", *src.split("/")), os.path.join(MODELS, *dst.split("/"))
    os.makedirs(dst_dir, exist_ok=True)
    for f in sorted(os.listdir(src_dir)):
        is_model = f.endswith((".obj", ".png")) and any(f.startswith(p) for p in prefixes) and "_preview" not in f \
            and "_closeup" not in f and "_context" not in f and "_mountcheck" not in f and "_comparison" not in f and "_engine" not in f
        if is_model or f == "mounts.json":
            shutil.copy2(os.path.join(src_dir, f), os.path.join(dst_dir, f)); n += 1
print(f"published {n} files to {MODELS}")
