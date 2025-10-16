<script lang="ts">
	import AppSidebar from '$lib/components/app-sidebar.svelte';
	import DynamicBreadcrumb from '$lib/components/dynamic-breadcrumb.svelte';
	import GlobalSearchDialog from '$lib/components/global-search-dialog.svelte';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { page } from '$app/state';
	import Input from '$lib/components/ui/input/input.svelte';
	import { Toaster } from 'svelte-sonner';
	import { onMount } from 'svelte';

	let { children, data } = $props();

	const isOnRoot = $derived(page.url.pathname === '/');

	let user = data.me;
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

<Toaster position="top-center" richColors />
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
					placeholder="Busque em todo o sistema (⌘K)"
					value={headerSearchValue}
					oninput={handleHeaderSearchInput}
				/>
			</div>
		</header>
		<main class="flex flex-1 flex-col gap-0.5 px-6 py-4">
			{#if !isOnRoot}
				<DynamicBreadcrumb />
			{/if}
			{@render children?.()}
		</main>
	</Sidebar.Inset>
</Sidebar.Provider>
