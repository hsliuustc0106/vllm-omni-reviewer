# Code Quality Guidelines

## Function Length

**General Thresholds:**
- Functions under 100 lines: Generally acceptable
- Functions 100-300 lines: Review carefully for split opportunities
- Functions over 300 lines: Strong candidate for refactoring

**Critical Questions:**
- Can this function be split into smaller, focused functions?
- Are there distinct logical sections that could be extracted?
- Is the function doing multiple things?
- Would extracting helpers improve readability and testability?

**Good Example:**
```python
async def process_request(request: Request) -> Response:
    """Process a single inference request."""
    validated_input = _validate_input(request.input)
    model_output = await _run_inference(validated_input)
    return _format_response(model_output)

def _validate_input(input_data: dict) -> ValidatedInput:
    """Validate and normalize input data."""
    if not input_data.get("prompt"):
        raise ValueError("Missing prompt")
    return ValidatedInput(prompt=input_data["prompt"])

async def _run_inference(input_data: ValidatedInput) -> ModelOutput:
    """Execute model inference."""
    return await model.generate(input_data.prompt)

def _format_response(output: ModelOutput) -> Response:
    """Format model output as API response."""
    return Response(text=output.text, tokens=output.token_count)
```

**Bad Example:**
```python
async def process_request(request: Request) -> Response:
    """Process a single inference request."""
    # Validation (10 lines)
    if not request.input:
        raise ValueError("Missing input")
    if not request.input.get("prompt"):
        raise ValueError("Missing prompt")
    if len(request.input["prompt"]) > MAX_LENGTH:
        raise ValueError("Prompt too long")

    # Preprocessing (15 lines)
    prompt = request.input["prompt"]
    tokens = tokenizer.encode(prompt)
    if len(tokens) > model.max_tokens:
        tokens = tokens[:model.max_tokens]

    # Inference (20 lines)
    with torch.no_grad():
        output = model.forward(tokens)
        logits = output.logits
        probs = torch.softmax(logits, dim=-1)
        next_token = torch.argmax(probs)

    # Postprocessing (15 lines)
    decoded = tokenizer.decode(next_token)
    response_text = decoded.strip()
    token_count = len(tokens)

    return Response(text=response_text, tokens=token_count)
```

## Cyclomatic Complexity

**Thresholds:**
- Complexity 1-5: Simple, easy to test
- Complexity 6-10: Moderate, review test coverage carefully
- Complexity 11+: High risk, requires refactoring

**Critical Questions:**
- How many test cases are needed to cover all paths?
- Can nested conditionals be flattened with early returns?
- Should this use guard clauses?
- Can complex conditions be extracted into named helper functions?

**Good Example (Low Complexity):**
```python
def allocate_kv_cache(config: CacheConfig) -> KVCache:
    """Allocate KV cache based on configuration."""
    if not config.enable_cache:
        return NullCache()

    if config.cache_type == "auto":
        return _allocate_auto_cache(config)

    if config.cache_type == "static":
        return _allocate_static_cache(config)

    raise ValueError(f"Unknown cache type: {config.cache_type}")
```

**Bad Example (High Complexity):**
```python
def allocate_kv_cache(config: CacheConfig) -> KVCache:
    """Allocate KV cache based on configuration."""
    if config.enable_cache:
        if config.cache_type == "auto":
            if config.memory_limit:
                if config.memory_limit > MIN_MEMORY:
                    cache = AutoCache(config.memory_limit)
                    if config.enable_compression:
                        cache.enable_compression()
                    return cache
                else:
                    return SmallCache(config.memory_limit)
            else:
                return DefaultCache()
        elif config.cache_type == "static":
            if config.num_blocks:
                return StaticCache(config.num_blocks)
            else:
                return StaticCache(DEFAULT_BLOCKS)
        else:
            raise ValueError(f"Unknown cache type: {config.cache_type}")
    else:
        return NullCache()
```

## Nesting Depth

