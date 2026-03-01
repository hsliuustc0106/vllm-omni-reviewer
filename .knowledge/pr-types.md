# PR Type Review Focus

## Bugfix
- Regression test to prevent recurrence?
- Root cause understood and documented?
- Similar bugs elsewhere in codebase?
- Fix addresses root cause, not just symptoms?

## Feature
- Comprehensive test coverage?
- User-facing documentation updated?
- Breaking changes documented?
- Performance impact measured?

## Refactor
- Behavior preserved (no functional changes)?
- Existing tests still pass?
- No performance regressions?
- Clear improvement in code quality?

## Model
- Model correctness validated (outputs match expected)?
- Memory/hardware requirements documented?
- Distributed execution support (TP/PP)?
- Works with quantization/cudagraph/streaming?

## Performance
- Benchmark results on realistic workloads?
- Quality preservation (no accuracy degradation)?
- Memory usage changes measured?
- Scalability with model/batch size?

## Distributed
- Correctness in TP/PP/EP/DP modes?
- Communication overhead measured?
- Memory distribution across devices?
- Fault tolerance and error handling?

## Quantization
- Memory measurements before/after?
- Quality trade-offs documented (accuracy, perceptual)?
- Compatibility with different model types?
- Fallback when quantization not supported?

## Platform (NPU/XPU/ROCm)
- Platform-specific correctness?
- Fallback for unsupported features?
- Performance on target platform?
- Clear documentation of requirements?

## API
- Backward compatibility preserved?
- Breaking changes clearly marked?
- Migration path for deprecated APIs?
- OpenAI-compatible endpoints maintained?

## Documentation
- Technical content accurate?
- Code examples work (copy-paste test)?
- Clear explanations for target audience?
- Links to related docs?

## CI
- Test coverage for new code paths?
- No flaky tests introduced?
- Build reproducibility maintained?
- Clear failure messages?
