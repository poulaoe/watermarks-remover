# MarkLLM-enabled service image

This optional image combines the existing Watermarks Remover HTTP service with
the repository's MarkLLM research harness.

## Build

From the repository root:

```sh
docker build -f service/Dockerfile.markllm-service -t watermarks-remover-full service/
```

The image installs CPU PyTorch and the pinned dependencies in
`service/scripts/requirements-markllm.txt`, then checks out the MarkLLM source
at the pinned commit used by the existing harness Dockerfile.

## Deploy

Use `service/Dockerfile.markllm-service` as the Dockerfile path for the
existing service deployment. Keep the service's current API-key and bridge
environment variables unchanged. Set:

- `MARKLLM_DIR=/opt/markllm`
- `WATERMARKS_MARKLLM_SCHEME=kgw` (or `synthid` only when that is the known
  generation scheme)
- `HF_HOME=/home/remover/.cache/huggingface`

The first detector run may need to download the default model
(`facebook/opt-1.3b`) from Hugging Face. Ensure the service has outbound access
and enough memory/disk; CPU inference can be slow. Persist `HF_HOME` across
deploys if the platform supports a persistent disk.

## Important limits

MarkLLM is a research detector, not a general AI-authorship detector. It can
only give a meaningful watermark result when the source scheme, model,
configuration, and watermark keys match those used during generation. The
default scheme is KGW. A negative result does not establish that text was
human-written or that no other watermark exists.

This image does not add a general detector for every commercial AI system.
The upstream detector status endpoint remains the source of truth for what is
actually available at runtime.