**Thresholds:**
- 1-2 levels: Acceptable
- 3 levels: Review for flattening opportunities
- 4+ levels: Requires refactoring

**Refactoring Strategies:**
- Extract nested blocks into helper functions
- Use early returns to reduce nesting
- Replace nested loops with comprehensions or itertools
- Use guard clauses at function start
- Invert conditions to handle edge cases first

**Good Example (Flat Structure):**
```python
async def execute_distributed_inference(
    request: Request,
    tp_group: TPGroup,
    pp_group: PPGroup
) -> Output:
    """Execute inference across distributed workers."""
    if not tp_group.is_initialized():
        raise RuntimeError("TP group not initialized")

    if not pp_group.is_initialized():
        raise RuntimeError("PP group not initialized")

    input_data = await _prepare_distributed_input(request, tp_group)
    intermediate = await _execute_pipeline_stages(input_data, pp_group)
    return await _gather_distributed_output(intermediate, tp_group)
```

**Bad Example (Deep Nesting):**
```python
async def execute_distributed_inference(
    request: Request,
    tp_group: TPGroup,
    pp_group: PPGroup
) -> Output:
    """Execute inference across distributed workers."""
    if tp_group.is_initialized():
        if pp_group.is_initialized():
            input_data = await _prepare_input(request)
            if input_data:
                for stage in pp_group.stages:
                    if stage.is_active():
                        for worker in tp_group.workers:
                            if worker.is_ready():
                                result = await worker.process(input_data)
                                if result:
                                    return result
    raise RuntimeError("Distributed execution failed")
```

## Function Responsibilities

**Single Responsibility Principle:**
- Each function should do one thing well
- Function name should clearly describe what it does
- If you need "and" in the function name, it probably does too much
- Side effects should be explicit in the function name

**Critical Questions:**
- Can you describe what this function does in one sentence without using "and"?
- Does it have multiple reasons to change?
- Are there side effects beyond the function's stated purpose?
- Would splitting this function make testing easier?

**Good Example:**
```python
def parse_model_config(config_path: str) -> ModelConfig:
    """Parse model configuration from file."""
    with open(config_path) as f:
        raw_config = json.load(f)
    return ModelConfig.from_dict(raw_config)

def validate_model_config(config: ModelConfig) -> None:
    """Validate model configuration parameters."""
    if config.hidden_size % config.num_heads != 0:
        raise ValueError("hidden_size must be divisible by num_heads")

def load_model_weights(config: ModelConfig) -> dict:
    """Load model weights from checkpoint."""
    checkpoint_path = config.checkpoint_path
    return torch.load(checkpoint_path)
```

**Bad Example:**
```python
def load_and_validate_model(config_path: str) -> tuple[ModelConfig, dict]:
    """Load model config, validate it, and load weights."""
    # Parse config
    with open(config_path) as f:
        raw_config = json.load(f)
    config = ModelConfig.from_dict(raw_config)

    # Validate config
    if config.hidden_size % config.num_heads != 0:
        raise ValueError("hidden_size must be divisible by num_heads")

    # Load weights
    checkpoint_path = config.checkpoint_path
    weights = torch.load(checkpoint_path)

    # Initialize model (side effect!)
    global _model_instance
    _model_instance = Model(config, weights)

    return config, weights
```

## Test Coverage

**Coverage Thresholds by Code Type:**
- **New features**: Comprehensive coverage required (happy path, edge cases, error handling)
- **Bug fixes**: Regression test mandatory + edge cases around the fix
- **Refactoring**: Existing tests must pass, no new tests required unless behavior changes
- **Performance optimizations**: Benchmarks with before/after measurements required
- **Distributed code**: Must test in distributed mode, not just single-device

**Critical Questions:**
- How do we know this works?
- What happens when [edge case]?
- Are all code paths covered by tests?
- Are error conditions tested?
- Is this tested on realistic workloads or synthetic data?
- For performance claims: Where are the measurements?

