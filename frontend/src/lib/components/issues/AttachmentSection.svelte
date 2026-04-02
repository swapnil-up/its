<script lang="ts">
	import { apiFetch } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Paperclip, Trash2, Download } from 'lucide-svelte';
	import type { Attachment } from '$lib/types';

	let {
		issueId,
		issueCreatorId,
		attachments = [],
		onChanged
	}: {
		issueId: string;
		issueCreatorId: string;
		attachments: Array<Attachment>;
		onChanged: () => void;
	} = $props();

	let uploading = $state(false);
	let error = $state<string | null>(null);

	let fileInput: HTMLInputElement;

	function triggerFileInput() {
		fileInput.click();
	}
	function formatBytes(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	async function handleFileChange(e: Event) {
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		uploading = true;
		error = null;

		const formData = new FormData();
		formData.append('file', file);

		const res = await fetch(`http://localhost:8000/issues/${issueId}/attachments`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`
			},
			body: formData,
			credentials: 'include'
		});

		if (res.ok) {
			onChanged();
		} else {
			const data = await res.json();
			error = data.detail ?? 'Upload failed';
		}

		uploading = false;
		input.value = '';
	}

	async function handleDelete(attachmentId: string) {
		await apiFetch(`/issues/${issueId}/attachments/${attachmentId}`, {
			method: 'DELETE'
		});
		onChanged();
	}

	function isImage(contentType: string) {
		return contentType.startsWith('image/');
	}
</script>

<div class="space-y-3">
	<div class="flex items-center justify-between">
		<h3 class="flex items-center gap-1 text-sm font-medium text-muted-foreground">
			<Paperclip class="h-3 w-3" />
			{attachments.length}
			{attachments.length === 1 ? 'attachment' : 'attachments'}
		</h3>
		<Button variant="outline" size="sm" disabled={uploading} onclick={triggerFileInput}>
			{uploading ? 'Uploading...' : 'Attach file'}
		</Button>

		<input
			bind:this={fileInput}
			type="file"
			class="hidden"
			accept="image/*,.pdf,.txt"
			onchange={handleFileChange}
		/>
	</div>

	{#if error}
		<p class="text-sm text-destructive">{error}</p>
	{/if}

	{#each attachments as attachment (attachment.id)}
		<div class="flex items-center justify-between rounded-md border px-3 py-2">
			<div class="flex min-w-0 items-center gap-2">
				{#if isImage(attachment.content_type)}
					<img
						src={attachment.url}
						alt={attachment.filename}
						class="h-8 w-8 shrink-0 rounded object-cover"
					/>
				{:else}
					<Paperclip class="h-4 w-4 shrink-0 text-muted-foreground" />
				{/if}
				<div class="min-w-0">
					<p class="truncate text-sm font-medium">{attachment.filename}</p>
					<p class="text-xs text-muted-foreground">
						{formatBytes(attachment.size)} · {attachment.uploader?.full_name ?? "Unknown Uploader"}
					</p>
				</div>
			</div>
			<div class="ml-2 flex shrink-0 items-center gap-1">
				<a href={attachment.url} target="_blank" rel="noopener noreferrer">
					<Button variant="ghost" size="icon" title="Download">
						<Download class="h-3 w-3" />
					</Button>
				</a>
				{#if attachment.uploader?.id === authStore.user?.id || issueCreatorId === authStore.user?.id}
					<Button
						variant="ghost"
						size="icon"
						title="Delete attachment"
						class="text-destructive hover:text-destructive"
						onclick={() => handleDelete(attachment.id)}
					>
						<Trash2 class="h-3 w-3" />
					</Button>
				{/if}
			</div>
		</div>
	{/each}
</div>
