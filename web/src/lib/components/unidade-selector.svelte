<script lang="ts">
	import * as Select from '$lib/components/ui/select';
	import { invalidateAll } from '$app/navigation';
	import { definirUnidadeAtiva, unidadeAtiva } from '$lib/stores/unidade';
	import type { Unidade } from '$lib/types';

	let { unidades = [] }: { unidades?: Unidade[] } = $props();

	const selecionada = $derived(
		unidades.find((unidade) => unidade.id === $unidadeAtiva) ?? unidades[0]
	);

	async function trocar(valor: string) {
		const id = Number(valor);
		if (!Number.isInteger(id) || id === $unidadeAtiva) return;

		definirUnidadeAtiva(id);
		// Sem invalidar, as listagens carregadas na unidade anterior continuam
		// na tela como se fossem da nova.
		await invalidateAll();
	}
</script>

{#if unidades.length > 1}
	<Select.Root
		type="single"
		value={String($unidadeAtiva ?? '')}
		onValueChange={trocar}
		name="unidade"
	>
		<Select.Trigger class="w-[140px]" aria-label="Unidade ativa">
			{selecionada?.sigla ?? 'Unidade'}
		</Select.Trigger>
		<Select.Content>
			{#each unidades as unidade (unidade.id)}
				<Select.Item value={String(unidade.id)}>{unidade.nome}</Select.Item>
			{/each}
		</Select.Content>
	</Select.Root>
{:else if unidades.length === 1}
	<span class="text-sm font-medium text-muted-foreground" title={unidades[0].nome}>
		{unidades[0].sigla}
	</span>
{/if}
