<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Input } from '$lib/components/ui/input';
	import { untrack } from 'svelte';
	import type { Atendido } from '$lib/types';
	import type { Snippet } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import * as Form from '$lib/components/ui/form';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';
	import { api } from '$lib/api-client';
	import { ApiException } from '$lib/types';

	let {
		selectedIds = $bindable([]),
		onSelect,
		trigger,
		form,
		name,
		apiEndpoint,
		dialogTitle,
		dialogDescription,
		buttonText = 'Selecionar',
		emptyStateText,
		searchPlaceholder,
		multiSelect = true,
		initialSelectedItems = []
	}: {
		selectedIds?: number[];
		onSelect?: (items: Atendido[]) => void;
		trigger?: Snippet;
		form?: FieldProps<T, U>['form'];
		name?: U;
		apiEndpoint: string;
		dialogTitle: string;
		dialogDescription: string;
		buttonText?: string;
		emptyStateText: string;
		searchPlaceholder: string;
		multiSelect?: boolean;
		initialSelectedItems?: Atendido[];
	} = $props();

	let open = $state(false);
	let search = $state('');
	let items = $state<Atendido[]>([]);
	let loading = $state(false);
	let tempSelectedIds = $state<number[]>([]);
	let selectedItemsData = $state<Atendido[]>([]);

	let page = $state(1);
	let total = $state(0);
	let totalPages = $state(0);
	let failure = $state('');
	let retry = $state(0);
	const perPage = 50;
	let requestVersion = 0;

	async function fetchItems(
		searchTerm: string,
		requestedPage: number,
		signal: AbortSignal,
		version: number
	) {
		try {
			const [path, query = ''] = apiEndpoint.split('?');
			const params = new URLSearchParams(query);
			params.set('search', searchTerm);
			params.set('page', String(requestedPage));
			params.set('per_page', String(perPage));
			const data = await api.get<{ items: Atendido[]; total: number; total_pages: number }>(
				`${path}?${params}`,
				{ signal }
			);
			if (signal.aborted || version !== requestVersion) return;
			items = data.items ?? [];
			total = data.total;
			totalPages = data.total_pages;
			const selected = new Map(selectedItemsData.map((item) => [item.id, item]));
			for (const item of items) {
				if (tempSelectedIds.includes(item.id)) selected.set(item.id, item);
			}
			selectedItemsData = [...selected.values()];
		} catch (err) {
			if (signal.aborted || version !== requestVersion) return;
			failure =
				err instanceof ApiException ? err.message : 'Não foi possível carregar os resultados.';
			items = [];
		} finally {
			if (!signal.aborted && version === requestVersion) loading = false;
		}
	}

	$effect(() => {
		if (!open) return;
		const term = search;
		const currentPage = page;
		retry;
		const controller = new AbortController();
		const version = ++requestVersion;
		loading = true;
		failure = '';
		const timer = setTimeout(() => {
			untrack(() => void fetchItems(term, currentPage, controller.signal, version));
		}, 300);
		return () => {
			clearTimeout(timer);
			controller.abort();
		};
	});

	function toggleItem(item: Atendido) {
		if (multiSelect) {
			if (tempSelectedIds.includes(item.id)) {
				tempSelectedIds = tempSelectedIds.filter((id) => id !== item.id);
				selectedItemsData = selectedItemsData.filter((i) => i.id !== item.id);
			} else {
				tempSelectedIds = [...tempSelectedIds, item.id];
				selectedItemsData = [...selectedItemsData, item];
			}
		} else {
			tempSelectedIds = [item.id];
			selectedItemsData = [item];
		}
	}

	function confirmSelection() {
		selectedIds = [...new Set(tempSelectedIds)];
		const uniqueItems = selectedItemsData.filter(
			(item, index, self) => index === self.findIndex((t) => t.id === item.id)
		);
		onSelect?.(uniqueItems);
		open = false;
	}

	function handleOpenChange(isOpen: boolean) {
		open = isOpen;
		search = '';
		page = 1;
		total = 0;
		totalPages = 0;
		items = [];
		failure = '';
		if (isOpen) {
			tempSelectedIds = [...new Set(selectedIds)];
			const available = new Map(
				[...selectedItemsData, ...initialSelectedItems].map((item) => [item.id, item])
			);
			selectedItemsData = tempSelectedIds.flatMap((id) =>
				available.has(id) ? [available.get(id)!] : []
			);
		}
	}
