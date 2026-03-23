<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import { authStore } from '$lib/stores/auth.svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    let { children } = $props();

    const PUBLIC_ROUTES = ['/login', '/register'];
    const isPublic = PUBLIC_ROUTES.includes($page.url.pathname);

    $effect(() => {
        
        if (!authStore.isAuthenticated && !isPublic) {
            goto('/login');
        }
    });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{#if (authStore.isAuthenticated || isPublic)}
{@render children()}
{/if}
