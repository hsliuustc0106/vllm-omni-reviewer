**Critical Focus:**
- Model-specific correctness validation (outputs match expected behavior)
- Memory/hardware requirements documented and tested
- Inference latency testd
- Distributed execution support (TP/PP/EP/DP compatibility)
- Model configuration handling
- Integration with existing model registry

**Questions to Ask:**
- What are the model's unique architectural features? which category it belongs?
- How does it handle different input modalities?
- What are the memory requirements for typical use cases?
- Does it work with quantization/parallelism/disaggregated/cudagraph/streaming output?

**Using Linked Issue Context:**
- Verify model requirements from issue are met (architecture, capabilities)
- Check if the issue mentions hardware specs - validate memory/compute requirements
- Look for expected behavior examples in the issue - verify outputs match

**Common Issues:**
- Missing model-specific tests
- Incomplete distributed execution support
- Memory requirements not documented
- Config parsing errors
- Missing integration with quantization
- Missing tests

**vllm-omni Specific Considerations:**
- Multi-modal model support (text, image, audio, video)
- cuda graph support
- batch support
- online/offline support
- quantization support
- parallelism support
- disaggregated encoder/llm/dit support
- kv/token/hidden states transfer mechanisms
- Model-specific attention mechanisms
- Custom tokenizer handling
