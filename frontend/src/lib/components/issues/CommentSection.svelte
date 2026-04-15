<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import CommentForm from './CommentForm.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Pencil, Trash2 } from 'lucide-svelte';
	import { Separator } from '$lib/components/ui/separator';
	import { wsClient } from '$lib/websocket.svelte';

	let {
		issueId,
		issueCreatorId,
		onCountChanged
	}: {
		issueId: string;
		issueCreatorId: string;
		onCountChanged: () => void;
	} = $props();

	type Comment = {
		id: string;
		content: string;
		commenter: { id: string; email: string; full_name: string };
		created_at: string;
		updated_at: string;
	};

	let comments = $state<Comment[]>([]);
	let total = $state(0);
	let offset = $state(0);
	const LIMIT = 20;

	let editingId = $state<string | null>(null);
	let editContent = $state('');

	let hasMore = $derived(offset + LIMIT < total);

	async function fetchComments(reset = false) {
		const currentOffset = reset ? 0 : offset;
		const res = await apiFetch(
			`/issues/${issueId}/comments?limit=${LIMIT}&offset=${currentOffset}`
		);
		if (!res.ok) return;
		const data = await res.json();
		if (reset) {
			comments = data.items;
			offset = 0;
		} else {
			comments = [...comments, ...data.items];
		}
		total = data.total;
	}

	async function loadMore() {
		offset += LIMIT;
		await fetchComments();
	}

	async function handleDelete(commentId: string) {
		await apiFetch(`/issues/${issueId}/comments/${commentId}`, {
			method: 'DELETE'
		});
		await fetchComments(true);
		onCountChanged();
	}

	async function handleEdit(commentId: string) {
		await apiFetch(`/issues/${issueId}/comments/${commentId}`, {
			method: 'PATCH',
			body: JSON.stringify({ content: editContent })
		});
		editingId = null;
		await fetchComments(true);
	}

	function startEdit(comment: Comment) {
		editingId = comment.id;
		editContent = comment.content;
	}

	onMount(() => {
		fetchComments(true);

		wsClient.connect(`issue:${issueId}`);
		const cleanup = wsClient.onMessage((msg) => {
			if (['comment_created', 'comment_deleted'].includes(msg.type)) {
				fetchComments(true);
				onCountChanged();
			}
		});
	});
</script>

<div class="space-y-4">
	<h3 class="text-sm font-medium text-muted-foreground">
		{total}
		{total === 1 ? 'comment' : 'comments'}
	</h3>

	{#each comments as comment (comment.id)}
		<div class="space-y-1">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span class="text-sm font-medium">{comment.commenter.full_name}</span>
					<span class="text-xs text-muted-foreground">
						{new Date(comment.created_at).toLocaleDateString()}
					</span>
				</div>

				{#if comment.commenter.id === authStore.user?.id || issueCreatorId === authStore.user?.id}
					<div class="flex gap-1">
						{#if comment.commenter.id === authStore.user?.id}
							<Button
								variant="ghost"
								size="icon"
								title="Edit comment"
								onclick={() => startEdit(comment)}
							>
								<Pencil class="h-3 w-3" />
							</Button>
						{/if}
						<Button
							variant="ghost"
							size="icon"
							title="Delete comment"
							class="text-destructive hover:text-destructive"
							onclick={() => handleDelete(comment.id)}
						>
							<Trash2 class="h-3 w-3" />
						</Button>
					</div>
				{/if}
			</div>

			{#if editingId === comment.id}
				<div class="space-y-2">
					<Textarea bind:value={editContent} rows={2} />
					<div class="flex gap-2">
						<Button size="sm" onclick={() => handleEdit(comment.id)}>Save</Button>
						<Button size="sm" variant="outline" onclick={() => (editingId = null)}>Cancel</Button>
					</div>
				</div>
			{:else}
				<p class="text-sm">{comment.content}</p>
			{/if}
		</div>
		<Separator />
	{/each}

	{#if hasMore}
		<Button variant="outline" size="sm" onclick={loadMore}>Load more comments</Button>
	{/if}

	<CommentForm
		{issueId}
		onCommentAdded={() => {
			fetchComments(true);
			onCountChanged();
		}}
	/>
</div>
