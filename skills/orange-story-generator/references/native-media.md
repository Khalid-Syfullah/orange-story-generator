# ChatGPT native paintings and Google video jobs

The user selected ChatGPT native images and connected Google video generation for this project. The queue helper tracks jobs; the Codex agent makes the actual generation tool calls. Keep the existing 27-job catalog and ledger intact when changing tools.

## Paintings

Use the available `imagegen` skill and built-in `image_gen.imagegen` capability (exposed in this session as `image_gen__imagegen`). Inspect the actual schema before calling; do not invoke an image API, the imagegen CLI, or a third-party connector. The built-in tool needs no `OPENAI_API_KEY` or Google setup. Its availability and included usage limits depend on the session/account; if unavailable, stop before reserving the job.

1. Read the full painting job prompt and resolve its approved `reference_assets` from the ledger. Inspect each local reference with `view_image` before using it. Pass the local paths through `referenced_image_paths`, identifying each reference's purpose in the prompt. For a genuinely new image with no references, omit both reference arguments. Use `num_last_images_to_include` only when required references have no local path; never supply both reference mechanisms.
2. Request one original painterly composition per job. Describe landscape 16:9 framing and clear editorial reading areas in the prompt; the current built-in schema has no aspect-ratio, model, size, count, or destination parameter. Use `transparent_background: false` for complete paintings. Preserve the catalog's cast, citrus anatomy, palette, brushwork, and grounded gestures.
3. Call `begin` immediately before generation. Await the single call's real completion and show its returned image. Generation can take several minutes; use the image tool's supported yield/wait flow. A timeout is not evidence of failure: reconcile the existing call before another submission.
4. Use the returned local asset path when available. Copy the approved file into `outputs/paintings/<job-id>.<actual-extension>` and inspect that saved file. Built-in assets may be saved under the Codex generated-images directory; do not pass a made-up destination argument or invent an output path. If no local asset can be retrieved, preserve the result and report that saving is blocked; do not mark the phase complete or regenerate merely to obtain a filename.
5. Record the actual tool and inspection in the phase note/report, then follow the existing finish, commit, push, and checkpoint procedure. Carry saved approved references into the next job. For 03A, preserve the exact 02C pixels as an inset in a CSS/WebGL composition with a separate frame plate rather than asking the image model to redraw 02C.

## Motion with the connected Google tool

Discover an actually exposed Google video-generation tool with image-to-video support, such as the connected Veo tool. Connection labels in configuration are not callable tool names and do not establish that a server is enabled or authenticated. Inspect the loaded schema and required access before `begin`; do not invent tool names, project IDs, buckets, or arguments. Use the tool's documented upload/asset handling when it requires remote input and pass only the approved project painting.

Supply the approved `source_asset` painting and exact motion prompt. Use the tool's current supported inputs, duration, aspect ratio, and model options; request one restrained shot, roughly six to eight seconds where supported, with no audio required. Preserve contact points, character identity, fruit attachment, and natural cloth/foliage timing. Inspect the whole clip, including first/last frames and settling, before accepting it. Save the actual returned clip under `outputs/motion/` and record Google generation provenance in the phase note/report.

If the Google tool is unavailable or unauthenticated, stop at the first pending motion job before `begin`. Report the job ID, approved source image, prompt location, and concrete missing access. Leave later jobs pending and preserve all completed painting checkpoints. Never label a camera pan over a still, a prompt file, or an empty placeholder as generated video. On resume, recheck the connection and continue the pending job when access is available.

Use an exposed polling/status tool to await a submitted Google operation when applicable. Save its operation identifier and metadata locally, keep private URLs and credentials out of published progress reports, and avoid automatic duplicate submissions after uncertain outcomes. Follow the queue's existing reconciliation, inspection, commit, push, and checkpoint rules.

## Image reference

- [Image generation in ChatGPT and Codex](https://learn.chatgpt.com/docs/image-generation): native image workflow, reference images, and usage. Google video arguments must come from the connected tool's current schema rather than from this image documentation.
