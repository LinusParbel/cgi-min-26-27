"""Prove that a Blender build test can fail (system python; starts Blender itself).

    python RunnerGame/Art/lib/mutation_check.py <build.py> <blender_test.py> <test_name> --old "<text>" --new "<text>"

1. runs the test file: it must be GREEN before the change,
2. replaces `--old` (must occur exactly once in build.py) by `--new`, checks that the built geometry really changed
   (triangle count / bounds fingerprint), runs the tests again: `<test_name>` must now be RED,
3. restores build.py (also on errors).

Mutate the BUILD code, not spec.json: a build-equals-spec test follows the spec and stays green. Typical mutations:
scale a part, close an opening, move a part by 0.2 m. Exit code 0 = the test is proven (green -> red); 1 otherwise.
The fingerprint step catches a mutation that never reached the geometry (e.g. placed after the value was read).
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
BL_ARGS = ["--background", "--factory-startup", "--python-exit-code", "1", "--python"]


def run_blender(script, *extra):
    cmd = [BLENDER, *BL_ARGS, str(script)] + (["--", *extra] if extra else [])
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def failed_tests(output):
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", output, re.M))


def fingerprint(build_py):
    """Build the asset in Blender and return the geometry fingerprint line."""
    probe = Path(tempfile.mkdtemp()) / "fp_probe.py"
    lib = Path(__file__).resolve().parent
    probe.write_text(
        "import sys, importlib.util\n"
        f"sys.path.insert(0, {str(lib)!r})\n"
        "import photo_lib as pl, geom_probe as gp\n"
        f"s = importlib.util.spec_from_file_location('b', {str(build_py)!r}); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
        "pl.al.clear_scene()\n"
        f"parts = m.build(pl.Spec({str(Path(build_py).with_name('spec.json'))!r}))\n"
        "print('FINGERPRINT', gp.fingerprint(parts))\n", encoding="utf-8")
    _, out = run_blender(probe)
    m = re.search(r"FINGERPRINT (.*)", out)
    if not m:
        sys.exit("fingerprint failed:\n" + out[-800:])
    return m.group(1).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("test_file")
    ap.add_argument("test_name")
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    a = ap.parse_args()
    build = Path(a.build).resolve()
    original = build.read_text(encoding="utf-8")
    if original.count(a.old) != 1:
        sys.exit(f"--old must occur exactly once in {build.name} (found {original.count(a.old)})")

    code, out = run_blender(Path(a.test_file).resolve())
    if failed_tests(out) or code != 0:
        sys.exit(f"not GREEN before the mutation: {sorted(failed_tests(out))}")
    fp_before = fingerprint(build)

    try:
        build.write_text(original.replace(a.old, a.new), encoding="utf-8")
        fp_after = fingerprint(build)
        code, out = run_blender(Path(a.test_file).resolve())
        red = failed_tests(out)
    finally:
        build.write_text(original, encoding="utf-8")

    print("geometry before:", fp_before)
    print("geometry after :", fp_after)
    if fp_before == fp_after:
        sys.exit("the mutation did NOT change the geometry: move it (it probably sits after the value was read)")
    print("RED tests      :", sorted(red) or "none")
    if a.test_name not in red:
        sys.exit(f"{a.test_name} stayed GREEN under a real geometry change: the test is blind")
    print(f"OK: {a.test_name} goes green -> red; build.py restored")


if __name__ == "__main__":
    main()
