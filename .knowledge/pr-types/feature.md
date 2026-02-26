**Critical Focus:**
- Is there comprehensive test coverage for the new functionality?
- Is user-facing documentation updated?
- Are breaking changes clearly documented?
- Does this fit the project architecture?
- What's the performance impact?

**Questions to Ask:**
- Why this approach vs alternatives?
- How does this interact with existing features?
- What happens when this feature is disabled?
- Are there backward compatibility concerns?

**Using Linked Issue Context:**
- Verify the implementation matches the feature requirements in the issue
- Check if the issue mentions use cases - are these covered in examples/tests?
- Look for design discussions in the issue - does the PR follow agreed approach?
- Validate that all acceptance criteria from the issue are met
- If the issue mentions constraints (performance, memory), verify they're satisfied

**Common Issues:**
- Missing test coverage
- No documentation
- Unclear edge case handling
- Performance impact not measured
- Breaking changes not documented

**vllm-omni Specific Considerations:**
- Integration with async_chunk execution model
- Compatibility with distributed execution
- Impact on memory usage and KV cache
- Streaming output support
