<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Input } from '$lib/components/ui/input';
	import { Debounced } from 'runed';
	import type { Atendido } from '$lib/types';
	import type { Snippet } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import * as Form from '$lib/components/ui/form';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';
	import { apiFetch } from '$lib/api-client';

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
		multiSelect = true
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
	} = $props();

	let open = $state(false);
	let search = $state('');
	let items = $state<Atendido[]>([]);
	let loading = $state(false);
	let tempSelectedIds = $state<number[]>([]);
	let selectedItemsData = $state<Atendido[]>([]);

	const debouncedSearch = new Debounced(() => search, 300);

	async function fetchItems(searchTerm: string = '') {
		loading = true;
		try {
			const response = await apiFetch(
				`${apiEndpoint}?search=${encodeURIComponent(searchTerm)}&per_page=50`
			);
			if (response.ok) {
				const data = await response.json();
				items = data.items || [];
				syncSelectedItemsData();
			}
		} catch (error) {
			console.error('Error fetching items:', error);
		} finally {
			loading = false;
		}
	}

	function syncSelectedItemsData() {
		const newlyFetchedSelected = items.filter((item) => tempSelectedIds.includes(item.id));
		const existingSelectedNotInResults = selectedItemsData.filter(
			(item) =>
				tempSelectedIds.includes(item.id) && !items.some((fetched) => fetched.id === item.id)
		);
		selectedItemsData = [...existingSelectedNotInResults, ...newlyFetchedSelected];
	}

	$effect(() => {
		if (open) {
			tempSelectedIds = [...new Set(selectedIds)];
			items = [];
			search = '';
		}
	});

	$effect(() => {
		if (!open) return;

		const searchTerm = debouncedSearch.current;
		fetchItems(searchTerm);
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
		if (!isOpen) {
			search = '';
			items = [];
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

<Button type="button" variant="outline" class="w-full sm:w-auto" onclick={() => (open = true)}>
	{#if trigger}
		{@render trigger()}
	{:else}
		{buttonText}
	{/if}
</Button>

<Dialog.Root bind:open onOpenChange={handleOpenChange}>
	<Dialog.Content class="flex max-h-[85vh] max-w-3xl flex-col">
		<Dialog.Header>
			<Dialog.Title>{dialogTitle}</Dialog.Title>
			<Dialog.Description>{dialogDescription}</Dialog.Description>
		</Dialog.Header>

		<div class="flex flex-1 flex-col space-y-4 overflow-hidden py-4">
			<div class="relative">
				<Search class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				<Input type="text" placeholder={searchPlaceholder} bind:value={search} class="pl-10" />
			</div>

			<div class="min-h-[300px] flex-1 overflow-y-auto rounded-md border p-4">
				{#if loading}
					<div class="py-8 text-center text-muted-foreground">Carregando...</div>
				{:else if items.length === 0}
					<div class="py-8 text-center text-muted-foreground">{emptyStateText}</div>
				{:else}
					<div class="space-y-2">
						{#each items as item, index (`${item.id}-${index}`)}
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
		</div>

		<Dialog.Footer class="flex-shrink-0">
			<Button type="button" variant="outline" onclick={() => (open = false)}>Cancelar</Button>
			<Button type="button" onclick={confirmSelection}>Confirmar Seleção</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
