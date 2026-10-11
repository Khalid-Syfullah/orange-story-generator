# ChatGPT native media jobs

The user selected native ChatGPT generation for this project. The queue helper tracks jobs; the Codex agent makes the actual native tool calls. Keep the existing 27-job catalog and ledger intact when changing tools.

## Paintings

Use the available `imagegen` skill and built-in `image_gen.imagegen` capability (exposed in this session as `image_gen__imagegen`). Inspect the actual schema before calling; do not invoke an image API, the imagegen CLI, or a third-party connector. The built-in tool needs no `OPENAI_API_KEY` or Google setup. Its availability and included usage limits depend on the session/account; if unavailable, stop before reserving the job.

1. Read the full painting job prompt and resolve its approved `reference_assets` from the ledger. Inspect each local reference with `view_image` before using it. Pass the local paths through `referenced_image_paths`, identifying each reference's purpose in the prompt. For a genuinely new image with no references, omit both reference arguments. Use `num_last_images_to_include` only when required references have no local path; never supply both reference mechanisms.
2. Request one original painterly composition per job. Describe landscape 16:9 framing and clear editorial reading areas in the prompt; the current built-in schema has no aspect-ratio, model, size, count, or destination parameter. Use `transparent_background: false` for complete paintings. Preserve the catalog's cast, citrus anatomy, palette, brushwork, and grounded gestures.
3. Call `begin` immediately before generation. Await the single call's real completion and show its returned image. Generation can take several minutes; use the image tool's supported yield/wait flow. A timeout is not evidence of failure: reconcile the existing call before another submission.
4. Use the returned local asset path when available. Copy the approved file into `outputs/paintings/<job-id>.<actual-extension>` and inspect that saved file. Built-in assets may be saved under the Codex generated-images directory; do not pass a made-up destination argument or invent an output path. If no local asset can be retrieved, preserve the result and report that saving is blocked; do not mark the phase complete or regenerate merely to obtain a filename.
5. Record the actual tool and inspection in the phase note/report, then follow the existing finish, commit, push, and checkpoint procedure. Carry saved approved references into the next job. For 03A, preserve the exact 02C pixels as an inset in a CSS/WebGL composition with a separate frame plate rather than asking the image model to redraw 02C.

## Motion

**Capability check, October 11, 2026:** this session exposes native image generation but no native generative video tool. Third-party video connectors and timeline renderers do not satisfy this provider choice. Official OpenAI documentation also lists the old Sora 2 models and Videos API as removed on September 24, 2026, with no replacement listed. Do not configure those retired endpoints or infer native app availability from old Sora examples.

On every resumed run, inspect the currently exposed tools. If a native image-to-video tool is actually available, use its current schema and supported inputs, duration, aspect ratio, and model options. Supply the approved `source_asset` painting and exact motion prompt; ask for one restrained shot, roughly six to eight seconds where supported, with no audio required. Preserve supported contact points, character identity, fruit attachment, and natural cloth/foliage timing. Inspect the whole clip, including first/last frames and settling, before accepting it.

If no suitable native tool is available, stop at the first pending motion job before `begin`. Report the job ID, approved source image, and prompt location. Leave later jobs pending and preserve all completed painting checkpoints. Never label a camera pan over a still, an external-provider clip, a prompt file, or an empty placeholder as native generated video. Resume automatically only after the required capability exists or the user changes the provider choice. If the user explicitly supplies an already generated native clip, inspect it and record its supplied provenance before completing the matching job; do not claim it was generated in this session.

Submitted operations with uncertain outcomes follow the queue's existing reconciliation rule. Save operation metadata locally, keep private URLs out of published progress reports, and avoid automatic duplicate submissions.

## Official references

- [Image generation in ChatGPT and Codex](https://learn.chatgpt.com/docs/image-generation): native image workflow, reference images, and usage.
- [OpenAI API deprecations](https://developers.openai.com/api/docs/deprecations): dated Sora 2 / Videos API retirement notice. Recheck current official documentation if a future session exposes native video generation.
