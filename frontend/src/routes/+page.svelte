<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import type { Issue, IssueFilters } from '$lib/types';
	import IssueFiltersComponent from '$lib/components/issues/IssueFilters.svelte';
	import IssueTable from '$lib/components/issues/IssueTable.svelte';
	import CreateIssueDialog from '$lib/components/issues/CreateIssueDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	let issues = $state<Issue[]>([
        {
            id: '1',
            title: 'Fix i3wm workspace flicker',
            description: 'Workspace flickering when switching between monitor 1 and 2.',
            severity: 'high',
            status: 'in_progress',
            assigned_to: '101',
            created_by: '101',
            created_at: '2026-03-20T09:00:00Z',
            updated_at: '2026-03-21T10:00:00Z'
        },
        {
            id: '2',
            title: 'Anki Devanagari deck sync error',
            description: 'Syncing characters fails on Linux mobile client.',
            severity: 'medium',
            status: 'new',
            assigned_to: null,
            created_by: '101',
            created_at: '2026-03-22T14:30:00Z',
            updated_at: '2026-03-22T14:30:00Z'
        },
        {
            id: '3',
            title: 'NEPSE API rate limit handler',
            description: 'Implement exponential backoff for stock data fetcher.',
            severity: 'critical',
            status: 'resolved',
            assigned_to: '101',
            created_by: '102',
            created_at: '2026-03-23T08:15:00Z',
            updated_at: '2026-03-23T11:00:00Z'
        }
    ]);
	let loading = $state(true);
	let filters = $state<IssueFilters>({ search: '', severity: null, status: null });

	let filteredIsues = $derived(
		issues.filter((issue) => {
			if (filters.search && !issue.title.toLowerCase().includes(filters.search.toLowerCase()))
				return false;
			if (filters.status && issue.status !== filters.status) return false;
			if (filters.severity && issue.severity !== filters.severity) return false;
			return true;
		})
	);

	async function fetchIssue() {
		loading = true;
		const res = await apiFetch('/issues');
		if (res.ok) {
			issues = await res.json();
		}
		loading = false;
	}

	async function handleLogout() {
		await apiFetch('/auth/logout', { method: 'POST' });
		authStore.clearAuth();
		goto('/login');
	}

	onMount(fetchIssue);
</script>

<div class="min-h-screen bg-background">
	<header class="flex items-center justify-between border-b px-6 py-4">
		<h1 class="flex items-center gap-3">
			<span class="text-sm">{authStore.user?.email}</span>
			<Button variant="outline" size="sm" onclick={handleLogout}>Logout</Button>
		</h1>
	</header>

	<main class="space-y-4 px-6 py-6">
		<div class="flex items-center justify-between">
			<IssueFiltersComponent bind:filters />
			<!-- <CreateIssueDialog onCreated={fetchIssues} /> -->
		</div>

		<IssueTable
			issues={filteredIsues}
			{loading}
			currentUserId={authStore.user?.id ?? ''}
			 
		/>
	</main>
</div>
