# PR #1412: [Quantization] Add FP8 quantization support for Wan 2.2 transformer

## Summary

**Author:** lishunyang12 | **Files changed:** 6

Adds FP8 W8A8 quantization support for Wan 2.2 video transformer by threading quant_config through all parallel linear layers.

**Pros:**
- Follows established Z-Image pattern consistently
- Threads quant_config through all 6 transformer classes correctly
- Includes comprehensive CLI support (--quantization, --ignored-layers)
- Backward compatible (quant_config defaults to None)
- Proper use of TYPE_CHECKING to avoid runtime import overhead

**Cons:**
- **No test coverage** for quantization functionality
- **No memory measurements** despite claiming "significant memory reduction"
- Missing type annotation in create_transformer_from_config (line 73)
- **No documentation** explaining when to use FP8 or expected trade-offs
- Test results show latency but not actual memory usage or quality metrics

**Overall:** Implementation is technically sound but lacks validation. Cannot verify the core value proposition (memory reduction) without measurements. Need tests and benchmarks before merge.

## Critical Issues

1. **Missing test coverage** - Major feature with zero tests
2. **Unvalidated performance claims** - No memory measurements provided
3. **Type safety gap** - Missing QuantizationConfig type annotation
4. **Documentation gap** - Users don't know when/how to use this feature

## Inline Comments

### vllm/model_executor/models/wan.py:73
Missing type annotation for quant_config parameter. Should be `quant_config: QuantizationConfig | None = None` for type safety.

### vllm/model_executor/models/wan.py:150
The quantization is applied to all ParallelLinear layers, but there's no validation that the config is compatible with these layer types. What happens if someone passes an incompatible quantization scheme?

### tests/models/test_wan.py:0
This PR adds a major feature (FP8 quantization) but includes no tests. We need:
1. Test that quantization actually reduces memory (measure before/after)
2. Test that ignored_layers parameter works correctly
3. Test error handling for invalid configs
4. Regression test to ensure non-quantized path still works

### README.md:0
No documentation for the new quantization feature. Users need to know:
- When to use FP8 quantization
- Expected memory savings
- Quality trade-offs
- How to use --quantization and --ignored-layers flags
