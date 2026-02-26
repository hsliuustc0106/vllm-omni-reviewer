# Critical Review Guidelines

## Conciseness Requirements

**Word Limits:**
- Standard review: 150-250 words maximum
- Inline review summary: 50-100 words maximum
- Each inline comment: 2-4 sentences maximum

**Banned Phrases (generic praise):**
- "solid", "generally", "looks good", "well done", "nice work", "great job"
- "comprehensive", "well structured", "good implementation"
- Any phrase that doesn't reference specific code locations

**Every sentence must:**
- Add new information
- Reference specific file:line locations
- Demand evidence or question assumptions
- Provide actionable feedback

## Summary Structure

### Good Example (Concise & Critical):
```
This PR adds FP8 quantization for Wan 2.2 transformer.

**Red Flags:**
- Missing tests: Yes - no test coverage for quantization
- Unvalidated claims: Yes - claims "significant memory reduction" without measurements
- Missing error handling: No
- Breaking changes: No
- Security concerns: No

**Pros:**
- Follows Z-Image pattern (wan.py:150-180)
- Threads quant_config through 6 classes correctly
- Backward compatible (defaults to None)

**Cons:**
- No tests for quantization functionality
- No memory measurements despite performance claims
- Missing type annotation (wan.py:73)
- No documentation for when to use FP8

**Verdict:** Request changes - need tests and measurements.
```
(Word count: 142)

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

## Inline Comment Examples

**Good (Critical & Concise):**
```
Missing regression test for this bug fix. Add a test that reproduces the original issue and verifies this fix prevents it. Without this, we risk reintroducing the bug.
```

**Bad (Too verbose):**
```
It would be really beneficial if we could add some test coverage here to ensure that this functionality works as expected and to prevent any potential regressions in the future. This would help maintain code quality and give us confidence in the changes.
```

**Good (Demands Evidence):**
```
Where are the memory measurements? The PR claims "50% reduction" but provides no before/after data. Run benchmarks with realistic workloads and report peak VRAM usage.
```

**Bad (Accepts Claims):**
```
The performance optimization looks promising. It would be good to have some benchmarks to validate the improvements.
```

## Red Flags Checklist (Mandatory)

Every review MUST explicitly check and report on these:

1. **Missing tests:**
   - New feature without tests?
   - Bug fix without regression test?
   - Changed behavior without test updates?

2. **Unvalidated claims:**
   - Performance claims without benchmarks?
   - Memory claims without measurements?
   - Quality claims without metrics?

3. **Missing error handling:**
   - No validation of inputs?
   - No handling of failure cases?
   - Silent failures or unclear errors?

4. **Breaking changes:**
   - API changes without documentation?
   - Behavior changes without migration guide?
   - Removed features without deprecation?

5. **Security concerns:**
   - Input validation missing?
   - Resource exhaustion possible?
   - Privilege escalation risks?

**Format in review:**
```
**Red Flags:**
- Missing tests: Yes - no coverage for X functionality
- Unvalidated claims: Yes - claims Y without measurements
- Missing error handling: No
- Breaking changes: No
- Security concerns: No
```
