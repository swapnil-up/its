<script lang="ts">
	import * as Table from '$lib/components/ui/table';
	import * as Select from '$lib/components/ui/select';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import EditIssueDialog from './EditIssueDialog.svelte';
	import { apiFetch } from '$lib/api';
	import type { Issue } from '$lib/types';
	let {
		issues,
		loading,
		currentUserId,
	}: {
		issues: Issue[];
		loading: boolean;
		currentUserId: string;
	} = $props();

    async function handleStatusChange(issue:Issue, newStatus: string) {
        await apiFetch('/issues/${issue.id}', {
            method: 'PATCH', 
            body: JSON.stringify({status: newStatus})
        })
    }
</script>

{#if loading}
<div class="text-center py-12">Loading issues...</div>
{:else if issues.length===0}
<div class="text-center py-12">No issues found.</div>
{:else}
<Table.Root>
    <Table.Header>
        <Table.Row>
            <Table.Head>Title</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head>Severity</Table.Head>
            <Table.Head>Created</Table.Head>
            <Table.Head>Actions</Table.Head>
        </Table.Row>
    </Table.Header>
    <Table.Body>
        {#each issues as issue (issue.id)}
        <Table.Row>
            <Table.Cell>{issue.title}</Table.Cell>
            <Table.Cell>{issue.status}</Table.Cell>
            <Table.Cell>{issue.severity}</Table.Cell>
            <Table.Cell>{new Date(issue.created_at).toLocaleDateString()}</Table.Cell>
            <Table.Cell>Edit/ Delete</Table.Cell>
        </Table.Row>
        {/each}
    </Table.Body>
</Table.Root>
{/if}