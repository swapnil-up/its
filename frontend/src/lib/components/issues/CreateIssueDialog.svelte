<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Select from '$lib/components/ui/select';
	import { apiFetch } from '$lib/api';

	let { onCreated }: { onCreated: () => void } = $props();

	let open = $state(false);
	let title = $state('');
	let description = $state('');
	let severity = $state('low');
	let loading = $state(false);
	let error = $state<string | null>(null);

	let isValid = $derived(title.length > 0 && description.length > 0);

	async function handleCreate() {
		loading = true;
		error = null;
		const res = await apiFetch('/issues/', {
			method: 'POST',
			body: JSON.stringify({ title, description, severity })
		});
		if (res.ok) {
			open = false;
			title = '';
			description = '';
			severity = 'low';
			onCreated();
		} else {
			const data = await res.json();
			error = data.detail ?? 'Failed to create issue';
		}
		loading = false;
	}

	const getLabel = (value: string | null, options: { label: string; value: string }[]) => {
		if (!value) return null;
		return options.find((o) => o.value === value)?.label;
	};

	const severityOptions = [
		{ label: 'Low', value: 'low' },
		{ label: 'Medium', value: 'medium' },
		{ label: 'High', value: 'high' },
		{ label: 'Critical', value: 'critical' }
	];
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		<Button>New Issue</Button>
	</Dialog.Trigger>
	<Dialog.Content>
		<Dialog.Header><Dialog.Title>Create Issue</Dialog.Title></Dialog.Header>
		<div class="space-y-4 py-2">
			<Label for="title">Title</Label>
			<Input id="title" bind:value={title} placeholder="Brief description of the issue" />
			<Label for="desc">Description</Label>
			<Textarea id="desc" bind:value={description} placeholder="Full details..." rows={4} />
			<Select.Root type="single" bind:value={severity}>
				<Select.Trigger>
					{getLabel(severity, severityOptions) || 'All severities'}
				</Select.Trigger>
				<Select.Content>
					{#each severityOptions as opt}
						<Select.Item value={opt.value}>{opt.label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		</div>
		{#if error}
			<p class="text-destructive">{error}</p>
		{/if}

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
			<Button variant="destructive" disabled={loading} onclick={handleCreate}
				>{loading ? 'Creating...' : 'Create'}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
