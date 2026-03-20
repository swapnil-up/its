<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import type { Issue, IssueFilters } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	let issues = $state<Issue[]>([]);
	let loading = $state(true);
	let filters = $state<IssueFilters>({ search: '', severity: null, status: null });


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

</div>
