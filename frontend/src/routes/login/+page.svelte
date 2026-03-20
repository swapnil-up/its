<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { apiFetch } from '$lib/api';
	import { authStore } from '$lib/stores/auth.svelte';

	let email = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state<string | null>(null);

	let justRegistered = $derived($page.url.searchParams.get('registered') === 'true');
	let isValid = $derived(email.includes('@') && password.length >= 0);

	async function handleLogin() {
		loading = true;
		error = null;
		try {
			const res = await apiFetch('/auth/login', {
				method: 'POST',
				body: JSON.stringify({ email, password })
			});
			if (!res.ok) {
				error = 'Invalid email or password';
				return;
			}
			const { access_token } = await res.json();

			const user = await apiFetch('/me', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${access_token}`
				}
			});
			const { user_data } = await user.json();
			authStore.setAuth(access_token, user_data);
			goto('/');
		} catch {
			error = 'Could not reach server';
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-background">
	<Card.Root class="w-full max-w-md">
		{#if justRegistered}
			<div class="px-6 pt-6">
				<Alert
					class="border-green-500 bg-green-50/50 text-green-700 dark:bg-green-950/20 dark:text-green-400"
				>
					<div class="flex items-center gap-2">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							class="lucide lucide-check-circle-2"
							><path
								d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"
							/><path d="m9 12 2 2 4-4" /></svg
						>
						<AlertDescription>Registration successful! Please log in.</AlertDescription>
					</div>
				</Alert>
			</div>
		{/if}
		<Card.Header>
			<Card.Title>Login</Card.Title>
			<Card.Description>Start tracking issues today</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			{#if error}
				<Alert variant="destructive">
					<AlertDescription>{error}</AlertDescription>
				</Alert>
			{/if}

			<div class="space-y-2">
				<Label for="email">Email</Label>
				<Input id="email" type="email" bind:value={email} placeholder="ada@example.com" />
			</div>
			<div class="space-y-2">
				<Label for="password">Password</Label>
				<Input id="password" type="password" bind:value={password} placeholder="8+ characters" />
			</div>
		</Card.Content>
		<Card.Footer class="flex flex-col gap-3">
			<Button class="w-full" disabled={!isValid || loading} onclick={handleLogin}>
				{loading ? 'Logging in...' : 'Login'}
			</Button>
			<p class="text-center text-sm text-muted-foreground">
				Don't have an account yet?
				<a href="/login" class="underline">Register</a>
			</p>
		</Card.Footer>
	</Card.Root>
</div>
