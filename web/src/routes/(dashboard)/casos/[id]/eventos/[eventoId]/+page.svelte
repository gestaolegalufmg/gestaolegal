<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import InfoCard from '$lib/components/ui/info-card.svelte';
	import type { PageProps } from './$types';
	import Edit from '@lucide/svelte/icons/edit';
	import Download from '@lucide/svelte/icons/download';
	import FileText from '@lucide/svelte/icons/file-text';
	import { TIPO_EVENTO } from '$lib/constants/tipo_evento';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';

	let { data }: PageProps = $props();
	const { evento, caso } = data;

	function formatDateTime(dateString: string) {
		const date = new Date(dateString);
		return date.toLocaleString('pt-BR');
	}

	function formatDate(dateString: string) {
		const date = new Date(dateString);
		return date.toLocaleDateString('pt-BR');
	}

	function getTipoLabel(tipo: string) {
		const tipoMap: Record<string, string> = {
			[TIPO_EVENTO.AUDIENCIA]: 'Audiência',
			[TIPO_EVENTO.CONCILIACAO]: 'Conciliação',
			[TIPO_EVENTO.DECISAO_JUDICIAL]: 'Decisão Judicial',
			[TIPO_EVENTO.REDISTRIBUICAO_DO_CASO]: 'Redistribuição do Caso',
			[TIPO_EVENTO.ENCERRAMENTO_DO_CASO]: 'Encerramento do Caso',
			[TIPO_EVENTO.DOCUMENTOS]: 'Documentos',
			[TIPO_EVENTO.PROTOCOLO_DE_PETICAO]: 'Protocolo de Petição',
			[TIPO_EVENTO.DILIGENCIA_EXTERNA]: 'Diligência Externa',
			[TIPO_EVENTO.CONTATO]: 'Contato',
			[TIPO_EVENTO.REUNIAO]: 'Reunião',
			[TIPO_EVENTO.OUTROS]: 'Outros'
		};
		return tipoMap[tipo] || tipo;
	}

	const eventoInfoData = [
		{ label: 'ID', value: evento.id.toString() },
		{ label: 'Número do Evento', value: evento.num_evento?.toString() || '--' },
		{ label: 'Tipo', value: getTipoLabel(evento.tipo) },
		{ label: 'Data do Evento', value: evento.data_evento, formatter: formatDate },
		{ label: 'Responsável', value: evento.usuario_responsavel?.nome || '--' },
		{ label: 'Status', value: evento.status ? 'Ativo' : 'Inativo' }
	];

	const auditInfoData = [
		{ label: 'Criado Por', value: evento.criado_por?.nome || '--' },
		{ label: 'Data de Criação', value: evento.data_criacao, formatter: formatDateTime }
	];

	async function handleDownload() {
		if (!evento.arquivo) return;

		const response = await api.get(`caso/${caso.id}/eventos/${evento.id}/download`);
		if (!response.ok) {
			toast.error('Erro ao baixar arquivo');
			return;
		}

		const blob = await response.blob();
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = evento.arquivo.split('/').pop() || 'arquivo';
		document.body.appendChild(a);
		a.click();
		window.URL.revokeObjectURL(url);
		document.body.removeChild(a);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">
				Evento #{evento.num_evento || evento.id}
			</h1>
			<p class="text-muted-foreground">
				<a href="/casos/{caso.id}" class="hover:underline">Caso #{caso.id}</a>
				/ {getTipoLabel(evento.tipo)}
			</p>
		</div>
		<div class="flex gap-2">
			<Button variant="outline" href="/casos/{caso.id}">Voltar</Button>
			{#if evento.arquivo}
				<Button variant="outline" onclick={handleDownload}>
					<Download class="mr-2 h-4 w-4" />
					Download
				</Button>
			{/if}
			<Button href="/casos/{caso.id}/eventos/{evento.id}/editar">
				<Edit class="mr-2 h-4 w-4" />
				Editar
			</Button>
		</div>
	</div>

	<div class="grid gap-6 md:grid-cols-2">
		<InfoCard title="Informações do Evento" items={eventoInfoData} />
		<InfoCard title="Informações de Auditoria" items={auditInfoData} />

		{#if evento.descricao}
			<Card.Root class="md:col-span-2">
				<Card.Header>
					<Card.Title>Descrição</Card.Title>
				</Card.Header>
				<Card.Content>
					<p class="text-sm whitespace-pre-wrap">{evento.descricao}</p>
				</Card.Content>
			</Card.Root>
		{/if}

		{#if evento.arquivo}
			<Card.Root>
				<Card.Header>
					<Card.Title>Arquivo Anexado</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
						<div class="flex items-center gap-2">
							<FileText class="h-5 w-5" />
							<span class="text-sm">{evento.arquivo.split('/').pop()}</span>
						</div>
						<Button variant="ghost" size="sm" onclick={handleDownload}>
							<Download class="h-4 w-4" />
						</Button>
					</div>
				</Card.Content>
			</Card.Root>
		{/if}
	</div>
</div>
