# vllm-omni Code Patterns

## Async Function Complexity

**Guidelines:**
- Each `await` is a potential failure point and state transition
- Consider splitting long async chains into smaller helpers
- Watch for race conditions in complex async flows

**Good:**
```python
async def process_batch(requests: list[Request]) -> list[Response]:
    validated = [_validate_request(r) for r in requests]
    results = await asyncio.gather(
        *[_process_single(r) for r in validated],
        return_exceptions=True
    )
    return [_handle_result(r) for r in results]
```

## Distributed Execution Patterns

**When complexity is justified:**
- Tensor parallelism synchronization across workers
- Pipeline parallelism stage coordination
- Distributed KV cache management
- Multi-node communication patterns

**Critical questions:**
- Is distributed complexity isolated from business logic?
- Are distributed failure modes handled?
- Is there a clear fallback for single-device execution?

## KV Cache Management

**Guidelines:**
- Ensure clear separation between allocation, update, and cleanup
- Document invariants and assumptions
- Use type system to enforce valid states

**Pattern:**
```python
class KVCache:
    def allocate(self, num_blocks: int) -> None:
        assert self._state == CacheState.UNINITIALIZED
        self._blocks = [Block() for _ in range(num_blocks)]
        self._state = CacheState.ALLOCATED

    def update(self, block_id: int, kv_data: Tensor) -> None:
        assert self._state == CacheState.ALLOCATED
        self._blocks[block_id].update(kv_data)
```

## Test Coverage Thresholds

| Code Type | Requirement |
|-----------|-------------|
| New features | Happy path + edge cases + error handling |
| Bug fixes | Regression test + edge cases around fix |
| Performance | Benchmarks with before/after measurements |
| Distributed | Must test in distributed mode |
| Quantization | Memory savings + quality impact measured |

## Code Quality Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Function length | 100+ lines | Review for split opportunities |
| Complexity | 11+ | Requires refactoring |
| Nesting depth | 4+ levels | Requires refactoring |
