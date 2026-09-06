<script lang="ts">
	import * as Select from '$lib/components/ui/select';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { definirUnidadeAtiva, unidadeAtiva } from '$lib/stores/unidade';
	import type { Unidade } from '$lib/types';

	let { unidades = [] }: { unidades?: Unidade[] } = $props();
	let trocando = $state(false);

	const selecionada = $derived(
		unidades.find((unidade) => unidade.id === $unidadeAtiva) ?? unidades[0]
	);

	async function trocar(valor: string) {
		const id = Number(valor);
		if (trocando || !unidades.some((unidade) => unidade.id === id) || id === $unidadeAtiva) return;

		trocando = true;
		try {
			definirUnidadeAtiva(id);
			if (/^\/casos\/\d+(?:\/|$)/.test(page.url.pathname)) {
				// Sai também das telas de edição, eventos e processos. Invalidar
				// antes de sair tentaria buscar o caso antigo na nova unidade.
				await goto('/casos', { invalidateAll: true });
			} else {
				await invalidateAll();
			}
		} finally {
			trocando = false;
		}
	}
</script>

{#if unidades.length > 1}
	<Select.Root
		type="single"
		value={String($unidadeAtiva ?? '')}
		onValueChange={trocar}
		name="unidade"
		disabled={trocando}
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
