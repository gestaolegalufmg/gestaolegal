<script lang="ts">
	import '../app.css';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { Toaster } from 'svelte-sonner';
	import { ehRotaPublica } from '$lib/utils/rotas';

	let { children } = $props();

	onMount(() => {
		if (browser) {
			const hasAuthToken = document.cookie.split('; ').find((row) => row.startsWith('auth_token='));
			if (!hasAuthToken && !ehRotaPublica(page.url.pathname)) {
				goto('/login');
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
	<link rel="icon" type="image/png" sizes="512x512" href="/favicon-512.png" />
	<link rel="apple-touch-icon" href="/favicon-512.png" />
</svelte:head>

<!-- No layout raiz para que as telas públicas (login, setup-admin) também
	 exibam toasts: antes ele ficava só no layout do dashboard e os erros
	 dessas telas eram emitidos sem nada que os renderizasse. -->
<Toaster position="top-center" richColors />

{@render children?.()}
