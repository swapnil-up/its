<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Select from '$lib/components/ui/select';
	import { apiFetch } from '$lib/api';
	import type { Issue, User } from '$lib/types';
	import { Pencil } from 'lucide-svelte'


	let { onUpdated, issue, users }: { onUpdated: () => void; issue: Issue; users: User[] } =
		$props();

	let open = $state(false);
	let description = $state('');
	let severity = $state('low');
	let loading = $state(false);
	let error = $state<string | null>(null);
	let assignee = $state<string>(issue.assigned_to ?? '');

	let isValid = $derived(description.length > 0);
	let assigneeName = $derived(users.find((u) => u.id === assignee)?.full_name ?? 'Unassigned');

	$effect(() => {
		if (open) {
			description = issue.description;
			severity = issue.severity;
			assignee = issue.assigned_to ?? '';
		}
	});

	async function handleUpdate() {
		loading = true;
		error = null;
		const res = await apiFetch(`/issues/${issue.id}`, {
			method: 'PATCH',
			body: JSON.stringify({ description, severity, assigned_to: assignee || null })
		});
		if (res.ok) {
			open = false;
			onUpdated();
		} else {
			const data = await res.json();
			error = data.detail ?? 'Failed to update issue';
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
		<Button variant="ghost" size="sm"><Pencil class="h-4 w-4" /></Button>
	</Dialog.Trigger>
	<Dialog.Content>
		<Dialog.Header
			><Dialog.Title>Update Issue</Dialog.Title>
			<Dialog.Description>
				{issue.title}
			</Dialog.Description></Dialog.Header
		>
		<div class="space-y-4 py-2">
			<Label for="desc">Description</Label>
			<Textarea id="desc" bind:value={description} placeholder="Full details..." rows={4} />

			<Label for="severity">Severity</Label>
			<Select.Root type="single" bind:value={severity}>
				<Select.Trigger>
					{getLabel(severity, severityOptions)}
				</Select.Trigger>
				<Select.Content>
					{#each severityOptions as opt}
						<Select.Item value={opt.value}>{opt.label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>

			<Label for="assigned">Assigned To</Label>
			<Select.Root type="single" bind:value={assignee}>
				<Select.Trigger>
					{assigneeName}
				</Select.Trigger>
				<Select.Content>
					<Select.Item value="">Unassigned</Select.Item>
					{#each users as user}
						<Select.Item value={user.id}>{user.full_name}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		</div>
		{#if error}
			<p class="text-destructive">{error}</p>
		{/if}

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
			<Button variant="destructive" disabled={loading || !isValid} onclick={handleUpdate}
				>{loading ? 'Updating...' : 'Update'}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
