# vllm-omni Architecture

## Overview

vllm-omni extends vLLM for omni-modal (multi-modal) model serving, supporting text, image, video, and audio generation. It provides a unified inference engine with OpenAI-compatible APIs for both LLM and diffusion models.

**Key Differentiators from vLLM:**
- Multi-stage pipeline architecture (e.g., Thinker → Talker → Code2Wav)
- Diffusion Transformer (DiT) model support
- Inter-stage communication via shared memory connectors
- Stage-level concurrency control

---

## Five-Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│  1. User Interface Layer                            │
│     OpenAI-compatible API, CLI, Python SDK          │
├─────────────────────────────────────────────────────┤
│  2. Orchestration Layer                             │
│     Omni, AsyncOmni - coordinates stages            │
├─────────────────────────────────────────────────────┤
│  3. Engine Layer                                    │
│     ModelExecutor, Scheduler, KV cache management   │
├─────────────────────────────────────────────────────┤
│  4. Execution Layer                                 │
│     Workers (GPUARWorker, GPUGenerationWorker)      │
├─────────────────────────────────────────────────────┤
│  5. Model Layer                                     │
│     OmniLLM, OmniDiffusion, model implementations   │
└─────────────────────────────────────────────────────┘
```

---

## Key Directories

| Directory | Purpose | Critical? |
|-----------|---------|-----------|
| `vllm_omni/entrypoints/` | API server, CLI entry points | High |
| `vllm_omni/engine/` | Async/sync engine, scheduler | **Critical** |
| `vllm_omni/model_executor/` | Model execution, weight loading | **Critical** |
| `vllm_omni/diffusion/` | Diffusion model support | High |
| `vllm_omni/connectors/` | Inter-stage communication | High |
| `vllm_omni/stages/` | Stage definitions (LLM, diffusion) | High |
| `vllm_omni/config/` | Configuration classes | Medium |
| `vllm_omni/utils/` | Utility functions | Low |

---

## Core Components

### Entry Points

**Synchronous:** `Omni` class
```python
from vllm_omni import Omni
llm = Omni(model="Qwen/Qwen2.5-Omni-7B")
outputs = llm.generate("Hello")
```

**Asynchronous:** `AsyncOmni` class
```python
from vllm_omni import AsyncOmni
llm = AsyncOmni(model="Qwen/Qwen2.5-Omni-7B")
outputs = await llm.generate("Hello")
```

### Stage Types

| Type | Worker Classes | Use Case |
|------|---------------|----------|
| `llm` | `GPUARWorker`, `GPUGenerationWorker` | Text generation, multimodal understanding |
| `diffusion` | Diffusion-specific workers | Image/video generation |

### Connectors

| Connector | Use Case | Performance |
|-----------|----------|-------------|
| `OmniShmConnector` | Same-machine inter-process | Fastest |
| `OmniZmqConnector` | Distributed/multi-node | Network-capable |

---

## Multi-Stage Pipeline

### Example: Qwen-Omni Audio Generation

```
┌─────────┐     ┌─────────┐     ┌───────────┐
│ Thinker │ ──▶ │ Talker  │ ──▶ │ Code2Wav  │
│ (LLM)   │     │ (LLM)   │     │ (Audio)   │
└─────────┘     └─────────┘     └───────────┘
     │               │                │
   Text/Audio     Text Code      Audio Output
   Understanding  Generation     Synthesis
```

### Configuration (YAML)

Stages are configured via YAML files:
```yaml
stages:
  - name: thinker
    type: llm
    model: Qwen/Qwen2.5-Omni-7B
  - name: talker
    type: llm
    model: Qwen/Qwen2.5-Omni-7B
  - name: code2wav
    type: audio
    model: Qwen/Code2Wav
```

---

## Supported Models

### LLM Models (OmniLLM)
- Qwen3-Omni
- Qwen2.5-Omni

### Diffusion Models (OmniDiffusion)
- Z-Image
- Qwen-Image
- Wan2.2 (video)
- FLUX

---

## Data Flow

```
Request → API Layer → AsyncOmni/Omni
                         │
                         ▼
                    Stage Coordinator
                    (YAML config)
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Stage 1        Stage 2        Stage N
      (Worker)       (Worker)       (Worker)
          │              │              │
          └──────────────┴──────────────┘
                         │
                    OmniConnector
                    (Shm/Zmq)
                         │
                         ▼
                    Response
```

---

## Memory Management

### KV Cache (LLM Stages)
- Paged attention inherited from vLLM
- Block-based memory allocation
- Prefix caching for repeated contexts

### Diffusion Latent Cache
- Intermediate latent storage
- Timestep-based scheduling
- Memory-pressure aware

---

## Review Considerations

### Critical Paths (High Impact)
- `vllm_omni/engine/` — scheduler changes affect all workloads
- `vllm_omni/model_executor/` — model loading bugs break inference
- `vllm_omni/connectors/` — communication bugs cause hangs/crashes

### High-Risk Patterns
1. **Stage coordination changes** — can break multi-stage pipelines
2. **Memory management in connectors** — shared memory leaks
3. **Worker lifecycle changes** — affect tensor parallelism

### Testing Requirements
- LLM stages: Test with actual model inference
- Diffusion stages: Test generation quality
- Connectors: Test under load, verify no memory leaks
- Multi-stage: Test end-to-end pipelines

---

## Common Pitfalls

### Connector State
Connectors use shared memory. Changes to connector logic must handle:
- Proper cleanup on error paths
- Memory barrier semantics
- Process crash recovery

### Stage Configuration
Stage configs are loaded at init time. Runtime changes require:
- Full pipeline teardown
- Config validation
- State migration if needed

### Async vs Sync
`AsyncOmni` uses different code paths than `Omni`. Changes must:
- Test both entry points
- Verify async context handling
- Check for blocking calls in async path
