<script lang="ts">
	import * as Table from '$lib/components/ui/table';
	import * as Select from '$lib/components/ui/select';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import EditIssueDialog from './EditIssueDialog.svelte';
	import { apiFetch } from '$lib/api';
	import { Trash2 } from 'lucide-svelte';
	import type { Issue, User } from '$lib/types';
	import CommentSection from './CommentSection.svelte';
	import AttachmentSection from './AttachmentSection.svelte';

	let {
		issues = $bindable(),
		users,
		loading,
		currentUserId,
		onUpdated,
		onDeleted
	}: {
		issues: Issue[];
		users: User[];
		loading: boolean;
		currentUserId: string;
		onUpdated: () => void;
		onDeleted: () => void;
	} = $props();

	let deleteItem = $state<Issue | null>(null);
	let deleting = $state(false);
	let selectedIssue = $state<Issue | null>(null);

	const getLabel = (value: string | null, options: { label: string; value: string }[]) => {
		if (!value) return null;
		return options.find((o) => o.value === value)?.label;
	};

	const statusOptions = [
		{ label: 'New', value: 'new' },
		{ label: 'In Progress', value: 'in_progress' },
		{ label: 'Resolved', value: 'resolved' },
		{ label: 'Closed', value: 'closed' }
	];

	const severityOptions = [
		{ label: 'Low', value: 'low' },
		{ label: 'Medium', value: 'medium' },
		{ label: 'High', value: 'high' },
		{ label: 'Critical', value: 'critical' }
	];

	async function handleStatusChange(issue: Issue, newStatus: string) {
		await apiFetch(`/issues/${issue.id}`, {
			method: 'PATCH',
			body: JSON.stringify({ status: newStatus })
		});
		onUpdated();
	}

	async function handleSeverityChange(issue: Issue, newSeverity: string) {
		await apiFetch(`/issues/${issue.id}`, {
			method: 'PATCH',
			body: JSON.stringify({ severity: newSeverity })
		});
		onUpdated();
	}

	async function confirmDelete() {
		if (!deleteItem) return;
		deleting = true;
		await apiFetch(`/issues/${deleteItem.id}`, { method: 'DELETE' });
		deleting = false;
		deleteItem = null;
		onDeleted();
	}

	async function refreshSelectedIssue() {
		if (!selectedIssue) return;
		loading = true;
		try {
			const response = await apiFetch(`/issues/${selectedIssue.id}`);
			if (!response.ok) throw new Error('Failed to fetch');
			const updated = (await response.json()) as Issue;
			selectedIssue = updated;
			onUpdated();
		} catch (e) {
			console.error('Failed to refresh ', e);
		} finally {
			loading = false;
		}
	}
</script>

{#if loading}
	<div class="py-12 text-center">Loading issues...</div>
{:else if issues.length === 0}
	<div class="py-12 text-center">No issues found.</div>
{:else}
	<Table.Root class="w-full table-fixed">
		<Table.Header>
			<Table.Row>
				<Table.Head>ID</Table.Head>
				<Table.Head class="w-1/3">Title</Table.Head>
				<Table.Head>Status</Table.Head>
				<Table.Head>Severity</Table.Head>
				<Table.Head>Created By</Table.Head>
				<Table.Head>Assigned To</Table.Head>
				<Table.Head>Created At</Table.Head>
				<Table.Head>Actions</Table.Head>
			</Table.Row>
		</Table.Header>
		<Table.Body>
			{#each issues as issue (issue.id)}
				<Table.Row>
					<Table.Cell>{issue.id.slice(0, 8)}</Table.Cell>
					<Table.Cell
						class="cursor-pointer font-medium hover:underline"
						onclick={() => (selectedIssue = issue)}
					>
						{issue.title}
					</Table.Cell>
					<Table.Cell>
						<Select.Root
							type="single"
							bind:value={issue.status}
							onValueChange={(newStatus) => handleStatusChange(issue, newStatus)}
						>
							<Select.Trigger>
								{getLabel(issue.status, statusOptions)}
							</Select.Trigger>
							<Select.Content>
								{#each statusOptions as opt}
									<Select.Item value={opt.value}>{opt.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</Table.Cell>
					<Table.Cell
						><Select.Root
							type="single"
							bind:value={issue.severity}
							onValueChange={(newSeverity) => handleSeverityChange(issue, newSeverity)}
						>
							<Select.Trigger>
								{getLabel(issue.severity, severityOptions)}
							</Select.Trigger>
							<Select.Content>
								{#each severityOptions as opt}
									<Select.Item value={opt.value}>{opt.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</Table.Cell>
					<Table.Cell>{issue.creator.full_name}</Table.Cell>
					<Table.Cell>{issue.assignee?.full_name ?? 'Unassigned'}</Table.Cell>
					<Table.Cell>{new Date(issue.created_at).toLocaleDateString()}</Table.Cell>
					<Table.Cell>
						<div class="flex gap-2">
							<!-- <pre>{issue.creator.id}//{currentUserId}</pre> -->
							<EditIssueDialog {issue} {users} {onUpdated} />
							{#if issue.creator.id == currentUserId}
								<Button
									variant="ghost"
									size="sm"
									class="text-destructive hover:text-destructive"
									onclick={() => (deleteItem = issue)}><Trash2 class="h-4 w-4" /></Button
								>
							{/if}
						</div>
					</Table.Cell>
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>
{/if}

<Dialog.Root
	open={deleteItem != null}
	onOpenChage={(o) => {
		if (!o) deleteItem = null;
	}}
>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Are you sure you want to delete issue?</Dialog.Title>
			<Dialog.Description class="break-words"
				>"{deleteItem?.title}" will be deleted permanently.</Dialog.Description
			>
		</Dialog.Header>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (deleteItem = null)}>Cancel</Button>
			<Button variant="destructive" disabled={deleting} onclick={confirmDelete}
				>{deleting ? 'Deleting...' : 'Delete'}</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<Dialog.Root
	open={selectedIssue !== null}
	onOpenChange={(o) => {
		if (!o) selectedIssue = null;
	}}
>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title>{selectedIssue?.title}</Dialog.Title>
			<Dialog.Description class="text-sm">{selectedIssue?.description}</Dialog.Description>
		</Dialog.Header>

		<div class="flex-1 overflow-y-auto px-1">
			{#if selectedIssue}
				<div class="mb-6 rounded-lg border bg-muted/30 p-4">
					<AttachmentSection
						issueId={selectedIssue.id}
						issueCreatorId={selectedIssue.creator.id}
						attachments={selectedIssue.attachments || []}
						onChanged={refreshSelectedIssue}
					/>
				</div>
				<CommentSection
					issueId={selectedIssue.id}
					issueCreatorId={selectedIssue.creator_id}
					onCountChanged={onUpdated}
				/>
			{/if}
		</div>
	</Dialog.Content>
</Dialog.Root>
