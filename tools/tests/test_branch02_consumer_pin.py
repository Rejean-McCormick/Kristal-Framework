"""Framework owner validates consumer-submitted pins without editing TCK assets."""
from pathlib import Path
import tempfile
import json
import unittest
import os
from tools.v11.check_consumer_pin import verify_consumer_pin, ConsumerPinError

ROOT=Path(__file__).resolve().parents[2]
KIT=Path(os.environ.get('BRANCH02_KIT_ROOT','/missing-kit'))

class ConsumerPinTests(unittest.TestCase):
    @unittest.skipUnless(KIT.is_dir(),'Explicit Authoring Kit checkout required for bilateral source test')
    def test_actual_kit_draft4_pin_matches_framework_bytes(self):
        report=verify_consumer_pin(KIT/'contracts/v11-framework-pin.json')
        self.assertEqual(report['files_matched'],13)
        self.assertFalse('certified' in report['qualification'])

    @unittest.skipUnless(KIT.is_dir(),'Explicit Authoring Kit checkout required for negative test')
    def test_modified_consumer_pin_fails(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'pin.json'
            data=json.loads((KIT/'contracts/v11-framework-pin.json').read_text())
            data['files']['schemas/v11/kristal-semantic-graph.schema.json']='f'*64
            file.write_text(json.dumps(data))
            with self.assertRaisesRegex(ConsumerPinError,'pin mismatch'):
                verify_consumer_pin(file)

    def test_missing_consumer_pin_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ConsumerPinError,'Missing consumer pin'):
                verify_consumer_pin(Path(td)/'absent.json')

if __name__=='__main__':unittest.main()
