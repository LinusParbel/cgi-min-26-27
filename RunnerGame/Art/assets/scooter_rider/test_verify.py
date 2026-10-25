"""Prove exported-mesh validation rejects invalid geometry/index/UV data."""
import unittest, tempfile
from pathlib import Path
from verify import read_obj
class ExportValidator(unittest.TestCase):
    fixture='v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\n'
    def check(self,text):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'test.obj'; p.write_text(text); return read_obj(p)
    def test_valid_triangle(self): self.assertEqual(len(self.check(self.fixture)[2]),1)
    def test_invalid_index_rejected(self):
        with self.assertRaises(AssertionError): self.check(self.fixture.replace('3/3/1','4/3/1'))
    def test_degenerate_triangle_rejected(self):
        with self.assertRaises(AssertionError): self.check(self.fixture.replace('v 0 1 0','v 2 0 0'))
    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError): self.check(self.fixture.replace('v 0 1 0','v nan 1 0'))
    def test_invalid_uv_rejected(self):
        with self.assertRaises(AssertionError): self.check(self.fixture.replace('vt 0 1','vt 0 2'))
if __name__=='__main__': unittest.main()
