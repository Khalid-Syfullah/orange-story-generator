---
name: orange-story-generator
description: Run the Orange story project's paintings, motion shots, WebGL implementation, and transitions sequentially with saved progress. Use for generating or resuming this project's prompt pack, not unrelated media tasks.
---

# Orange Story Generator

Run the project's approved prompt catalog one job at a time, inspecting each result and preserving the same art direction across all four chapters. A request to run the sequence authorizes the requested bounded run; do not ask for confirmation between ordinary jobs. Creating or installing this skill alone does not start paid generation.

## Locate the project and check access

Find the project in the current workspace or the user-specified directory. It must contain `prompts/generation-prompts.json` and `prompts/ORANGE-STORY-PROMPTS.md`. Do not silently select a different Orange repository. Read the project's applicable instructions and the prompt document once. Use this skill's `scripts/queue.py` with `--project <absolute-project-path>`; the helper is independent of where the skill is installed.

Use the user-selected Google tools: Gemini Image/Nano Banana for paintings and Veo for image-to-video. Inspect the currently exposed MCP tool schemas rather than inventing tool names or arguments. See [references/google-media.md](references/google-media.md) for provider prerequisites and job handling. If the tools are not exposed, explain the concrete missing connection and continue only jobs that do not require it. Do not substitute still-image zoom animations for generated motion or switch providers without authorization.

## Execute and resume

1. Initialize or load the saved ledger: `python3 <skill>/scripts/queue.py --project <project> init`. Initialization is local and makes no provider calls. `status` reports completed and blocked work; `next` returns the next full prompt and its dependencies.
2. Check prerequisites and available model options before beginning the first provider job. Save images under `outputs/paintings/`, clips under `outputs/motion/`, and implementation/review reports under `outputs/reports/`. Preserve the catalog prompts; record intentional corrections in the review report.
3. Call `begin <id>` immediately before the provider call or implementation work. This reserves the job durably. Submit one request for that job, await its actual result, and inspect the returned local artifact. Avoid parallel provider calls. For painting references or video inputs, use the approved dependency artifacts recorded in the ledger.
4. Use `finish <id> --artifact <file> --note <inspection-summary>` only after the output exists and passes the relevant review. This creates a tracked `progress/<id>.json` report containing the result's checksum and validation summary. Treat every queue job as a phase: commit that report and the phase's relevant source changes, then push the commit before starting the next job. Follow [references/git-checkpoints.md](references/git-checkpoints.md). Run `checkpoint <id> --commit <sha> --remote origin --branch main` after the push; the helper verifies the commit description, committed report, and remote branch. Only then can `next` advance. Visual inspection remains the agent's responsibility.
5. Stop on an unrepaired defect, missing prerequisite, definite provider error, or uncertain timeout. `fail <id> --reason <reason>` records a definite failure. Add `--uncertain` when a submitted operation may still be running or may have completed. Save any operation identifier in `outputs/reports/<id>.json`. On resume, reconcile that operation; never create a replacement request just because the session timed out. A definite failure can be reset with `retry <id>` once its cause is fixed; running/uncertain jobs cannot be reset automatically.

The queue contains 11 painting/composition jobs, 9 individual motion jobs (the builders prompt runs once for each approved construction view), the WebGL foundation, five transition jobs, and the final review: 27 jobs total. Respect a user-requested subset or stopping point. Never mark excluded jobs as completed just to advance the queue.

## Production decisions that matter

- Begin with 01A to establish the approved cast and color grade. Carry actual reference images forward, not just repeated descriptive text. Check round orange anatomy, fingers, botanical junctions, and stable architecture.
- 03A must reuse the exact 02C painting. Preserve it as an inset in a frame/wall composition; a CSS/WebGL composition with a separately generated frame plate is valid. Record the composition and its asset links. A freshly redrawn near-match breaks continuity.
- Generate each motion shot from its approved painting with one modest action per character. Review contact, gravity, cloth lag, fruit attachment, face identity, and the full shot. One-time gestures settle; they do not ping-pong. An anatomical defect requires an asset correction, not a shader disguise.
- The implementation jobs are prompts for the coding agent, not video-model inputs. Build the actual four-chapter site in this project using the approved media. Preserve the single canvas, crop-aware anchors, readable DOM, and the detailed Model → Work handoff from the catalog. For each implementation job, save a report referencing changed files, the preview, and meaningful checks. Do not claim completion from a plan or copied prompt.
- The final correction prompt is a review-and-repair instruction. Apply it to observed defects, not a blanket request to regenerate everything. Allow one focused correction attempt per defective asset under the existing run scope; stop and explain if it still fails. Do not automatically make a large number of paid retries.

The user has explicitly authorized committing and pushing after every phase for this project, including its public GitHub repository. Carry this out automatically without requesting approval between phases. A failed push blocks advancement, not the already completed generation: resume by publishing and verifying the existing result. Keep progress visible during the run, and finish with the artifact index, completed/remaining jobs, phase commit links, and concrete blockers. Credentials, raw generated media, and the local ledger stay out of Git by default; publish the phase reports and relevant project source. Do not publish credentials or unrelated personal files.
