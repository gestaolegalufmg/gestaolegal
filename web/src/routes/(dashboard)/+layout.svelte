<script lang="ts">
	import AppFooter from '$lib/components/app-footer.svelte';
	import AppSidebar from '$lib/components/app-sidebar.svelte';
	import DynamicBreadcrumb from '$lib/components/dynamic-breadcrumb.svelte';
	import GlobalSearchDialog from '$lib/components/global-search-dialog.svelte';
	import NotificacaoBell from '$lib/components/notificacao-bell.svelte';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import UnidadeSelector from '$lib/components/unidade-selector.svelte';
	import { unidadesAtivas } from '$lib/stores/unidade';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { page } from '$app/state';
	import Input from '$lib/components/ui/input/input.svelte';
	import { onMount } from 'svelte';

	let { children, data } = $props();

	const isOnRoot = $derived(page.url.pathname === '/');

	// Derivado, e não cópia: depois do invalidateAll() da troca de unidade o
	// `data` vem recarregado, e o cabeçalho precisa acompanhar.
	const user = $derived(data.me);
	let searchDialogOpen = $state(false);
	let headerSearchValue = $state('');

	function openSearchDialog() {
		searchDialogOpen = true;
	}

	function handleHeaderSearchInput(event: Event) {
		const target = event.target as HTMLInputElement;
		headerSearchValue = target.value;
		if (headerSearchValue.length > 0) {
			searchDialogOpen = true;
		}
	}

	onMount(() => {
		function handleKeyDown(event: KeyboardEvent) {
			if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
				event.preventDefault();
				openSearchDialog();
			}
		}

		document.addEventListener('keydown', handleKeyDown);

		return () => {
			document.removeEventListener('keydown', handleKeyDown);
		};
	});
</script>

<GlobalSearchDialog bind:open={searchDialogOpen} bind:initialQuery={headerSearchValue} />

<Sidebar.Provider>
	<AppSidebar {user} />
	<Sidebar.Inset>
		<header class="flex h-16 shrink-0 items-center gap-4 border-b px-4">
			<div class="flex items-center gap-2">
				<Sidebar.Trigger class="-ml-1" />
				<Separator orientation="vertical" class="mr-2 h-4" />
			</div>
			<div class="max-w-[260px] flex-1">
				<Input
					placeholder="Busque em todo o sistema"
					value={headerSearchValue}
					oninput={handleHeaderSearchInput}
				/>
			</div>
			<div class="ml-auto flex items-center gap-3">
				<UnidadeSelector unidades={unidadesAtivas(user.unidades)} />
				<NotificacaoBell />
			</div>
		</header>
		<main class="flex flex-1 flex-col gap-0.5 px-6 py-4">
			{#if !isOnRoot}
				<DynamicBreadcrumb />
			{/if}
			{@render children?.()}
		</main>
		<AppFooter class="mt-auto" />
	</Sidebar.Inset>
</Sidebar.Provider>
