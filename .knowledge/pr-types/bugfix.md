**Critical Focus:**
- Is there a regression test to prevent this bug from recurring?
- Is the root cause clearly understood and documented?
- Are there similar bugs elsewhere in the codebase?
- Does the fix address symptoms or root cause?
- What's the impact if this isn't fixed?

**Questions to Ask:**
- How was this bug discovered?
- Are there edge cases not covered by the fix?
- Does the fix introduce new failure modes?
- Is the fix minimal or does it refactor unnecessarily?

**Using Linked Issue Context:**
- Verify the fix addresses the exact problem described in the linked issue
- Check if the issue mentions reproduction steps - are these covered in tests?
- Look for related issues mentioned in the original issue discussion
- Validate that the fix scope matches the issue scope (not over-fixing or under-fixing)
- If the issue describes impact/severity, verify the fix is appropriate for that level

**Common Issues:**
- Missing regression tests
- Incomplete root cause analysis
- Fix only addresses symptoms
- Over-engineering the solution
- Not checking for similar bugs elsewhere

**vllm-omni Specific Considerations:**
- Race conditions in async execution paths
- Dtype mismatches between model components
- KV cache management bugs
- Model config parsing errors
