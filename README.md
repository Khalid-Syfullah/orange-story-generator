# Orange Story Generator

A dedicated prompt and automation project for Orange's four-chapter painted website: The Model, The Work, The Terms, and Questions.

- [Complete production prompts](prompts/ORANGE-STORY-PROMPTS.md)
- [Structured prompt catalog](prompts/generation-prompts.json)
- [Sequential generation skill](skills/orange-story-generator/SKILL.md)

Open `orange-story-generator.code-workspace` in VS Code. The original reference recording is local to its owner and is not included in this repository.

## Run with Codex

Invoke the installed skill from this project:

> Use $orange-story-generator to run this project's prompts automatically one by one. Resume from saved progress, use ChatGPT's built-in image generation and native video generation when available, inspect each result, and commit and push after each phase. Pause at a motion job if native video generation is unavailable, then resume when access exists.

This is an agent-driven automation: the skill guides Codex through real tool calls and implementation jobs. The Python helper tracks progress and prevents duplicate submissions; it does not generate media by itself. Skill creation does not start the paid generation run.

Paintings use the built-in `image_gen` tool, one image at a time, with approved paintings carried forward as references. No Google Cloud project, storage bucket, or API key is needed for this image workflow. See [native media handling](skills/orange-story-generator/references/native-media.md).

Native video generation is **not exposed in the current session** (checked October 11, 2026). The nine motion jobs retain their prompts and approved painting dependencies, but pause before submission until a native video tool is available. The agent checks capabilities again on each resumed run. It must not substitute another provider, an API, or still-image zoom clips. Website implementation follows the approved motion jobs; this configuration update does not generate assets or complete the site.

## Preview the queue without generating anything

```sh
python3 skills/orange-story-generator/scripts/queue.py init
python3 skills/orange-story-generator/scripts/queue.py status
python3 skills/orange-story-generator/scripts/queue.py next
```

The 27-job queue runs paintings/compositions, individual motion shots, the WebGL foundation, chapter transitions, and final review. Every completed job creates a tracked `progress/<id>.json` report. The agent commits it with a clear title and description, pushes the phase changes, and verifies the remote commit before advancing. A failed push pauses the queue without repeating generation. See [phase checkpoints](skills/orange-story-generator/references/git-checkpoints.md).

Raw results go in `outputs/`; local execution state goes in `.local/run-state.json`. Both are ignored by Git, along with credentials and build dependencies. The smaller phase reports and project source are published. Keep a separate backup of generated outputs.

Run the local reliability checks with:

```sh
python3 -m unittest discover -s tests -v
```

The skill source is versioned here. Install it by copying `skills/orange-story-generator` into your Codex skills directory. Keep that installed copy synchronized when editing the skill.
