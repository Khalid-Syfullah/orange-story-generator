# Commit and push after every phase

Every queue job is a phase. After its output passes inspection, `finish` creates `progress/<phase-id>.json`; this gives media-only phases a meaningful tracked result without adding large raw images/videos to Git. The report records the artifact's relative name, SHA-256, size, and validation. Keep secrets, private provider operation IDs, credentials, and signed download URLs out of the published report.

Stage the report and the files changed by that phase explicitly. Inspect the staged diff and run appropriate checks. Preserve unrelated changes. Create one commit with a clear imperative title identifying the phase, followed by a blank line and a description explaining what changed, why it matters, and what was validated. Use a temporary body file for multiline commit messages.

Example:

```text
Complete phase 01A: establish the Orange hero painting

Create the approved raised-orange composition and record its artifact checksum.
This establishes the cast, palette, and sky space used by later scenes.

Validation: inspected orange anatomy, hand contact, faces, and headline space.
```

Push the commit to the project's configured remote and branch, normally `origin/main`. Verify that the remote branch contains that commit. Call:

```sh
python3 <skill>/scripts/queue.py --project <project> checkpoint <phase-id> --commit <sha> --remote origin --branch main
```

The helper checks the commit's title/description, the exact committed phase report, and live remote reachability before unblocking the next job. If a push fails or its result is uncertain, reconcile the remote and retry only the publication. Do not regenerate media or create duplicate commits to recover a failed push. Resolve concurrent remote changes normally; do not force-push over another contributor.

If CLI authentication fails but the authorized GitHub connector works, publish the same reviewed tree through its Git tree/commit/ref tools, using a lease against the observed branch head. Include the full title and description in the connector's `message` argument. Fetch the published commit locally, verify identical file trees and a clean working tree before aligning local history, and checkpoint the actual remote commit SHA. Preserve any local commit replaced during synchronization in a backup branch.
