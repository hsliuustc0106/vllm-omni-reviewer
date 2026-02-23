# vllm-omni Architecture

## Overview
vllm-omni is a fork/extension of vLLM focused on omni-modal (multi-modal) model serving.
It extends vLLM's high-throughput LLM inference engine with support for additional modalities.

## Key Areas
- **Engine**: Core inference engine, scheduling, and memory management
- **Model support**: Model definitions, weight loading, and quantization
- **API server**: OpenAI-compatible API endpoints
- **Multimodal**: Processing pipelines for non-text modalities (vision, audio)
- **Sampling**: Token sampling strategies and parameters
- **Worker**: Distributed execution and tensor parallelism

## Important Directories
- `vllm/` — main source code
- `vllm/model_executor/` — model execution layer
- `vllm/engine/` — async and sync engine implementations
- `vllm/entrypoints/` — API server and CLI entry points
- `vllm/multimodal/` — multimodal input processing
- `tests/` — test suite

## Review Considerations
- Changes to the engine or scheduler can have broad performance impact
- Model changes should be tested with the specific model architectures affected
- API changes must maintain OpenAI compatibility where applicable
- Memory management changes need careful review for correctness
