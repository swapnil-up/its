<script lang="ts">
	import { Input } from '$lib/components/ui/input';
	import * as Select from '$lib/components/ui/select';
	import type { IssueFilters } from '$lib/types';

	let { filters = $bindable() }: { filters: IssueFilters } = $props();

	const getLabel = (value: string | null, options: { label: string; value: string }[]) => {
		if (!value) return null;
		return options.find((o) => o.value === value)?.label;
	};

	const statusOptions = [
		{ label: 'All statuses', value: '' },
		{ label: 'New', value: 'new' },
		{ label: 'In Progress', value: 'in_progress' },
		{ label: 'Resolved', value: 'resolved' },
		{ label: 'Closed', value: 'closed' }
	];

	const severityOptions = [
		{ label: 'All severities', value: '' },
		{ label: 'Low', value: 'low' },
		{ label: 'Medium', value: 'medium' },
		{ label: 'High', value: 'high' },
		{ label: 'Critical', value: 'critical' }
	];
</script>

<div class="flex flex-1 items-center gap-3">
	<pre class="fixed right-0 bottom-0 z-50 bg-black/80 p-4 text-xs text-green-400">{JSON.stringify(
			filters,
			null,
			2
		)}</pre>

	<Input placeholder="Search by title..." bind:value={filters.search} />

	<Select.Root type="single" bind:value={filters.status}>
		<Select.Trigger>
			{getLabel(filters.status, statusOptions) || 'All statuses'}
		</Select.Trigger>
		<Select.Content>
			{#each statusOptions as opt}
				<Select.Item value={opt.value}>{opt.label}</Select.Item>
			{/each}
		</Select.Content>
	</Select.Root>

	<Select.Root type="single" bind:value={filters.severity}>
		<Select.Trigger>
			{getLabel(filters.severity, severityOptions) || 'All severities'}
		</Select.Trigger>
		<Select.Content>
			{#each severityOptions as opt}
				<Select.Item value={opt.value}>{opt.label}</Select.Item>
			{/each}
		</Select.Content>
	</Select.Root>
</div>
