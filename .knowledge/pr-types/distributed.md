**Critical Focus:**
- Correctness in distributed mode (TP/PP/EP/DP)
- Communication overhead measured
- Memory distribution across devices
- Fault tolerance and error handling
- Scalability with number of devices

**Questions to Ask:**
- What's the communication overhead?
- How is memory distributed?
- Does it work with other features? e.g., offloading, disaggregation...

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
