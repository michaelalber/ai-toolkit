# Edge Case Taxonomy

Systematic categories of edge cases to check during QA. Apply each category to the
feature being reviewed.

## Input edge cases

| Category | What to test | Why it matters |
|----------|-------------|---------------|
| Empty / null | null, empty string, empty list, zero | Often skipped in happy-path thinking |
| Boundary values | min, max, min-1, max+1 | Off-by-one errors live here |
| Invalid format | wrong type, wrong encoding, malformed JSON | Validation gaps |
| Very long input | strings at limit, lists with 10k items | Buffer overflows, timeout, UI truncation |
| Unicode / special chars | emoji, RTL text, SQL injection strings, `<script>` | Encoding bugs, XSS, injection |
| Duplicate input | same item submitted twice | Idempotency issues |

## State edge cases

| Category | What to test | Why it matters |
|----------|-------------|---------------|
| Missing prerequisites | required data not yet created | Order-of-operations bugs |
| Already-done action | submit same form twice, double-click | Non-idempotent operations |
| Concurrent modification | two users edit same record simultaneously | Race conditions |
| Stale data | cache not invalidated, optimistic lock conflict | Consistency bugs |
| Deleted entity | reference to soft-deleted or hard-deleted record | Dangling references |

## Integration edge cases

| Category | What to test | Why it matters |
|----------|-------------|---------------|
| Dependency down | third-party API unavailable | Cascading failures |
| Slow dependency | response takes 30s | Timeout handling |
| Partial failure | one item in a batch fails | Rollback / compensation |
| Rate limit hit | API quota exceeded | Degraded experience vs error |
| Contract mismatch | unexpected field added/removed in response | Deserialization fragility |

## Permission edge cases

| Category | What to test | Why it matters |
|----------|-------------|---------------|
| Unauthenticated | no session or expired token | Auth bypass |
| Insufficient role | lower-privilege user attempts admin action | Authorization bypass |
| Cross-tenant | user A accesses user B's data | Broken object-level authorization |
| Revoked permission | permission changed mid-session | Session invalidation |

## Volume edge cases

| Category | What to test | Why it matters |
|----------|-------------|---------------|
| Zero items | empty list, no results | Empty state rendering |
| One item | single record | Off-by-one, singular vs plural |
| Large volume | 10k+ records | Performance, pagination |
| Exact limit | at the configured maximum | Boundary behavior |
