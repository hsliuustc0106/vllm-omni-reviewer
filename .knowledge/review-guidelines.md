# Critical Review Guidelines

## Summary Structure

### Good Example (Pros/Cons):
```
This PR adds FP8 quantization support for Wan 2.2 transformer.

**Pros:**
- Follows established Z-Image pattern consistently
- Threads quant_config through all 6 transformer classes correctly
- Includes CLI support with clear help text
- Backward compatible (quant_config defaults to None)

**Cons:**
- No test coverage for quantization functionality
- Claims "significant memory reduction" but provides no memory measurements
- Missing type annotation in create_transformer_from_config
- No documentation explaining when to use FP8 or expected trade-offs
- Test results show only latency, not actual memory usage

Overall: Implementation is solid but lacks validation. Need tests and measurements before merge.
```

### Bad Example (Too Positive):
```
This PR adds FP8 quantization support. The implementation follows good patterns and includes CLI support. The code is well-structured and ready to merge.
```

## Test Coverage Examples

### Critical Questions to Ask:

**For new features:**
- "Where are the tests for this new functionality?"
- "How do we know this works correctly?"
- "What happens if [edge case]?"

**For bug fixes:**
- "Is there a regression test?"
- "How was this bug discovered?"
- "Are there similar bugs elsewhere?"

**For performance optimizations:**
- "Where are the benchmark results?"
- "What's the memory usage before/after?"
- "Is this measured on realistic workloads?"

### Example Comments:

**Good (Critical):**
```
This PR adds quantization but provides no test coverage. We need tests to verify:
1. FP8 quantization actually reduces memory (before/after measurements)
2. Output quality remains acceptable
3. Invalid configs are handled gracefully
4. The ignored_layers parameter works correctly
Without tests, we can't validate the claims or prevent regressions.
```

**Bad (Too Accepting):**
```
The quantization implementation looks good.
```

## Performance Claims Examples

### Critical Questions:

- "Where are the measurements?"
- "What's the baseline for comparison?"
- "Is this tested on realistic data?"
- "What's the quality trade-off?"

### Example Comments:

**Good (Demanding Evidence):**
```
The PR claims "significant memory reduction" but the test results only show latency metrics. We need:
- Peak memory usage comparison (FP8 vs BF16)
- VRAM consumption measurements
- Quality metrics (FID/CLIP scores) to ensure quantization doesn't degrade output
```

**Bad (Accepting Claims):**
```
Good performance optimization.
```

## Design Questions Examples

### Critical Questions:

- "Why this approach vs alternatives?"
- "Is this the right abstraction?"
- "Does this fit the architecture?"
- "What are the trade-offs?"

### Example Comments:

**Good (Questioning Design):**
```
Storing a live reference to the mutable request object could lead to race conditions. The request's state may change between enqueue and send time. Consider capturing immutable snapshots of needed fields instead.
```

**Bad (Accepting Design):**
```
The design looks good.
```
