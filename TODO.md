# TODO

## Roadmap

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| 1 | Comments on Issues | ✅ Done | Polymorphic relationships, nested schemas, pagination |
| 2 | Real-time updates via WebSockets | ✅ Done | Connection manager, room broadcasting |
| 3 | File attachments using MinIO | ✅ Done | Presigned URLs, multipart uploads |
| 4 | Activity log / audit trail | ⬜ Todo | BackgroundTasks, timeline UI |
| 5 | AI-powered semantic search with pgvector | ⬜ Todo | Vector embeddings, similarity queries |
| 6 | Redis for caching + rate limiting | ⬜ Todo | Cache invalidation, fastapi-limiter |
| 7 | Markdown support | ⬜ Todo | marked/milkdown, XSS sanitization |
| 8 | In-app notifications | ⬜ Todo | Notification bell, feeds from activity log |
| 9 | Mention system (@username) | ⬜ Todo | Text parsing, mention resolution |
| 10 | Issue labels/tags | ⬜ Todo | Many-to-many, join tables |

---

## Completed

### 1. Comments on Issues
Every real issue tracker has comments. It's the natural hook for several other features — real-time updates, mentions, activity log.
- **Concepts:** polymorphic relationships in SQLAlchemy, nested response schemas, pagination at the comment level

### 2. Real-time updates via WebSockets
When user A changes an issue status, user B's dashboard updates without refresh.
- **Concepts:** FastAPI WebSocket endpoints, connection manager pattern, broadcasting to specific rooms

### 3. File attachments using MinIO
MinIO is an S3-compatible object store. You upload images/files through FastAPI, they land in MinIO.
- **Concepts:** multipart form uploads, presigned URLs, MinIO as Docker service

---

## Upcoming

### 4. Activity log / audit trail
Every state change writes a timestamnable record. Show it as a timeline on each issue.
- **Concepts:** BackgroundTasks, event-driven patterns, timeline UI

### 5. AI-powered semantic search with pgvector
pgvector adds vector similarity search. "Find similar issues" becomes a vector query.
- **Note:** Requires OpenAI API key or local embedding model — keep optional

### 6. Redis for caching + rate limiting
Cache expensive queries with TTL, invalidate on write. Rate limit auth endpoints.
- **Concepts:** Redis, fastapi-limiter, cache invalidation strategy

### 7. Markdown support
Render issue descriptions and comments as markdown.
- **Concepts:** marked or @milkdown/kit, XSS sanitization

### 8. In-app notifications
Notification bell for issues assigned to you or when someone comments.
- **Feeds from:** activity log

### 9. Mention system (@username)
Tag users in comments with text parsing and profile linking.
- **Concepts:** text parsing, mention resolution

### 10. Issue labels/tags
Many-to-many relationship between issues and tags.
- **Concepts:** join tables in SQLAlchemy, array filtering
