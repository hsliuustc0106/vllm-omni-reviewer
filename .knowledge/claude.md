# Claude Code Usage Guide

## Posting PR Reviews with Inline Comments

### Method 1: Simple Review (Recommended for comprehensive reviews)

Post a single review with "REQUEST_CHANGES" status that includes all feedback in the body:

```bash
# 1. Get the commit SHA
COMMIT_SHA=$(gh pr view <PR_NUMBER> --repo vllm-project/vllm-omni --json headRefOid --jq '.headRefOid')

# 2. Create review payload
cat > review_payload.json << 'EOF'
{
  "commit_id": "COMMIT_SHA_HERE",
  "body": "Overall review comment with pros/cons...\n\n---\n\n## Specific Issues\n\n### `path/to/file.py:123`\nIssue description here\n\n### `path/to/another.py:456`\nAnother issue description",
  "event": "REQUEST_CHANGES"
}
EOF

# 3. Post the review
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/vllm-project/vllm-omni/pulls/<PR_NUMBER>/reviews \
  --input review_payload.json
```

**Pros:**
- All feedback in one place
- Easy to read and reference
- No issues with line number resolution
- Works well for comprehensive reviews

**Cons:**
- Comments not attached to specific code lines in the diff view

---

### Method 2: Review with True Inline Comments (Advanced)

Post a review with comments attached to specific lines in the diff:

```bash
# 1. Get the commit SHA
COMMIT_SHA=$(gh pr view <PR_NUMBER> --repo vllm-project/vllm-omni --json headRefOid --jq '.headRefOid')

# 2. Create review payload with inline comments
cat > review_payload.json << 'EOF'
{
  "commit_id": "COMMIT_SHA_HERE",
  "body": "Overall review comment",
  "event": "REQUEST_CHANGES",
  "comments": [
    {
      "path": "examples/offline_inference/mammothmodal2_preview/README.md",
      "position": 41,
      "body": "Typo: 'Summery' should be 'Summarize'"
    },
    {
      "path": "vllm_omni/model_executor/models/mammoth_moda2/mammoth_moda2_ar.py",
      "position": 52,
      "body": "Missing docstring for this function"
    }
  ]
}
EOF

# 3. Post the review
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/vllm-project/vllm-omni/pulls/<PR_NUMBER>/reviews \
  --input review_payload.json
```

**Important Notes:**
- Use `position` (not `line`) for the line number in the diff
- `position` is the line number counting from the start of the diff for that file
- For new files, count from the `@@ -0,0 +1,N @@` line
- GitHub will reject if the position doesn't match an actual changed line

**Pros:**
- Comments appear directly on code lines in the diff view
- Better for targeted, specific feedback

**Cons:**
- Requires calculating diff positions correctly
- More complex to set up
- Can fail if positions are wrong

---

### Method 3: Using gh pr review (Simple but Limited)

```bash
# Post a simple review comment
gh pr review <PR_NUMBER> --repo vllm-project/vllm-omni --request-changes --body "Review comment"

# Post a general comment (not a review)
gh pr comment <PR_NUMBER> --repo vllm-project/vllm-omni --body "Comment text"
```

**Pros:**
- Simple command
- No JSON required

**Cons:**
- Cannot add inline comments
- Less control over formatting

---

## Example: PR #336 Review

Successfully posted review using Method 1:

```json
{
  "commit_id": "147ed395032026ffab87c678459af61e69a884a3",
  "body": "This PR adds MammothModa2...\n\n**Pros:**\n- Item 1\n\n**Cons:**\n- Item 1\n\n---\n\n## Specific Issues\n\n### `file.py:123`\nIssue description",
  "event": "REQUEST_CHANGES"
}
```

Result: https://github.com/vllm-project/vllm-omni/pull/336#pullrequestreview-3858233751

---

## Review Event Types

- `APPROVE` - Approve the PR
- `REQUEST_CHANGES` - Request changes before merge
- `COMMENT` - General feedback without approval/rejection

---

## Tips

1. **For comprehensive reviews**: Use Method 1 with all issues in the body
2. **For quick fixes**: Use Method 3 with gh pr review
3. **For precise code feedback**: Use Method 2 with calculated diff positions
4. **Always include**:
   - Pros/cons structure
   - Specific file references with line numbers
   - Actionable feedback
   - Clear recommendation (approve/request changes)
