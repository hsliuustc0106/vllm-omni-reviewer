# PR Type-Specific Review Guidance

## bugfix

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
- Memory leaks in long-running inference

---

## feature

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
- Compatibility with distributed execution (TP/PP)
- Impact on memory usage and KV cache
- Streaming output support
- Multi-modal feature interactions

---

## model

**Critical Focus:**
- Model-specific correctness validation (outputs match expected behavior)
- Memory requirements documented and tested
- Distributed execution support (TP/PP compatibility)
- Model configuration handling
- Integration with existing model registry

**Questions to Ask:**
- What are the model's unique architectural features?
- How does it handle different input modalities?
- What are the memory requirements for typical use cases?
- Does it work with quantization?

**Using Linked Issue Context:**
- Verify model requirements from issue are met (architecture, capabilities)
- Check if the issue mentions hardware specs - validate memory/compute requirements
- Look for expected behavior examples in the issue - verify outputs match
- If the issue mentions specific model variants, ensure all are supported

**Common Issues:**
- Missing model-specific tests
- Incomplete distributed execution support
- Memory requirements not documented
- Config parsing errors
- Missing integration with quantization

**vllm-omni Specific Considerations:**
- Multi-modal model support (text, image, audio, video)
- Reward model integration
- Model-specific attention mechanisms
- Custom tokenizer handling
- Streaming output for generative models

---

## quantization

**Critical Focus:**
- Memory measurements before and after quantization
- Quality trade-offs documented (accuracy, perceptual quality)
- Performance benchmarks on realistic workloads
- Compatibility with different model types
- Fallback behavior when quantization not supported

**Questions to Ask:**
- What's the memory reduction achieved?
- What's the quality impact (quantitative metrics)?
- What's the performance impact (latency, throughput)?
- Which model components are quantized?

**Using Linked Issue Context:**
- Check if measurements match target metrics from issue
- Verify quality preservation meets expectations from issue discussion
- If the issue mentions specific models, ensure quantization works for them
- Look for performance targets in the issue - validate benchmarks meet them

**Common Issues:**
- Missing memory measurements
- No quality evaluation
- Performance not benchmarked
- Quantization breaks distributed execution
- No fallback for unsupported cases

**vllm-omni Specific Considerations:**
- FP8 quantization for transformers, VAE, attention
- KV cache quantization
- Multi-modal model quantization (different components)
- Interaction with distributed execution
- Platform-specific quantization support (NPU, XPU)

---

## documentation

**Critical Focus:**
- Accuracy of technical content
- Completeness of coverage
- Working examples that can be copy-pasted
- Clear explanations for target audience
- Links to related documentation

**Questions to Ask:**
- Can a new user follow this documentation?
- Are all code examples tested and working?
- Are there missing prerequisites or setup steps?
- Is the documentation up-to-date with current code?

**Using Linked Issue Context:**
- Verify documentation addresses confusion/questions raised in issue
- If the issue mentions specific pain points, ensure they're clarified
- Look for user feedback in the issue - does the doc address it?
- Check if the issue mentions missing examples - are they now included?

**Common Issues:**
- Outdated examples
- Missing prerequisites
- Unclear explanations
- No troubleshooting guidance
- Broken links

**vllm-omni Specific Considerations:**
- Multi-modal usage examples
- Quantization configuration
- Distributed execution setup
- Platform-specific instructions (NPU, XPU, ROCm)
- API compatibility with vLLM

---

## ci

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

---

## platform

**Critical Focus:**
- Platform-specific correctness (NPU, XPU, ROCm)
- Fallback behavior for unsupported features
- Compatibility with existing code
- Performance on target platform
- Clear documentation of platform requirements

**Questions to Ask:**
- Does this work on all supported platforms?
- What happens on unsupported platforms?
- Are platform-specific optimizations justified?
- Are there platform-specific tests?

**Using Linked Issue Context:**
- Verify platform-specific requirements from issue are met
- Check if the issue mentions specific hardware - validate compatibility
- Look for performance expectations in the issue - are they met?
- If the issue mentions missing features, ensure they're now supported

**Common Issues:**
- Missing fallback for unsupported platforms
- No platform-specific tests
- Performance not validated on target platform
- Breaking changes for other platforms
- Unclear platform requirements

**vllm-omni Specific Considerations:**
- Ascend NPU support
- Intel XPU support
- AMD ROCm support
- Platform-specific quantization
- Distributed execution on heterogeneous hardware

---

## performance

**Critical Focus:**
- Benchmark results on realistic workloads
- Quality preservation (no accuracy degradation)
- Performance impact across different scenarios
- Memory usage changes
- Scalability with model size and batch size

**Questions to Ask:**
- What's the performance improvement (quantitative)?
- What workloads were benchmarked?
- Are there scenarios where performance degrades?
- What's the memory impact?

**Using Linked Issue Context:**
- Check if benchmarks match performance targets from issue
- Verify workloads tested match use cases mentioned in issue
- If the issue mentions bottlenecks, confirm they're addressed
- Look for performance expectations in the issue - are they met?

**Common Issues:**
- Missing benchmarks
- Unrealistic workloads
- Quality degradation not measured
- Performance regression in other scenarios
- Memory usage not considered

**vllm-omni Specific Considerations:**
- Inference latency and throughput
- Multi-modal model performance
- Distributed execution efficiency
- KV cache optimization
- Streaming output performance

---

## api

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

---

## refactor

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

---

## wip

**Critical Focus:**
- Directional feedback on approach
- Architectural concerns
- Early identification of blockers
- Not ready for merge
- Clear indication of what's incomplete

**Questions to Ask:**
- What's the goal of this PR?
- What's still missing?
- Are there architectural concerns?
- What feedback is most valuable?

**Using Linked Issue Context:**
- Check if approach aligns with issue discussion
- Look for design decisions in the issue - does the WIP follow them?
- If the issue mentions alternatives, is this the agreed approach?
- Verify the WIP is heading in the right direction per issue goals

**Common Issues:**
- Unclear what's being proposed
- No indication of what's incomplete
- Premature implementation details
- Missing context on goals
- Not clearly marked as WIP

**vllm-omni Specific Considerations:**
- Experimental features
- Architecture explorations
- Performance experiments
- New model support prototypes
- API design proposals

---

## distributed

**Critical Focus:**
- Correctness in distributed mode (TP/PP)
- Communication overhead measured
- Memory distribution across devices
- Fault tolerance and error handling
- Scalability with number of devices

**Questions to Ask:**
- Does this work with Tensor Parallelism?
- Does this work with Pipeline Parallelism?
- What's the communication overhead?
- How is memory distributed?

**Using Linked Issue Context:**
- Verify distributed requirements from issue are addressed
- Check if the issue mentions scaling targets - are they met?
- Look for distributed execution scenarios in the issue - are they tested?
- If the issue mentions communication bottlenecks, verify they're resolved

**Common Issues:**
- Not tested in distributed mode
- Communication overhead not measured
- Memory imbalance across devices
- Poor fault tolerance
- Scalability not validated

**vllm-omni Specific Considerations:**
- Multi-modal model distribution
- KV cache distribution
- Quantization in distributed mode
- Streaming output in distributed mode
- Platform-specific distributed execution (NPU, XPU)
