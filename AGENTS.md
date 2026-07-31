# Sleeper AI Agent

**Every request: start at [index.md](./index.md)**. Follow concept paths before searching files.

## Request procedure

1. Read `index.md` (root)
2. Pick the concept that covers the question
3. Read that concept's `index.md`
4. Follow sub-concept links until you reach endpoint/schema/reference docs
5. Use the tool/data named there

Grep/find only when index has no path to the answer.

## Example

User: "What draft picks did the Bengals make?"

1. Read `index.md` → see `sleeper` concept
2. Read `sleeper/index.md` → see `drafts` sub-concept
3. Read `sleeper/drafts/index.md` → lists `endpoint.md`
4. Read `sleeper/drafts/endpoint.md` → tool name/params
5. Call tool with league ID

No grep. Index led to the answer.