**Coverage by Complexity:**
- **Complexity 1-5**: Basic happy path tests acceptable
- **Complexity 6-10**: Must test all major branches and error paths
- **Complexity 11+**: Comprehensive coverage required for all paths

**Good Example (Comprehensive Coverage):**
```python
# PR #1405: Bugfix with good test coverage
def _normalize_layer_kv(kv_data):
    """Normalize KV cache from tuple or tensor format."""
    if isinstance(kv_data, tuple):
        return kv_data[0], kv_data[1]
    return kv_data[0], kv_data[1]

# Tests included:
# ✓ Test with tuple format (NPU case)
# ✓ Test with stacked tensor format (GPU case)
# ✓ Test with mismatched block counts (truncation with warning)
# ✓ Defensive validation at multiple levels
```

**Bad Example (Missing Coverage):**
```python
# PR #1412: Major feature with zero tests
def apply_fp8_quantization(model, quant_config):
    """Apply FP8 quantization to model layers."""
    for layer in model.layers:
        if layer.name not in quant_config.ignored_layers:
            layer.quantize_to_fp8()
    return model

# Tests included:
# ✗ No tests at all
# ✗ No memory measurements (claimed "significant memory reduction")
# ✗ No validation of ignored_layers parameter
# ✗ No error handling tests for invalid configs
# ✗ No regression test for non-quantized path

# This was flagged as a CRITICAL BLOCKER despite being technically sound
```

**Test Requirements by PR Type:**

**Bugfix PRs:**
- Regression test covering exact reproduction steps from linked issue
- Tests for edge cases around the fix
- Tests for similar bugs elsewhere in codebase
- Example: PR #1405 praised for "good test coverage for tuple and mismatch paths"

**Feature PRs:**
- Happy path tests
- Edge case tests (boundary conditions, empty inputs, max limits)
- Error handling tests (invalid inputs, missing dependencies)
- Integration tests with existing features
- Example: PR #1412 flagged as critical blocker for "zero tests" on major feature

**Performance PRs:**
- Before/after benchmark measurements
- Memory usage measurements (peak, average, VRAM)
- Quality metrics if applicable (accuracy, FID scores, CLIP scores)
- Tests on realistic workloads, not just synthetic data

**Distributed PRs:**
- Tests in TP mode (tensor parallelism)
- Tests in PP mode (pipeline parallelism)
- Communication overhead measurements
- Memory distribution validation across devices
- Fault tolerance tests

**vllm-omni Specific Test Requirements:**

**Async Functions:**
- Test concurrent execution with asyncio.gather
- Test race conditions between awaits
- Test error propagation through async chains
- Test timeout and cancellation behavior

**Model Code:**
- Test model correctness (outputs match expected behavior)
- Test memory requirements for typical use cases
- Test quantization compatibility
- Test distributed execution (TP/PP)
- Test streaming output for generative models

**KV Cache Management:**
- Test allocation, update, cleanup lifecycle
- Test state transitions and invariants
- Test concurrent access patterns
- Test memory leak prevention

**Quantization:**
- Measure memory reduction (before/after)
- Measure quality impact (quantitative metrics)
- Test compatibility with different model types
- Test ignored_layers parameter
- Test fallback when quantization not supported

## vllm-omni Specific Considerations

### Async Function Complexity

**Guidelines:**
- Async functions with multiple await points increase complexity
- Each await is a potential failure point and state transition
- Consider splitting long async chains into smaller async helpers
- Watch for race conditions in complex async flows

**Critical Questions:**
- Are all await points properly error-handled?
- Can concurrent operations be grouped with asyncio.gather?
- Are there race conditions between awaits?
- Is the async complexity justified or could this be synchronous?

