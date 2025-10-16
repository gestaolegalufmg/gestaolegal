<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Input from '$lib/components/ui/input/input.svelte';
	import { Separator } from '$lib/components/ui/separator/index.js';
	import SearchIcon from '@lucide/svelte/icons/search';
	import LoaderIcon from '@lucide/svelte/icons/loader';
	import { goto } from '$app/navigation';
	import type { SearchResponse, SearchResultItem } from '$lib/types/search';
	import { Debounced } from 'runed';
	import { getEntityIcon, getEntityLabel } from '$lib/constants';
	import { apiFetch } from '$lib/api-client';

	let { open = $bindable(false), initialQuery = $bindable('') } = $props();

	let searchQuery = $state('');
	let isSearching = $state(false);
	let searchResults = $state<SearchResultItem[]>([]);
	let selectedIndex = $state(0);

	const debouncedQuery = new Debounced(() => searchQuery, 300);

	$effect(() => {
		if (open && initialQuery) {
			searchQuery = initialQuery;
		}
	});

	async function performSearch(query: string) {
		if (!query || query.trim().length < 2) {
			searchResults = [];
			return;
		}

		isSearching = true;
		try {
			const response = await apiFetch(`search?q=${encodeURIComponent(query)}`);
			const data: SearchResponse = await response.json();

			const items: SearchResultItem[] = [];

			data.results.atendidos.items.forEach((item: any) => {
				items.push({
					id: item.id,
					title: item.nome,
					subtitle: item.cpf || item.email,
					type: 'atendido',
					url: `/plantao/atendidos-assistidos/${item.id}`
				});
			});

			data.results.casos.items.forEach((item: any) => {
				items.push({
					id: item.id,
					title: `Caso #${item.id} - ${item.area_direito}`,
					subtitle: item.descricao?.substring(0, 60),
					type: 'caso',
					url: `/casos/${item.id}`
				});
			});

			data.results.orientacoes_juridicas.items.forEach((item: any) => {
				items.push({
					id: item.id,
					title: `Orientação Jurídica - ${item.area_direito}`,
					subtitle: item.descricao?.substring(0, 60),
					type: 'orientacao_juridica',
					url: `/plantao/orientacoes-juridicas/${item.id}`
				});
			});

			data.results.usuarios.items.forEach((item: any) => {
				items.push({
					id: item.id,
					title: item.nome,
					subtitle: `${item.email} - ${item.urole}`,
					type: 'usuario',
					url: `/usuarios/${item.id}`
				});
			});

			searchResults = items;
			selectedIndex = 0;
		} catch (error) {
			console.error('Search error:', error);
			searchResults = [];
		} finally {
			isSearching = false;
		}
	}

	function handleSearchInput(event: Event) {
		const target = event.target as HTMLInputElement;
		searchQuery = target.value;
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			selectedIndex = Math.min(selectedIndex + 1, searchResults.length - 1);
		} else if (event.key === 'ArrowUp') {
			event.preventDefault();
			selectedIndex = Math.max(selectedIndex - 1, 0);
		} else if (event.key === 'Enter' && searchResults[selectedIndex]) {
			event.preventDefault();
			navigateToResult(searchResults[selectedIndex]);
		}
	}

	function navigateToResult(result: SearchResultItem) {
		open = false;
		searchQuery = '';
		searchResults = [];
		goto(result.url);
	}

	$effect(() => {
		if (!open) {
			searchQuery = '';
			searchResults = [];
			selectedIndex = 0;
			initialQuery = '';
		}
	});

	$effect(() => {
		performSearch(debouncedQuery.current);
	});
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-w-2xl gap-0 p-0" showCloseButton={false}>
		<form action="/search" method="GET" class="flex items-center border-b px-4 py-3">
			<SearchIcon class="mr-2 h-4 w-4 shrink-0 opacity-50" />
			<Input
				type="text"
				placeholder="Busque por atendidos, casos, orientações..."
				class="border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
				value={searchQuery}
				oninput={handleSearchInput}
				onkeydown={handleKeyDown}
			/>
			{#if isSearching}
				<LoaderIcon class="ml-2 h-4 w-4 animate-spin opacity-50" />
			{/if}
		</form>

		<div class="max-h-[400px] overflow-y-auto">
			{#if searchResults.length > 0}
				<div class="p-2">
					{#each searchResults as result, index (result.type + result.id)}
						{@const Icon = getEntityIcon(result.type)}
						<button
							type="button"
							class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-accent {selectedIndex ===
							index
								? 'bg-accent'
								: ''}"
							onclick={() => navigateToResult(result)}
							onmouseenter={() => (selectedIndex = index)}
						>
							<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-muted">
								<Icon class="h-5 w-5" />
							</div>
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-2">
									<p class="truncate text-sm font-medium">{result.title}</p>
									<span
										class="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
									>
										{getEntityLabel(result.type)}
									</span>
								</div>
								{#if result.subtitle}
									<p class="mt-0.5 truncate text-xs text-muted-foreground">
										{result.subtitle}
									</p>
								{/if}
							</div>
						</button>
					{/each}
				</div>
			{:else if searchQuery && !isSearching}
				<div class="p-8 text-center">
					<p class="text-sm text-muted-foreground">Nenhum resultado encontrado</p>
				</div>
			{:else if !searchQuery}
				<div class="p-8 text-center">
					<p class="text-sm text-muted-foreground">Digite para buscar em todo o sistema</p>
				</div>
			{/if}
		</div>

		<Separator />

		<div class="flex items-center justify-between px-4 py-2 text-xs text-muted-foreground">
			<span>Use ↑ ↓ para navegar</span>
			<span>Enter para abrir</span>
			<span>Esc para fechar</span>
		</div>
	</Dialog.Content>
</Dialog.Root>
