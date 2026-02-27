# Critical Review Guidelines

## Inline-Only Review Approach

**Philosophy:**
- Inline comments are the review - no summary needed
- Each comment targets a specific critical issue at a specific line
- Let the inline comments speak for themselves
- Maximum 5 comments per review - only the most critical issues

## Conciseness Requirements

**Word Limits:**
- Standard review (if needed): 150-250 words maximum
- Inline comments: 2-4 sentences maximum each
- Maximum 5 inline comments per PR

**Banned Phrases (generic praise):**
- "solid", "generally", "looks good", "well done", "nice work", "great job"
- "comprehensive", "well structured", "good implementation"
- Any phrase that doesn't reference specific code locations

**Every inline comment must:**
- Target a critical blocker or high-impact issue
- Demand specific action or evidence
- Be 2-4 sentences maximum
- Reference the specific line it's commenting on

## Review Priority

**Focus on Critical Issues Only (Maximum 5 comments):**
1. **Missing tests** - highest priority
2. **Unvalidated claims** - demand measurements/evidence
3. **Security concerns** - input validation, resource exhaustion
4. **Design flaws** - architectural issues, race conditions
5. **Breaking changes** - undocumented API changes

**Skip:**
- Minor style issues
- Nitpicks
- Nice-to-haves
- Issues already covered by linters

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

**Philosophy: Each inline comment should be self-contained and actionable. No summary needed.**

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

**Good (Questions Design):**
```
Hard-coding 16 steps will break with future model variants. Add config validation to ensure num_ar_steps==16, or make the implementation flexible to handle different step counts.
```

**Bad (Generic):**
```
Consider making this more flexible for future use cases.
```

## Smart Context Fetching

**When to Fetch Additional Context:**

Use context-fetching tools when posting critical inline comments that need more information:

### 1. Import/Dependency Analysis

**Scenario:** New imports that might have performance or compatibility implications

**Tools to use:**
```
extract_imports_from_diff(pr_number)
fetch_symbol_definition("ParallelLinear", search_paths=["vllm/"])
```

**Example inline comment:**
```
This imports ParallelLinear from vllm.model_executor.layers.linear. I checked the definition and it requires tensor parallelism setup. Verify this model supports TP and add error handling if TP is not configured.
```

### 2. Unclear Code Context

**Scenario:** The 3-line diff context isn't enough to understand the change

**Tools to use:**
```
fetch_file_context("vllm/worker/gpu_model_runner.py", line=285, context_lines=30)
```

**Example inline comment:**
```
This modifies the model loading sequence. Looking at the surrounding code (lines 260-310), this breaks the initialization order - KV cache must be allocated before CUDA graphs. Move this after line 295.
```

### 3. Configuration File Checks

**Scenario:** Code changes that might require config updates

**Tools to use:**
```
check_related_config_files(pr_number)
```

**Example inline comment:**
```
Adding a new model requires updating the model registry. I checked and vllm/model_executor/models/__init__.py needs to import and register Qwen3TTS. Add the registration in __init__.py.
```

## Context Fetching Limits

**Maximum per review:**
- 3-5 context fetches total
- 20-50 lines per fetch_file_context call
- 3 results max from fetch_symbol_definition

**Don't fetch context for:**
- Minor style issues
- Obvious problems that don't need verification
- Issues where the diff provides enough context
- Nice-to-have improvements

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
