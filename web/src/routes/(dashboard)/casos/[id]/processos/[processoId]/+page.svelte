<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import InfoCard from '$lib/components/ui/info-card.svelte';
	import type { PageProps } from './$types';
	import Edit from '@lucide/svelte/icons/edit';
	import { Badge } from '$lib/components/ui/badge';

	let { data }: PageProps = $props();
	const { processo } = data;

	function formatDate(dateString?: string | null): string {
		if (!dateString) return 'Não informado';
		const date = new Date(dateString);
		return date.toLocaleDateString('pt-BR');
	}

	function formatCurrency(value?: number | null): string {
		if (value === null || value === undefined) return 'R$ 0,00';
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'BRL'
		}).format(value);
	}

	const especieLabels: Record<string, string> = {
		civel: 'Cível',
		trabalhista: 'Trabalhista',
		criminal: 'Criminal',
		administrativo: 'Administrativo',
		tributario: 'Tributário'
	};

	const probabilidadeLabels: Record<string, string> = {
		provavel: 'Provável',
		possivel: 'Possível',
		remota: 'Remota'
	};

	const posicaoLabels: Record<string, string> = {
		autor: 'Autor',
		reu: 'Réu',
		terceiro: 'Terceiro Interessado'
	};

	const processInfoData = [
		{ label: 'Espécie', value: especieLabels[processo.especie] || processo.especie },
		...(processo.numero
			? [{ label: 'Número do Processo', value: processo.numero.toString() }]
			: []),
		...(processo.identificacao ? [{ label: 'Identificação', value: processo.identificacao }] : []),
		...(processo.vara ? [{ label: 'Vara', value: processo.vara }] : []),
		{
			label: 'Probabilidade',
			value: processo.probabilidade
				? probabilidadeLabels[processo.probabilidade] || processo.probabilidade
				: 'Não informada'
		},
		{
			label: 'Posição do Assistido',
			value: processo.posicao_assistido
				? posicaoLabels[processo.posicao_assistido] || processo.posicao_assistido
				: 'Não informada'
		},
		{ label: 'Status', value: processo.status ? 'Ativo' : 'Inativo' }
	];

	const financialData = [
		{
			label: 'Valor da Causa Inicial',
			value: formatCurrency(processo.valor_causa_inicial)
		},
		{
			label: 'Valor da Causa Atual',
			value: formatCurrency(processo.valor_causa_atual)
		}
	];

	const datesData = [
		{
			label: 'Data de Distribuição',
			value: formatDate(processo.data_distribuicao)
		},
		{
			label: 'Data de Trânsito em Julgado',
			value: formatDate(processo.data_transito_em_julgado)
		}
	];
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<div class="flex items-center gap-3">
				<h1 class="text-3xl font-bold tracking-tight">
					{processo.identificacao || `Processo Nº ${processo.numero}`}
				</h1>
				<Badge variant={processo.status ? 'default' : 'secondary'}>
					{processo.status ? 'Ativo' : 'Inativo'}
				</Badge>
			</div>
			<p class="text-muted-foreground">
				{especieLabels[processo.especie] || processo.especie}
				-
				<a
					href={processo.link}
					target="_blank"
					rel="noopener noreferrer"
					class="break-all text-primary hover:underline"
				>
					{processo.link}
				</a>
			</p>
		</div>
		<div class="flex gap-2">
			<Button variant="outline" href="/casos/{processo.id_caso}">Voltar</Button>
			<Button href="/casos/{processo.id_caso}/processos/{processo.id}/editar">
				<Edit class="mr-2 h-4 w-4" />
				Editar
			</Button>
		</div>
	</div>

	<div class="grid gap-6 md:grid-cols-2">
		<InfoCard title="Informações do Processo" items={processInfoData} />
		<InfoCard title="Valores" items={financialData} />
		<InfoCard title="Datas Importantes" items={datesData} />

		{#if processo.obs}
			<Card.Root class="md:col-span-2">
				<Card.Header>
					<Card.Title>Observações</Card.Title>
				</Card.Header>
				<Card.Content>
					<p class="text-sm whitespace-pre-wrap">{processo.obs}</p>
				</Card.Content>
			</Card.Root>
		{/if}
	</div>

	{#if processo.criado_por}
		<Card.Root>
			<Card.Header>
				<Card.Title>Informações de Auditoria</Card.Title>
			</Card.Header>
			<Card.Content class="grid gap-4 md:grid-cols-2">
				<div>
					<p class="text-sm text-muted-foreground">Criado Por</p>
					<p class="font-medium">{processo.criado_por.nome}</p>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}
</div>