**Example:**
```python
# Good: Clear async flow with error handling
async def process_batch(requests: list[Request]) -> list[Response]:
    """Process a batch of requests concurrently."""
    validated = [_validate_request(r) for r in requests]
    results = await asyncio.gather(
        *[_process_single(r) for r in validated],
        return_exceptions=True
    )
    return [_handle_result(r) for r in results]

# Bad: Complex async flow with unclear error handling
async def process_batch(requests: list[Request]) -> list[Response]:
    """Process a batch of requests."""
    results = []
    for req in requests:
        validated = await _validate_async(req)
        if validated:
            preprocessed = await _preprocess(validated)
            if preprocessed:
                result = await _infer(preprocessed)
                if result:
                    postprocessed = await _postprocess(result)
                    results.append(postprocessed)
    return results
```

### Distributed Execution Patterns

**Guidelines:**
- Functions handling TP/PP coordination may legitimately be complex
- Document why complexity is necessary
- Ensure comprehensive test coverage for distributed paths
- Separate coordination logic from computation logic

**When Complexity is Justified:**
- Tensor parallelism synchronization across workers
- Pipeline parallelism stage coordination
- Distributed KV cache management
- Multi-node communication patterns

**Critical Questions:**
- Is the distributed complexity isolated from business logic?
- Are distributed failure modes handled?
- Is there a clear fallback for single-device execution?
- Are communication patterns documented?

### Model Initialization

**Guidelines:**
- Model config parsing functions can be legitimately long
- Focus on clear sections with comments
- Consider builder pattern for complex initialization
- Separate parsing, validation, and construction

**Acceptable Patterns:**
```python
def create_model_from_config(config: dict) -> Model:
    """Create model instance from configuration dictionary."""
    # Parse architecture parameters (10-15 lines)
    arch_config = _parse_architecture_config(config)

    # Parse quantization settings (10-15 lines)
    quant_config = _parse_quantization_config(config)

    # Parse distributed settings (10-15 lines)
    dist_config = _parse_distributed_config(config)

    # Construct model (5-10 lines)
    return Model(arch_config, quant_config, dist_config)
```

### KV Cache Management

**Guidelines:**
- Cache operations may have complex state management
- Ensure clear separation between allocation, update, and cleanup
- Document invariants and assumptions
- Use type system to enforce valid states

**Critical Questions:**
- Are cache invariants documented and enforced?
- Is memory management explicit and leak-free?
- Are concurrent access patterns safe?
- Is the cache state machine clear?

**Example:**
```python
class KVCache:
    """KV cache with explicit state management."""

    def allocate(self, num_blocks: int) -> None:
        """Allocate cache blocks. Must be called before use."""
        assert self._state == CacheState.UNINITIALIZED
        self._blocks = [Block() for _ in range(num_blocks)]
        self._state = CacheState.ALLOCATED

    def update(self, block_id: int, kv_data: Tensor) -> None:
        """Update a cache block. Cache must be allocated."""
        assert self._state == CacheState.ALLOCATED
        self._blocks[block_id].update(kv_data)

    def cleanup(self) -> None:
        """Release cache resources. Idempotent."""
        if self._state != CacheState.UNINITIALIZED:
            self._blocks.clear()
            self._state = CacheState.UNINITIALIZED
```

## Review Checklist

When reviewing code for quality issues, check:

- [ ] Functions over 30 lines: Can they be split?
- [ ] Functions with 3+ levels of nesting: Can they be flattened?
- [ ] Functions with complex conditionals: Can they use early returns?
- [ ] Functions doing multiple things: Can responsibilities be separated?
- [ ] Async functions with many awaits: Is error handling clear?
- [ ] Distributed code: Is complexity justified and documented?
- [ ] Long initialization functions: Are they well-structured?
- [ ] State management: Are invariants clear and enforced?
- [ ] New features: Is there comprehensive test coverage?
- [ ] Bug fixes: Is there a regression test?
- [ ] Performance claims: Are there before/after measurements?
- [ ] Distributed code: Is it tested in distributed mode?
- [ ] Complex functions (11+ complexity): Are all paths tested?
- [ ] Async code: Are race conditions and error propagation tested?
- [ ] Quantization: Are memory savings and quality impact measured?
- [ ] Model code: Is correctness validated with expected outputs?
