# Google media jobs

This workflow uses Google-maintained reference MCP servers from [GoogleCloudPlatform/genmedia-creative-studio](https://github.com/GoogleCloudPlatform/genmedia-creative-studio/tree/main/experiments/mcp-genmedia). The repository describes them as reference software, not an officially supported Google product.

The prepared Codex connection names are `google-gemini-image` and `google-veo`. Connection names are not callable tool names. Discover the actual loaded tools and schemas. Typically the image tool is `nanobanana_image_generation`; image-to-video is `veo_i2v`.

Prerequisites: Google Cloud project, enabled billing and model API access, Application Default Credentials, and a private Cloud Storage bucket for Veo source/output objects. A Gemini API key alone does not authenticate these Vertex AI servers. Account sign-in and billing setup may require the account owner. Do not put keys, tokens, or credential files into the project or GitHub.

For images, supply the full job prompt, approved reference images where applicable, 16:9 landscape, and a local output directory/filename. Choose a currently available Gemini image model; retain the project choices unless unavailable. Produce one approved composition per job. 03A is a composition preserving 02C, rather than an independent re-imagination of it.

For motion, inspect and use the approved `source_asset` from the ledger. Upload only that project asset to the user-owned bucket as required by the selected tool. Request one video, generally eight seconds where supported, in 16:9 with the motion prompt from the catalog. Use the tool's current parameter schema and supported model constraints. The originally chosen starting model was `veo-3.1-fast-generate-001`; verify current availability before a new run. Record the returned operation/asset metadata and downloaded local output. Prompt duration and loop direction are guidance, not a guarantee of a clean result.

Never submit two generations concurrently. Do not automatically retry a timed-out paid request. Reconcile a provider operation before deciding whether to retry. Use only the minimum project/bucket access required for these jobs; do not create service-account keys or change broad IAM permissions as a workaround.

The queue helper records local execution state but does not submit API calls, sign in, or verify visual quality. The Codex agent running the skill performs those parts using the connected tools.
