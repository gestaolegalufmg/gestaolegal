<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Badge } from '$lib/components/ui/badge';
	import Send from '@lucide/svelte/icons/send';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import type { ListAssistenciaJudiciaria, Paginated } from '$lib/types';

	let {
		orientacaoId,
		onEncaminhado
	}: {
		orientacaoId: number;
		onEncaminhado?: () => void | Promise<void>;
	} = $props();

	let open = $state(false);
	let search = $state('');
	let items = $state<ListAssistenciaJudiciaria[]>([]);
	let selectedId = $state<number | null>(null);
	let loading = $state(false);
	let submitting = $state(false);

	const areaLabels: Record<string, string> = {
		administrativo: 'Administrativo',
		ambiental: 'Ambiental',
		civel: 'Cível',
		empresarial: 'Empresarial',
		penal: 'Penal',
		trabalhista: 'Trabalhista'
	};

	async function fetchList() {
		loading = true;
		try {
			const params = new URLSearchParams({ per_page: '50' });
			if (search) params.set('search', search);
			const data = await api.get<Paginated<ListAssistenciaJudiciaria>>(
				`assistencia_judiciaria?${params.toString()}`
			);
			items = data.items;
		} catch {
			toast.error('Erro ao carregar assistências judiciárias');
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (open) {
			fetchList();
		}
	});

	async function handleConfirm() {
		if (!selectedId) return;
		submitting = true;
		try {
			await api.post(`assistencia_judiciaria/${selectedId}/encaminhar`, {
				id_orientacao: orientacaoId
			});
			toast.success('Orientação encaminhada com sucesso!');
			open = false;
			selectedId = null;
			search = '';
			await onEncaminhado?.();
		} catch {
			toast.error('Erro ao encaminhar orientação');
		} finally {
			submitting = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger class="inline-flex">
		<Button variant="default" size="sm">
			<Send class="mr-2 h-4 w-4" />
			Encaminhar
		</Button>
	</Dialog.Trigger>
	<Dialog.Content class="max-w-lg">
		<Dialog.Header>
			<Dialog.Title>Encaminhar para Assistência Judiciária</Dialog.Title>
			<Dialog.Description>
				Selecione a assistência judiciária para a qual deseja encaminhar esta orientação.
			</Dialog.Description>
		</Dialog.Header>

		<div class="space-y-3">
			<Input
				bind:value={search}
				placeholder="Buscar assistência..."
				ondebounceinput={fetchList}
				debounceMs={400}
			/>

			<div class="max-h-72 space-y-2 overflow-y-auto">
				{#if loading}
					<p class="py-4 text-center text-sm text-muted-foreground">Carregando...</p>
				{:else if items.length === 0}
					<p class="py-4 text-center text-sm text-muted-foreground">
						Nenhuma assistência judiciária encontrada
					</p>
				{:else}
					{#each items as item (item.id)}
						<button
							type="button"
							class="w-full rounded-md border p-3 text-left transition-colors hover:bg-muted {selectedId ===
							item.id
								? 'border-primary bg-muted'
								: ''}"
							onclick={() => (selectedId = item.id)}
						>
							<div class="flex items-center justify-between">
								<span class="font-medium">{item.nome}</span>
								{#if item.cidade}
									<span class="text-xs text-muted-foreground">{item.cidade}</span>
								{/if}
							</div>
							<div class="mt-1 flex flex-wrap gap-1">
								{#each item.areas_atendidas as area}
									<Badge variant="secondary" class="text-xs">{areaLabels[area] || area}</Badge>
								{/each}
							</div>
						</button>
					{/each}
				{/if}
			</div>
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>Cancelar</Button>
			<Button onclick={handleConfirm} disabled={!selectedId || submitting}>
				{submitting ? 'Encaminhando...' : 'Encaminhar'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
