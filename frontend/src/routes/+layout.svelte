<script lang="ts">
	import '../app.css';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	let { children } = $props();

	// Client-side authentication guard
	onMount(() => {
		if (browser) {
			// Check if auth_token cookie exists
			const hasAuthToken = document.cookie
				.split('; ')
				.find((row) => row.startsWith('auth_token='));

			const isPublicRoute = $page.url.pathname === '/login';

			// Redirect to login if not authenticated and not already on login page
			if (!hasAuthToken && !isPublicRoute) {
				goto('/login');
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" type="image/png" href="/favicon.png" />
</svelte:head>

{@render children?.()}
