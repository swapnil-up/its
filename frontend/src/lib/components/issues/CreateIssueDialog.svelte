<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Select from '$lib/components/ui/select';
	import { apiFetch } from '$lib/api';
	import { Plus } from 'lucide-svelte'
	import type { User } from '$lib/types';

	let { onCreated, users=$bindable() }: { onCreated: () => void; users: User[] } = $props();

	let open = $state(false);
	let title = $state('');
	let description = $state('');
	let severity = $state('low');
	let loading = $state(false);
	let error = $state<string | null>(null);
	let assigned_to = $state<string>('');

	let assigneeName = $derived(users.find((u) => u.id === assigned_to)?.full_name ?? "Unassigned");
	let isValid = $derived(title.length > 0 && description.length > 0);
	$effect(()=>{
		if (!open){
			resetForm();
		}else{
			syncFreshData();
		}
	})

	async function syncFreshData() {
		const usersRes = await apiFetch('/users')
		if (usersRes.ok) {
			users = await usersRes.json();
		}
	}


	async function handleCreate() {
		loading = true;
		error = null;
		const res = await apiFetch('/issues', {
			method: 'POST',
			body: JSON.stringify({ title, description, severity, assigned_to: assigned_to===""? null:assigned_to })
		});
		if (res.ok) {
			open = false;
			title = '';
			description = '';
			severity = 'low';
			onCreated();
		} else {
			const data = await res.json();
			error = data.detail ? `${data.detail[0].msg} . ${data.detail[0].input}` : 'Failed to create issue';
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

	function resetForm(){
		title = '';
		description = '';
		severity = 'low';
		loading = false;
		error = null;
		assigned_to=""
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger>
		<Button><Plus class="h-4 w-4 mr-2" /> New Issue</Button>
	</Dialog.Trigger>
	<Dialog.Content>
		<Dialog.Header><Dialog.Title>Create Issue</Dialog.Title></Dialog.Header>
		<div class="space-y-4 py-2">
			<Label for="title">Title</Label>
			<Input id="title" bind:value={title} placeholder="Brief description of the issue" />
			<Label for="desc">Description</Label>
			<Textarea id="desc" bind:value={description} placeholder="Full details..." rows={4} />
			<Label for="severity">Severity</Label>
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
			<Label for="assigned">Assigned To</Label>
			<Select.Root type="single" bind:value={assigned_to}>
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
			<p class="text-destructive break-words">{error}</p>
		{/if}

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
			<Button variant="destructive" disabled={!isValid || loading} onclick={handleCreate}
				>{loading ? 'Creating...' : 'Create'}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
