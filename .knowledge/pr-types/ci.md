**Critical Focus:**
- Test coverage for new code paths
- CI reliability (no flaky tests)
- Build reproducibility
- Test execution time
- Clear failure messages

**Questions to Ask:**
- Do the tests cover edge cases?
- Are the tests deterministic?
- What's the impact on CI runtime?
- Are test dependencies clearly specified?

**Using Linked Issue Context:**
- Verify CI fix addresses the specific failure mentioned in issue
- If the issue mentions flaky tests, check if root cause is fixed
- Look for reproduction steps in the issue - are they now tested?
- Check if the issue mentions missing test coverage - is it now added?

**Common Issues:**
- Flaky tests
- Slow test execution
- Missing test coverage
- Unclear test failure messages
- Test dependencies not isolated

**vllm-omni Specific Considerations:**
- Multi-modal model testing
- Distributed execution tests
- Platform-specific test matrices (NPU, XPU, ROCm)
- Quantization correctness tests
- Memory leak detection
