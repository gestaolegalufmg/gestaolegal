<script lang="ts">
	import { api, apiFetch } from '$lib/api-client';
	import type { ArquivoEvento } from '$lib/types/evento';
	import { Button } from '$lib/components/ui/button';
	import ConfirmAction from '$lib/components/confirm-action.svelte';
	import { toast } from 'svelte-sonner';
	import { mensagemDeErro } from '$lib/utils/erros';

	let { casoId, eventoId, arquivos, podeExcluir = false }: {
		casoId: number; eventoId: number; arquivos: ArquivoEvento[]; podeExcluir?: boolean;
	} = $props();
	let removidos = $state<number[]>([]);
	const visiveis = $derived(arquivos.filter((a) => !removidos.includes(a.id)));
	const rota = $derived(`caso/${casoId}/eventos/${eventoId}/arquivos`);

	async function baixar(arquivo: ArquivoEvento) {
		try {
			const response = await apiFetch(`${rota}/${arquivo.id}/download`);
			if (!response.ok) throw new Error('Não foi possível baixar o anexo');
			const url = URL.createObjectURL(await response.blob());
			const link = document.createElement('a');
			link.href = url;
			link.download = arquivo.nome;
			link.click();
			URL.revokeObjectURL(url);
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao baixar anexo'));
		}
	}

	async function excluir(arquivo: ArquivoEvento) {
		try {
			await api.delete(`${rota}/${arquivo.id}`);
			removidos = [...removidos, arquivo.id];
			toast.success('Anexo excluído');
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao excluir anexo'));
		}
	}
</script>

<div class="space-y-3">
	{#each visiveis as arquivo (arquivo.id)}
		<div class="flex items-center justify-between gap-3 rounded-lg bg-muted/50 p-3">
			<div class="min-w-0 break-all text-sm">
				<span>{arquivo.nome}</span>
				{#if arquivo.indisponivel_origem}
					<p class="text-muted-foreground">Arquivo indisponível no acervo original</p>
				{/if}
			</div>
			<div class="flex shrink-0 gap-2">
				<Button type="button" variant="outline" size="sm" disabled={arquivo.indisponivel_origem} onclick={() => baixar(arquivo)}>Baixar</Button>
				{#if podeExcluir}
					<ConfirmAction title="Excluir anexo?" description={`O arquivo ${arquivo.nome} será removido deste evento.`}
						confirmText="Excluir" onConfirm={() => excluir(arquivo)}>
						{#snippet trigger()}Excluir{/snippet}
					</ConfirmAction>
				{/if}
			</div>
		</div>
	{:else}
		<p class="text-sm text-muted-foreground">Nenhum anexo.</p>
	{/each}
</div>
