#!/usr/bin/env python3
"""Persistent sequential prompt queue. Does not call a paid provider itself."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def build_jobs(catalog):
    jobs = []
    def add(ident, kind, prompt, dependencies=(), **metadata):
        jobs.append(dict(id=ident, kind=kind, prompt=prompt,
                         dependencies=list(dependencies), **metadata))
    for painting in catalog['paintings']:
        ident = painting['id']
        refs = {'01A': [], '01B': ['01A'], '01C': ['01A', '01B'],
                '01D': ['01A'], '02A': ['01A'], '02B': ['02A'],
                '02C': ['02A', '02B'], '03A': ['02C'], '03B': ['01A', '01C'],
                '04A': ['01C'], '04B': ['01A']}[ident]
        add(ident, 'painting', painting['prompt'], refs,
            title=painting['title'], chapter=painting['chapter'],
            reuse_asset=painting.get('reuse_asset'), reference_assets=refs)
    for shot in catalog['motion_shots']:
        if shot['id'] == 'M02':
            for suffix, asset in [('A', '02A'), ('B', '02B')]:
                add('M02' + suffix, 'motion', shot['prompt'], [asset],
                    title=shot['title'], source_asset=asset)
        else:
            add(shot['id'], 'motion', shot['prompt'], [shot['source_asset']],
                title=shot['title'], source_asset=shot['source_asset'])
    media_ids = [job['id'] for job in jobs]
    add('webgl-foundation', 'implementation', catalog['implementation_prompt'],
        media_ids, title='Four-chapter WebGL foundation')
    add('transition-01-02', 'implementation',
        catalog['model_to_work_transition']['specification_markdown'],
        ['webgl-foundation'], title='The Model to The Work')
    blocks = re.findall(r'\*\*([^*]+)\*\*\s*\n(.*?)(?=\n\*\*|\Z)',
                        catalog['other_transitions_markdown'], re.S)
    names = ['transition-02-03', 'terms-internal', 'transition-03-04', 'questions-application']
    if len(blocks) != len(names):
        raise ValueError('Expected four remaining transition prompts.')
    previous = 'transition-01-02'
    for ident, (title, body) in zip(names, blocks):
        add(ident, 'implementation', body.strip(), [previous], title=title)
        previous = ident
    add('qa-review', 'review', catalog['correction_prompt'], [previous],
        title='Whole-story motion and continuity review')
    ids = [job['id'] for job in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate job IDs.')
    for index, job in enumerate(jobs):
        if not set(job['dependencies']).issubset(ids[:index]):
            raise ValueError('A dependency appears after its job: ' + job['id'])
    return jobs


def write_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n')
    os.replace(temporary, path)


def load(project):
    raw = (project / 'prompts/generation-prompts.json').read_text()
    sha = hashlib.sha256(raw.encode()).hexdigest()
    state_path = project / '.local/run-state.json'
    jobs = build_jobs(json.loads(raw))
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state['catalog_sha256'] != sha:
            raise ValueError('Prompt catalog changed. Preserve the old ledger and explicitly start a new run.')
    else:
        state = dict(version=1, catalog_sha256=sha, created_at=now(),
                     jobs={job['id']: dict(status='pending') for job in jobs})
    return state_path, state, jobs


def next_job(state, jobs):
    for job in jobs:
        entry = state['jobs'][job['id']]
        if entry['status'] == 'done' and not entry.get('checkpoint'):
            raise ValueError(f"{job['id']} needs a commit and verified push before the next phase.")
        if entry['status'] != 'done':
            if entry['status'] != 'pending':
                raise ValueError(f"{job['id']} is {entry['status']}; reconcile its result before advancing.")
            if not all(state['jobs'][d]['status'] == 'done' for d in job['dependencies']):
                raise ValueError('Dependencies are not complete: ' + job['id'])
            return job
    return None


def phase_report(project, job, entry, artifact):
    checksum = hashlib.sha256()
    with artifact.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(chunk)
    relative = Path(entry['artifact'])
    data = dict(phase=job['id'], title=job['title'], kind=job['kind'],
                artifact=relative.name if relative.is_absolute() else str(relative),
                artifact_sha256=checksum.hexdigest(), artifact_bytes=artifact.stat().st_size,
                validation=entry['review'], completed_at=entry['completed_at'])
    path = project / 'progress' / (job['id'] + '.json')
    write_state(path, data)
    entry['phase_report'] = str(path.relative_to(project))
    entry['phase_report_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoint(project, entry, commit, remote, branch):
    def git(*arguments):
        environment = dict(os.environ, GIT_TERMINAL_PROMPT='0')
        return subprocess.check_output(['git', *arguments], cwd=project,
                                       env=environment, stderr=subprocess.PIPE).decode().strip()
    if entry['status'] != 'done':
        raise ValueError('Complete and inspect the phase before creating its checkpoint.')
    sha = git('rev-parse', '--verify', commit + '^{commit}')
    message = git('show', '-s', '--format=%B', sha)
    title, separator, description = message.partition('\n\n')
    if not separator or len(title.strip()) < 8 or len(description.strip()) < 20:
        raise ValueError('The phase commit needs a clear title and a substantive description.')
    report = entry['phase_report']
    # Read the committed report, not merely the current working file.
    committed = subprocess.check_output(['git', 'show', sha + ':' + report], cwd=project,
                                         stderr=subprocess.PIPE)
    if hashlib.sha256(committed).hexdigest() != entry['phase_report_sha256']:
        raise ValueError('The commit does not contain the reviewed phase report.')
    head = git('ls-remote', remote, 'refs/heads/' + branch)
    if not head:
        raise ValueError('The remote branch does not exist; push the phase commit first.')
    remote_sha = head.split()[0]
    if remote_sha != sha:
        git('fetch', remote, 'refs/heads/' + branch)
        git('merge-base', '--is-ancestor', sha, remote_sha)
    entry['checkpoint'] = dict(commit=sha, title=title, description=description,
                               remote=remote, branch=branch, remote_head=remote_sha,
                               verified_at=now())
    return entry['checkpoint']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['init', 'status', 'next']:
        commands.add_parser(name)
    for name in ['begin', 'finish', 'fail', 'retry', 'checkpoint']:
        child = commands.add_parser(name)
        child.add_argument('id')
        if name == 'finish':
            child.add_argument('--artifact', type=Path, required=True)
            child.add_argument('--note', required=True, help='Inspection or implementation validation outcome.')
        if name == 'fail':
            child.add_argument('--reason', required=True)
            child.add_argument('--uncertain', action='store_true')
        if name == 'checkpoint':
            child.add_argument('--commit', required=True)
            child.add_argument('--remote', default='origin')
            child.add_argument('--branch', default='main')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    lock = project / '.local/queue.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    import fcntl
    with lock.open('a') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        path, state, jobs = load(project)
        if args.command == 'init':
            write_state(path, state)
            result = dict(state_file=str(path), job_count=len(jobs), paid_requests=0)
        elif args.command == 'status':
            result = dict(jobs=[dict(id=job['id'], kind=job['kind'],
                                     **state['jobs'][job['id']]) for job in jobs])
        elif args.command == 'next':
            result = next_job(state, jobs) or dict(complete=True)
        else:
            if args.id not in state['jobs']:
                raise ValueError('Unknown job: ' + args.id)
            entry = state['jobs'][args.id]
            if args.command == 'begin':
                next_item = next_job(state, jobs)
                if not next_item or next_item['id'] != args.id:
                    raise ValueError('Only the next pending job may begin.')
                entry.update(status='running', started_at=now())
                result = next_item
            elif args.command == 'finish':
                if entry['status'] not in ['running', 'uncertain']:
                    raise ValueError('Only a started job or reconciled uncertain result can finish.')
                artifact = args.artifact
                artifact = artifact if artifact.is_absolute() else project / artifact
                artifact = artifact.resolve()
                if not artifact.is_file() or artifact.stat().st_size == 0:
                    raise ValueError('The artifact must exist and be nonempty.')
                try:
                    artifact = str(artifact.relative_to(project))
                except ValueError:
                    artifact = str(artifact)
                entry.update(status='done', artifact=artifact, review=args.note, completed_at=now())
                phase_report(project, next(job for job in jobs if job['id'] == args.id),
                             entry, project / artifact)
                result = dict(id=args.id, **entry)
            elif args.command == 'fail':
                if entry['status'] != 'running':
                    raise ValueError('Only a running job may fail.')
                entry.update(status='uncertain' if args.uncertain else 'failed',
                             reason=args.reason, stopped_at=now())
                result = dict(id=args.id, **entry)
            elif args.command == 'retry':
                if entry['status'] != 'failed':
                    raise ValueError('Retry requires a definite failure; reconcile running/uncertain requests first.')
                entry.update(status='pending', retry_requested_at=now())
                result = dict(id=args.id, **entry)
            else:
                result = checkpoint(project, entry, args.commit, args.remote, args.branch)
            write_state(path, state)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print('Queue stopped: ' + str(error), file=sys.stderr)
        sys.exit(2)
