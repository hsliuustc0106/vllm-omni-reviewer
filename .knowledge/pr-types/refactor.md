**Critical Focus:**
- Behavior preservation (no functional changes)
- Test coverage maintained or improved
- Clear migration path if APIs change
- Code quality improvements justified
- No performance regressions

**Questions to Ask:**
- Why is this refactoring necessary?
- Are there functional changes hidden in the refactor?
- Do all existing tests still pass?
- Is the new structure clearer?

**Using Linked Issue Context:**
- Verify refactor addresses technical debt mentioned in issue
- Check if the issue mentions specific pain points - are they resolved?
- Look for design goals in the issue - does the refactor achieve them?
- If the issue mentions performance, verify no regressions

**Common Issues:**
- Hidden functional changes
- Breaking existing tests
- Over-engineering
- No clear improvement
- Performance regressions

**vllm-omni Specific Considerations:**
- Multi-modal architecture refactoring
- Distributed execution code organization
- Model registry refactoring
- Quantization infrastructure
- API layer refactoring
