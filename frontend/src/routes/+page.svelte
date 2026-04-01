<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
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
	import {wsClient} from '$lib/websocket.svelte'

	let issues = $state<Issue[]>([]);
	let users = $state<User[]>([]);
	let loading = $state(true);
	let filters = $state<IssueFilters>({ search: '', severity: null, status: null });

	const PAGE_SIZE = 5;
	let currentPage = $state(1);
	let totalPages = $state(0);
	let totalItems = $state(0);
	let cleanupWS: (()=>void)|null = null

	let stats = $state({
		total: 0,
		by_status: { new: 0, in_progress: 0, resolved: 0, closed: 0 },
        by_severity: { low: 0, medium: 0, high: 0, critical: 0 }
	});

	$effect(() => {
		filters.search;
		filters.status;
		filters.severity;
		currentPage;
		fetchIssue()
	});

	async function fetchIssue() {
		loading = true;
		const params = new URLSearchParams({
            page: currentPage.toString(),
            size: PAGE_SIZE.toString(),
            ...(filters.search && { search: filters.search }),
            ...(filters.status && { status: filters.status }),
            ...(filters.severity && { severity: filters.severity })
        });
		const res = await apiFetch(`/issues?${params}`);
		if (res.ok) {
			const data = await res.json();
			issues = data.items;
			totalPages = data.pages
			totalItems = data.total
			stats = data.stats
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

		wsClient.connect('dashboard')
		cleanupWS = wsClient.onMessage((msg)=>{
			if (['issue_created', 'issue_updated', 'issue_deleted'].includes(msg.type)){
				fetchIssue()
			}
		})
	});

	onDestroy(()=>{
		cleanupWS?.()
		wsClient.disconnect()
	})
</script>

<div class="min-h-screen bg-background">
	<header class="mb-4 flex items-center justify-between border-b px-6 py-4">
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
			issues={issues}
			{users}
			{loading}
			currentUserId={authStore.user?.id ?? ''}
			onDeleted={fetchIssue}
			onUpdated={fetchIssue}
		/>
		<Pagination {currentPage} {totalPages} onPageChange={(p) => (currentPage = p)} />
	</main>
</div>
