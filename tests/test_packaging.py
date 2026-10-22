from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from tools.package_standard import package


class DistributionTests(unittest.TestCase):
    def test_archive_is_deterministic_checksums_match_and_owner_sources_are_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            first,second=Path(folder)/'a.zip',Path(folder)/'b.zip'
            package(first)
            package(second)
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with ZipFile(first) as archive:
                names=archive.namelist()
                self.assertFalse(any('/portfolio/' in n or '/dist/' in n or '/audit/' in n or '__pycache__' in n for n in names))
                root='project-record-standard/'
                config=json.loads(archive.read(root+'examples/projects.json'))
                self.assertTrue(all(e['project']['visibility']=='public' for e in config['projects']))
                checksums=archive.read(root+'checksums.sha256').decode().splitlines()
                for line in checksums:
                    digest,name=line.split('  ',1)
                    self.assertEqual(sha256(archive.read(root+name)).hexdigest(),digest)


if __name__=='__main__':
    unittest.main()
