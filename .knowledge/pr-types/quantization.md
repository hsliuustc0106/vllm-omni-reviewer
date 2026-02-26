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
