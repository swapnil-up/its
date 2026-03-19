<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import { isAuthenticated } from '$lib/stores/auth';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    let { children } = $props();

    const PUBLIC_ROUTES = ['/login', '/register'];

    $effect(() => {
        const isPublic = PUBLIC_ROUTES.includes($page.url.pathname);
        
        if (!$isAuthenticated && !isPublic) {
            goto('/login');
        }
    });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
