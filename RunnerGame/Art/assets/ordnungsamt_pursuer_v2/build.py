"""Build the current officer v2. Original anatomy pass: build_anatomy.py."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name('build_refined.py')),run_name='__main__')
