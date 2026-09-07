<script lang="ts">
	import type { PageData } from './$types';
	import { unidadeAtiva } from '$lib/stores/unidade';
	import { Button } from '$lib/components/ui/button';
	import { situacaoEscala } from '$lib/constants/escalas';
	let { data }: { data: PageData } = $props();
	const unidade = $derived(data.me.unidades?.find((u) => u.id === $unidadeAtiva));
	const podeConfigurar = $derived(['admin', 'colab_proj'].includes(data.me.urole));
	function dataHora(v: string | null) {
		return v
			? new Intl.DateTimeFormat('pt-BR', {
					dateStyle: 'short',
					timeStyle: 'short',
					timeZone: 'America/Sao_Paulo'
				}).format(new Date(v + '-03:00'))
			: 'Não informado';
	}
</script>

<div class="w-full space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<h1 class="text-3xl font-bold">Escalas de Plantão{unidade ? ` — ${unidade.nome}` : ''}</h1>
		{#if podeConfigurar}<Button href="/plantao/configurar-abertura?nova=1">Nova escala</Button>{/if}
	</div>
	<p class="text-muted-foreground">
		O prazo de inscrição define quando escolher seus dias. Após o prazo, a escala continua
		disponível para consulta e conferência de presença.
	</p>
	<div class="overflow-x-auto rounded-lg border">
		<table class="w-full text-left text-sm">
			<thead class="bg-muted"
				><tr
					><th class="p-4">Escala</th><th class="p-4">Inscrições (Brasília)</th><th class="p-4"
						>Dias de plantão</th
					><th class="p-4">Situação</th><th class="p-4">Ações</th></tr
				></thead
			>
			<tbody>
				{#each data.escalas as escala (escala.id)}
					<tr class="border-t">
						<td class="p-4 font-medium">{escala.nome}</td>
						<td class="p-4"
							>{dataHora(escala.data_abertura)}<br />até {dataHora(escala.data_fechamento)}</td
						>
						<td class="max-w-sm p-4"
							>{escala.dias.length} dia(s){#if escala.dias.length}<br />{escala.dias[0]
									.split('-')
									.reverse()
									.join('/')} a {escala.dias.at(-1)?.split('-').reverse().join('/')}{/if}</td
						>
						<td class="p-4">{situacaoEscala[escala.situacao]}</td>
						<td class="p-4"
							><Button variant="outline" href={`/plantao/escala?escala_id=${escala.id}`}
								>Abrir escala</Button
							></td
						>
					</tr>
				{:else}<tr
						><td colspan="5" class="p-8 text-center">Nenhuma escala cadastrada nesta unidade.</td
						></tr
					>{/each}
			</tbody>
		</table>
	</div>
</div>
