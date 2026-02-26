**Critical Focus:**
- API compatibility with existing code
- Backward compatibility preservation
- Clear documentation of API changes
- Breaking changes clearly marked
- Migration path for deprecated APIs

**Questions to Ask:**
- Does this break existing user code?
- Are breaking changes necessary?
- Is there a migration path?
- Are API changes documented?

**Using Linked Issue Context:**
- Verify API changes match feature request from issue
- Check if the issue mentions backward compatibility concerns
- Look for user feedback in the issue - does the API address it?
- If the issue mentions API design, does the PR follow it?

**Common Issues:**
- Undocumented breaking changes
- No migration path for deprecated APIs
- Inconsistent API design
- Missing API documentation
- No backward compatibility testing

**vllm-omni Specific Considerations:**
- OpenAI-compatible API endpoints
- Multi-modal API design
- Streaming API support
- Distributed execution API
- Compatibility with vLLM API
