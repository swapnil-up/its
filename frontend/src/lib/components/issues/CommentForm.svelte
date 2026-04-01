<script lang="ts">
	import { Textarea } from '$lib/components/ui/textarea';
	import { Button } from '$lib/components/ui/button';
	import { apiFetch } from '$lib/api';

	let {
		issueId,
		onCommentAdded
	}: {
		issueId: string;
		onCommentAdded: () => void;
	} = $props();

	let content = $state('');
	let loading = $state(false);
	let isValid = $derived(content.trim().length > 0);

	async function handleSubmit() {
		loading = true;
		const res = await apiFetch(`/issues/${issueId}/comments`, {
			method: 'POST',
			body: JSON.stringify({ content })
		});
		if (res.ok) {
			content = '';
			onCommentAdded();
		}
		loading = false;
	}
</script>

<div class="space-y-2">
	<Textarea bind:value={content} placeholder="Add a comment..." rows={3} />
	<div class="flex justify-end">
		<Button size="sm" disabled={!isValid || loading} onclick={handleSubmit}>
			{loading ? 'Posting...' : 'Post comment'}
		</Button>
	</div>
</div>
