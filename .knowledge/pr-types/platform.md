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
