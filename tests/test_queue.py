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
        (self.project / '.gitignore').write_text('.local/\noutputs/\n')
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Queue Test')
        self.git('config', 'user.email', 'queue-test@example.invalid')
        self.git('add', 'prompts', '.gitignore')
        self.git('commit', '-q', '-m', 'Initialize queue test fixture')
        self.remote = self.project / '.local/remote.git'
        self.remote.parent.mkdir()
        self.git('init', '-q', '--bare', str(self.remote))
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', '-q', 'origin', 'main')

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--project',
                                 str(self.project), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return json.loads(result.stdout) if success else result.stderr

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.project,
                                       stderr=subprocess.PIPE).decode().strip()

    def commit_phase(self, ident, description=True):
        self.git('add', 'progress/' + ident + '.json')
        arguments = ['commit', '-q', '-m', 'Complete phase ' + ident + ': save inspected output']
        if description:
            arguments += ['-m', 'Record the inspected artifact and checksum for the next phase.\n\nValidation: completed the queue fixture inspection.']
        self.git(*arguments)
        return self.git('rev-parse', 'HEAD')

    def publish_phase(self, ident):
        sha = self.commit_phase(ident)
        self.git('push', '-q', 'origin', 'main')
        return self.command('checkpoint', ident, '--commit', sha)

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
        self.command('next', success=False)
        self.publish_phase('01A')
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
            self.command('next', success=False)
            checkpoint = self.publish_phase(job['id'])
            self.assertEqual(checkpoint['commit'], self.git('rev-parse', 'HEAD'))
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

    def finish_first_phase(self):
        self.command('init')
        self.command('begin', '01A')
        output = self.project / 'hero.png'
        output.write_bytes(b'fixture output')
        self.command('finish', '01A', '--artifact', str(output), '--note', 'Inspected fixture')

    def test_unpushed_commit_cannot_unlock_next_phase(self):
        self.finish_first_phase()
        sha = self.commit_phase('01A')
        self.command('checkpoint', '01A', '--commit', sha, success=False)
        self.command('next', success=False)
        self.git('push', '-q', 'origin', 'main')
        self.command('checkpoint', '01A', '--commit', sha)
        self.assertEqual(self.command('next')['id'], '01B')

    def test_commit_without_description_cannot_unlock_next_phase(self):
        self.finish_first_phase()
        sha = self.commit_phase('01A', description=False)
        self.git('push', '-q', 'origin', 'main')
        self.assertIn('description', self.command('checkpoint', '01A', '--commit', sha, success=False))
        self.command('next', success=False)


if __name__ == '__main__':
    unittest.main()
