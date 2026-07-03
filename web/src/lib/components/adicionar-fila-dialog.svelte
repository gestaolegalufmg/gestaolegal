<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import Search from '@lucide/svelte/icons/search';
	import { Debounced } from 'runed';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { TIPOS_FILA } from '$lib/types';
	import type { Paginated, ListAtendido } from '$lib/types';

	let {
		open = $bindable(false),
		onSuccess
	}: {
		open?: boolean;
		onSuccess?: () => void | Promise<void>;
	} = $props();

	let search = $state('');
	let atendidos = $state<ListAtendido[]>([]);
	let loading = $state(false);
	let selectedId = $state<number | null>(null);
	let tipo = $state<string>(TIPOS_FILA[0]);
	let prioridade = $state(false);
	let submitting = $state(false);

	const debouncedSearch = new Debounced(() => search, 300);

	async function fetchAtendidos(term: string) {
		loading = true;
		try {
			const data = await api.get<Paginated<ListAtendido>>(
				`atendido?search=${encodeURIComponent(term)}&per_page=50`
			);
			atendidos = data.items ?? [];
		} catch {
			toast.error('Erro ao carregar atendidos');
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (open) {
			fetchAtendidos(debouncedSearch.current);
		}
	});

	$effect(() => {
		if (open) {
			// reset when opening
			selectedId = null;
			tipo = TIPOS_FILA[0];
			prioridade = false;
			search = '';
		}
	});

	async function handleSubmit() {
		if (!selectedId) {
			toast.error('Selecione um atendido');
			return;
		}
		submitting = true;
		try {
			await api.post('fila_atendimento', {
				id_atendido: selectedId,
				tipo,
				prioridade: prioridade ? 1 : 0
			});
			toast.success('Adicionado à fila com sucesso!');
			open = false;
			await onSuccess?.();
		} catch {
			toast.error('Erro ao adicionar à fila');
		} finally {
			submitting = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="flex max-h-[85vh] max-w-lg flex-col">
		<Dialog.Header>
			<Dialog.Title>Adicionar à Fila</Dialog.Title>
			<Dialog.Description>
				Selecione um atendido e o tipo de atendimento para adicioná-lo à fila.
			</Dialog.Description>
		</Dialog.Header>

		<div class="flex flex-1 flex-col space-y-4 overflow-hidden py-2">
			<div class="relative">
				<Search class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				<Input
					type="text"
					placeholder="Buscar atendido por nome, CPF..."
					bind:value={search}
					class="pl-10"
				/>
			</div>

			<div class="min-h-[180px] flex-1 overflow-y-auto rounded-md border p-2">
				{#if loading}
					<div class="py-8 text-center text-muted-foreground">Carregando...</div>
				{:else if atendidos.length === 0}
					<div class="py-8 text-center text-muted-foreground">Nenhum atendido encontrado</div>
				{:else}
					<div class="space-y-1">
						{#each atendidos as atendido (atendido.id)}
							<label
								class="flex cursor-pointer items-center space-x-3 rounded-lg p-2 transition-colors hover:bg-accent"
							>
								<input
									type="radio"
									name="fila-atendido"
									checked={selectedId === atendido.id}
									onchange={() => (selectedId = atendido.id)}
									class="h-4 w-4"
								/>
								<div class="min-w-0 flex-1">
									<p class="truncate text-sm font-medium">{atendido.nome}</p>
									{#if atendido.cpf}
										<p class="text-xs text-muted-foreground">CPF: {atendido.cpf}</p>
									{/if}
								</div>
							</label>
						{/each}
					</div>
				{/if}
			</div>

			<div class="space-y-2">
				<Label>Tipo de atendimento</Label>
				<Select.Root type="single" bind:value={tipo}>
					<Select.Trigger class="w-full">{tipo}</Select.Trigger>
					<Select.Content>
						{#each TIPOS_FILA as t (t)}
							<Select.Item value={t}>{t}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<label class="flex cursor-pointer items-center gap-2">
				<Checkbox bind:checked={prioridade} />
				<span class="text-sm">Atendimento prioritário</span>
			</label>
		</div>

		<Dialog.Footer class="flex-shrink-0">
			<Button variant="outline" onclick={() => (open = false)}>Cancelar</Button>
			<Button onclick={handleSubmit} disabled={submitting || !selectedId}>
				{submitting ? 'Adicionando...' : 'Adicionar à Fila'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
