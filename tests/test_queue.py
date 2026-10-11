import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/orange-story-generator/scripts/queue.py'


class QueueReliability(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        (self.project / 'prompts').mkdir()
        (self.project / 'prompts/generation-prompts.json').write_bytes(
            (ROOT / 'prompts/generation-prompts.json').read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--project',
                                 str(self.project), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return json.loads(result.stdout) if success else result.stderr

    def test_resume_does_not_submit_running_or_uncertain_job(self):
        self.command('init')
        self.command('begin', '01A')
        self.command('next', success=False)
        self.command('begin', '01A', success=False)
        self.command('fail', '01A', '--reason', 'Provider timeout', '--uncertain')
        self.command('retry', '01A', success=False)
        self.command('next', success=False)
        output = self.project / 'hero.png'
        output.write_bytes(b'provider output placeholder for ledger test')
        self.command('finish', '01A', '--artifact', str(output), '--note', 'Reconciled original operation')
        self.assertEqual(self.command('next')['id'], '01B')

    def test_complete_run_resumes_in_order_and_refuses_missing_outputs(self):
        self.assertEqual(self.command('init')['job_count'], 27)
        self.command('begin', '02A', success=False)
        completed = []
        while True:
            job = self.command('next')
            if job.get('complete'):
                break
            self.command('begin', job['id'])
            self.command('finish', job['id'], '--artifact', 'missing', '--note', 'Invalid', success=False)
            artifact = self.project / (job['id'] + '.json')
            artifact.write_text('{}')
            self.command('finish', job['id'], '--artifact', str(artifact), '--note', 'Test inspection')
            completed.append(job['id'])
        self.assertEqual(len(completed), 27)
        self.assertIn('M02A', completed)
        self.assertIn('M02B', completed)
        self.assertEqual(completed[-1], 'qa-review')
        self.command('begin', '01A', success=False)

    def test_catalog_change_cannot_silently_reset_history(self):
        self.command('init')
        path = self.project / 'prompts/generation-prompts.json'
        path.write_text(path.read_text() + '\n')
        self.assertIn('catalog changed', self.command('next', success=False))


if __name__ == '__main__':
    unittest.main()
