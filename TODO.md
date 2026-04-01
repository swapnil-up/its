1. Comments on Issues
Every real issue tracker has comments. More importantly it's the natural hook for several other features — real-time updates, mentions, activity log. 
New concepts: polymorphic relationships in SQLAlchemy, nested response schemas, pagination at the comment level.
2. Real-time updates via WebSockets
When user A changes an issue status, user B's dashboard updates without refresh.
New concepts: FastAPI WebSocket endpoints, connection manager pattern (tracking active connections), broadcasting to specific rooms, Svelte handling WebSocket lifecycle with runes.
3. File attachments on issues using MinIO
MinIO is an S3-compatible object store that runs in Docker. You upload images/files through FastAPI, they land in MinIO, the issue stores a reference URL.
New concepts: multipart form uploads in FastAPI, presigned URLs (time-limited access links), adding MinIO as a Docker service, Svelte file input handling.
4. Activity log / audit trail
Every state change (issue created, status changed, comment added, file attached) writes a timestamnable record. Show it as a timeline on each issue. Uses FastAPI BackgroundTasks — the route returns immediately, the audit write happens asynchronously.
New concepts: BackgroundTasks dependency, event-driven patterns, timeline UI in Svelte.
5. AI-powered semantic search with pgvector
pgvector is a Postgres extension that adds vector similarity search. When an issue is created, you generate an embedding (via OpenAI or a local model) and store it. Then "find similar issues" becomes a vector similarity query. 
New concepts: pgvector Postgres extension, SQLAlchemy vector column type, embedding generation, cosine similarity queries, Svelte UI for surfacing similar issues.
This one requires an API key (OpenAI) or running a local embedding model. Worth doing but keep it optional/feature-flagged.
6. Redis for caching + rate limiting
Add Redis as a Docker service. Cache expensive queries (issue list with joins) with a short TTL, invalidate on write. Add rate limiting to the auth endpoints (max 5 login attempts per minute per IP).
New concepts: Redis as a Docker service, fastapi-limiter, cache invalidation strategy, thinking about consistency tradeoffs.
7. Markdown support
Issue descriptions and comments rendered as markdown in the UI. A markdown editor in the create/edit forms.
New concepts: marked or @milkdown/kit in Svelte, sanitizing user HTML (XSS concern worth discussing), backend storing raw markdown vs rendered HTML.
8. In-app notifications
Notification bell in the header. Get notified when an issue assigned to you is updated, or when someone comments. Feeds from the activity log.
9. Mention system (@username in comments)
Tagging users in comments. Teaches text parsing, mention resolution, linking to user profiles.
10. Issue labels/tags
Many-to-many relationship between issues and tags. Teaches join tables in SQLAlchemy, array filtering.
