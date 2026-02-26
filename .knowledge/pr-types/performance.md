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