</script>

{#if form && name}
	<Form.Field {form} {name}>
		<Form.Control>
			{#snippet children({ props })}
				<input type="hidden" {...props} bind:value={selectedIds} />
			{/snippet}
		</Form.Control>
	</Form.Field>
{/if}

<Button
	type="button"
	variant="outline"
	class="w-full sm:w-auto"
	onclick={() => handleOpenChange(true)}
>
	{#if trigger}
		{@render trigger()}
	{:else}
		{buttonText}
	{/if}
</Button>

<Dialog.Root bind:open onOpenChange={handleOpenChange}>
	<Dialog.Content class="flex max-h-[85vh] flex-col sm:max-w-3xl">
		<Dialog.Header>
			<Dialog.Title>{dialogTitle}</Dialog.Title>
			<Dialog.Description>{dialogDescription}</Dialog.Description>
		</Dialog.Header>

		<div class="flex flex-1 flex-col space-y-4 overflow-hidden py-4">
			<div class="relative">
				<Search class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				<Input
					type="text"
					placeholder={searchPlaceholder}
					aria-label={searchPlaceholder}
					bind:value={search}
					oninput={() => {
						page = 1;
					}}
					class="h-12 w-full pr-4 pl-10 text-base md:text-base"
				/>
			</div>

			<div class="min-h-[300px] flex-1 overflow-y-auto rounded-md border p-4">
				{#if loading}
					<div class="py-8 text-center text-muted-foreground">Carregando...</div>
				{:else if failure}
					<div role="alert" class="space-y-2 py-8 text-center">
						<p>{failure}</p>
						<Button type="button" variant="outline" onclick={() => retry++}>Tentar novamente</Button
						>
					</div>
				{:else if items.length === 0}
					<div class="py-8 text-center text-muted-foreground">{emptyStateText}</div>
				{:else}
					<div class="space-y-2">
						{#each items as item (item.id)}
							<label
								class="flex cursor-pointer items-center space-x-3 rounded-lg p-3 transition-colors hover:bg-accent"
							>
								{#if multiSelect}
									<input
										type="checkbox"
										checked={tempSelectedIds.includes(item.id)}
										onchange={() => toggleItem(item)}
										class="h-4 w-4 rounded border-gray-300"
									/>
								{:else}
									<input
										type="radio"
										name="item-selector"
										checked={tempSelectedIds.includes(item.id)}
										onchange={() => toggleItem(item)}
										class="h-4 w-4"
									/>
								{/if}
								<div class="min-w-0 flex-1">
									<p class="truncate text-sm font-medium">{item.nome}</p>
									<div class="flex gap-4 text-xs text-muted-foreground">
										{#if item.cpf}
											<span>CPF: {item.cpf}</span>
										{/if}
										{#if item.email}
											<span>{item.email}</span>
										{/if}
									</div>
								</div>
							</label>
						{/each}
					</div>
				{/if}
			</div>

			<div class="flex flex-shrink-0 items-center justify-between text-sm text-muted-foreground">
				<span>
					{#if multiSelect}
						{tempSelectedIds.length} selecionado(s)
					{:else}
						{tempSelectedIds.length > 0 ? '1 selecionado' : 'Nenhum selecionado'}
					{/if}
				</span>
			</div>
			<div
				class="flex flex-wrap items-center justify-between gap-2"
				aria-label="Paginação dos resultados"
			>
				<span aria-live="polite" class="text-sm text-muted-foreground">
					{#if !loading && !failure}{total} resultado(s) · Página {page} de {Math.max(
							1,
							totalPages
						)}{/if}
				</span>
				<div class="flex gap-2">
					<Button
						type="button"
						variant="outline"
						disabled={loading || !!failure || page <= 1}
						onclick={() => page--}>Anterior</Button
					>
					<Button
						type="button"
						variant="outline"
						disabled={loading || !!failure || page >= totalPages}
						onclick={() => page++}>Próxima</Button
					>
				</div>
			</div>
		</div>

		<Dialog.Footer class="flex-shrink-0">
			<Button type="button" variant="outline" onclick={() => (open = false)}>Cancelar</Button>
			<Button type="button" disabled={loading || !!failure} onclick={confirmSelection}
				>Confirmar Seleção</Button
			>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
