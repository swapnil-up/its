<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import type { Issue, IssueFilters, User } from '$lib/types';
	import IssueFiltersComponent from '$lib/components/issues/IssueFilters.svelte';
	import IssueTable from '$lib/components/issues/IssueTable.svelte';
	import CreateIssueDialog from '$lib/components/issues/CreateIssueDialog.svelte';
	import { Button } from '$lib/components/ui/button';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import StatsBar from '$lib/components/issues/StatsBar.svelte';
	import { Bug, LogOut, Sun, Moon } from 'lucide-svelte';
	import { themeStore } from '$lib/stores/theme.svelte';
	import Pagination from '$lib/components/issues/Pagination.svelte';

	let issues = $state<Issue[]>([]);
	let users = $state<User[]>([]);
	let loading = $state(true);
	let filters = $state<IssueFilters>({ search: '', severity: null, status: null });

	let filteredIssues = $derived(
		issues.filter((issue) => {
			if (filters.search && !issue.title.toLowerCase().includes(filters.search.toLowerCase()))
				return false;
			if (filters.status && issue.status !== filters.status) return false;
			if (filters.severity && issue.severity !== filters.severity) return false;
			return true;
		})
	);

	let stats = $derived({
		total: issues.length,
		by_status: {
			new: issues.filter((i) => i.status === 'new').length,
			in_progress: issues.filter((i) => i.status === 'in_progress').length,
			resolved: issues.filter((i) => i.status === 'resolved').length,
			closed: issues.filter((i) => i.status === 'closed').length
		},
		by_severity: {
			low: issues.filter((i) => i.severity === 'low').length,
			medium: issues.filter((i) => i.severity === 'medium').length,
			high: issues.filter((i) => i.severity === 'high').length,
			critical: issues.filter((i) => i.severity === 'critical').length
		}
	});

	const PAGE_SIZE = 5;
	let currentPage = $state(1);
	$effect(() => {
		filters.search;
		filters.status;
		filters.severity;
		currentPage = 1;
	});

	let totalPages = $derived(Math.ceil(filteredIssues.length/PAGE_SIZE))
	let paginatedIssues = $derived(
		filteredIssues.slice(
			(currentPage -1)*PAGE_SIZE,
			currentPage*PAGE_SIZE
		)
	)

	async function fetchIssue() {
		loading = true;
		const res = await apiFetch('/issues');
		if (res.ok) {
			issues = await res.json();
		}
		loading = false;
	}

	async function fetchUsers() {
		loading = true;
		const res = await apiFetch('/users');
		if (res.ok) {
			users = await res.json();
		}
		loading = false;
	}

	async function handleLogout() {
		await apiFetch('/auth/logout', { method: 'POST' });
		authStore.clearAuth();
		goto('/login');
	}

	onMount(() => {
		fetchIssue();
		fetchUsers();
	});
</script>

<div class="min-h-screen bg-background">
	<header class="flex items-center justify-between border-b px-6 py-4 mb-4">
		<h1 class="flex items-center gap-2 text-xl font-semibold">
			<Bug class="h-5 w-5" /> Issue Tracker
		</h1>

		<h1 class="flex items-center gap-3">
			<span class="text-sm">{authStore.user?.email}</span>
			<Button variant="ghost" size="icon" onclick={themeStore.toggle} title="Toggle theme">
				{#if themeStore.isDark}
					<Sun class="h-4 w-4" />
				{:else}
					<Moon class="h-4 w-4" />
				{/if}
			</Button>
			<Button variant="outline" size="sm" onclick={handleLogout}
				><LogOut class="mr-2 h-4 w-4" /> Logout</Button
			>
		</h1>
	</header>

	<StatsBar {stats} />

	<main class="space-y-4 px-6 py-6">
		<div class="flex items-center justify-between gap-3">
			<IssueFiltersComponent bind:filters />
			<CreateIssueDialog onCreated={fetchIssue} {users} />
		</div>

		<IssueTable
			issues={paginatedIssues}
			{users}
			{loading}
			currentUserId={authStore.user?.id ?? ''}
			onDeleted={fetchIssue}
			onUpdated={fetchIssue}
		/>
		<Pagination {currentPage} {totalPages} onPageChange={(p)=>currentPage = p}/>
	</main>
</div>
