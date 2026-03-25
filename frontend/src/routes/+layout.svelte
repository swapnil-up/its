<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import { authStore } from '$lib/stores/auth.svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
    import {themeStore} from '$lib/stores/theme.svelte'

    let { children } = $props();
    let verifying = $state(authStore.isAuthenticated);

    const PUBLIC_ROUTES = ['/login', '/register'];
    const isPublic = $derived(PUBLIC_ROUTES.includes($page.url.pathname));

    $effect(() => {
        if (!authStore.isAuthenticated && !isPublic) {
            goto('/login', {replaceState: true});
        }
    });

    onMount(async () => {
        themeStore.init()
        if (authStore.isAuthenticated) {
            try {
                const res = await apiFetch('/me');
                if (!res.ok) authStore.clearAuth(); 
                else{
                    const user_data = await res.json();
                    authStore.setUserData(user_data);
                } 
                    
            } finally {
                verifying = false; 
            }
        }
    });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{#if (authStore.isAuthenticated || isPublic) && !verifying}
{@render children()}
{:else}
    <div class="flex h-screen items-center justify-center">
        <p class="text-sm text-muted-foreground animate-pulse">Loading...</p>
    </div>
{/if}
