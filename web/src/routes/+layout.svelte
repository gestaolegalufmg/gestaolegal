<script lang="ts">
	import '../app.css';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';

	let { children } = $props();

	onMount(() => {
		if (browser) {
			const hasAuthToken = document.cookie.split('; ').find((row) => row.startsWith('auth_token='));
			const isPublicRoute = page.url.pathname === '/login';

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
