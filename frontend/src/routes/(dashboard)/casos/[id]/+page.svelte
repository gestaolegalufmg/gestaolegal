<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import InfoCard from '$lib/components/ui/info-card.svelte';
	import type { PageProps } from './$types';
	import { SITUACAO_DEFERIMENTO_OPTIONS } from '$lib/constants/situacao-deferimento';
	import Edit from '@lucide/svelte/icons/edit';
	import User from '@lucide/svelte/icons/user';
	import { Eye, File, Plus, FileText, Download, Upload, Trash2 } from '@lucide/svelte';
	import DataTable, { type Column } from '$lib/components/data-table.svelte';
	import EventoDialog from '$lib/components/evento-dialog.svelte';
	import type { Evento } from '$lib/types/evento';
	import type { TipoEvento } from '$lib/constants/tipo_evento';
	import { TIPO_EVENTO } from '$lib/constants/tipo_evento';
	import type { BadgeVariant } from '$lib/components/ui/badge';
	import { toast } from 'svelte-sonner';

	let { data }: PageProps = $props();
	const { caso, eventoFormData, eventos: initialEventos } = data;

	let arquivos = $state(caso.arquivos || []);
	let fileInput: HTMLInputElement;
	let isUploading = $state(false);

	function getSituacaoLabel(situacao: string) {
		const option = SITUACAO_DEFERIMENTO_OPTIONS.find((opt) => opt.value === situacao);
		return option?.label || situacao;
	}

	function formatDateTime(dateString: string) {
		const date = new Date(dateString);
		return date.toLocaleString('pt-BR');
	}

	const caseInfoData = [
		{
			label: 'Área do Direito',
			value: caso.area_direito,
			formatter: (v: string) => v.charAt(0).toUpperCase() + v.slice(1)
		},
		...(caso.sub_area ? [{ label: 'Sub-área', value: caso.sub_area }] : []),
		{ label: 'Situação do Deferimento', value: getSituacaoLabel(caso.situacao_deferimento) },
		{ label: 'Status', value: caso.status ? 'Ativo' : 'Inativo' },
		...(caso.justif_indeferimento
			? [{ label: 'Justificativa de Indeferimento', value: caso.justif_indeferimento }]
			: [])
	];

	const responsiblesData = [
		{ label: 'Usuário Responsável', value: caso.usuario_responsavel?.nome || '--' },
		{ label: 'Orientador', value: caso.orientador?.nome || '--' },
		{ label: 'Estagiário', value: caso.estagiario?.nome || '--' },
		{ label: 'Colaborador', value: caso.colaborador?.nome || '--' }
	];

	const auditInfoData = [
		{ label: 'Criado Por', value: caso.criado_por?.nome },
		{ label: 'Data de Criação', value: caso.data_criacao, formatter: formatDateTime },
		...(caso.modificado_por ? [{ label: 'Modificado Por', value: caso.modificado_por.nome }] : []),
		...(caso.data_modificacao
			? [{ label: 'Data de Modificação', value: caso.data_modificacao, formatter: formatDateTime }]
			: [])
	];

	const badges: Record<TipoEvento, { text: string; variant: BadgeVariant }> = {
		[TIPO_EVENTO.AUDIENCIA]: { text: 'Audiência', variant: 'default' },
		[TIPO_EVENTO.CONCILIACAO]: { text: 'Conciliação', variant: 'default' },
		[TIPO_EVENTO.DECISAO_JUDICIAL]: { text: 'Decisão Judicial', variant: 'default' },
		[TIPO_EVENTO.REDISTRIBUICAO_DO_CASO]: { text: 'Redistribuição do Caso', variant: 'default' },
		[TIPO_EVENTO.ENCERRAMENTO_DO_CASO]: { text: 'Encerramento do Caso', variant: 'default' },
		[TIPO_EVENTO.DOCUMENTOS]: { text: 'Documentos', variant: 'default' },
		[TIPO_EVENTO.PROTOCOLO_DE_PETICAO]: { text: 'Protocolo de Petição', variant: 'default' },
		[TIPO_EVENTO.DILIGENCIA_EXTERNA]: { text: 'Diligência Externa', variant: 'default' },
		[TIPO_EVENTO.CONTATO]: { text: 'Contato', variant: 'default' },
		[TIPO_EVENTO.REUNIAO]: { text: 'Reunião', variant: 'default' },
		[TIPO_EVENTO.OUTROS]: { text: 'Outros', variant: 'default' }
	};

	const eventoColumns: Column[] = [
		{ header: 'ID', key: 'id' },
		{ header: 'Número do Evento', key: 'num_evento' },
		{ header: 'Tipo', key: 'tipo', type: 'badge', badgeMap: badges },
		{ header: 'Data do Evento', key: 'data_evento', type: 'date' },
		{ header: 'Responsável', key: 'usuario_responsavel.nome' },
		{
			header: 'Status',
			key: 'status',
			type: 'status'
		}
	];

	const eventoButtons = [
		{ title: 'Ver', icon: Eye, href: (v: Evento) => `/casos/${caso.id}/eventos/${v.id}` }
	];

	let eventoDialogOpen = $state(false);

	let eventos = $state(initialEventos);

	async function refreshEventos() {
		const eventosResponse = await fetch(`/api/caso/${caso.id}/eventos`);

		eventos = await eventosResponse.json();
	}

	async function handleFileUpload() {
		const file = fileInput.files?.[0];
		if (!file) return;

		isUploading = true;
		const formData = new FormData();
		formData.append('arquivo', file);

		try {
			const response = await fetch(`/api/caso/${caso.id}/arquivos`, {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				throw new Error('Erro ao enviar arquivo');
			}

			const newArquivo = await response.json();
			arquivos = [...arquivos, newArquivo];
			toast.success('Arquivo enviado com sucesso');
			fileInput.value = '';
		} catch (error) {
			toast.error('Erro ao enviar arquivo');
			console.error(error);
		} finally {
			isUploading = false;
		}
	}

	async function handleDownload(arquivo: any) {
		try {
			const response = await fetch(`/api/caso/${caso.id}/arquivos/${arquivo.id}/download`);
			if (!response.ok) {
				throw new Error('Erro ao baixar arquivo');
			}

			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = arquivo.link_arquivo.split('/').pop() || 'arquivo';
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		} catch (error) {
			toast.error('Erro ao baixar arquivo');
			console.error(error);
		}
	}

	async function handleDelete(arquivoId: number) {
		if (!confirm('Tem certeza que deseja deletar este arquivo?')) return;

		try {
			const response = await fetch(`/api/caso/${caso.id}/arquivos/${arquivoId}`, {
				method: 'DELETE'
			});

			if (!response.ok) {
				throw new Error('Erro ao deletar arquivo');
			}

			arquivos = arquivos.filter((a) => a.id !== arquivoId);
			toast.success('Arquivo deletado com sucesso');
		} catch (error) {
			toast.error('Erro ao deletar arquivo');
			console.error(error);
		}
	}
</script>

<div class="space-y-6">
	<div class="flex justify-between items-center">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Caso #{caso.id}</h1>
			<p class="text-muted-foreground capitalize">{caso.area_direito}</p>
		</div>
		<div class="flex gap-2">
			<Button variant="outline" href="/casos">Voltar</Button>
			<Button href="/casos/{caso.id}/editar">
				<Edit class="h-4 w-4 mr-2" />
				Editar
			</Button>
		</div>
	</div>

	<div class="grid gap-6 md:grid-cols-2">
		<InfoCard title="Informações do Caso" items={caseInfoData} />
		<InfoCard title="Responsáveis" items={responsiblesData} />

		{#if caso.descricao}
			<Card.Root class="md:col-span-2">
				<Card.Header>
					<Card.Title>Descrição</Card.Title>
				</Card.Header>
				<Card.Content>
					<p class="text-sm">{caso.descricao}</p>
				</Card.Content>
			</Card.Root>
		{/if}

		{#if caso.clientes && caso.clientes.length > 0}
			<Card.Root>
				<Card.Header>
					<Card.Title>Clientes</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="space-y-2">
						{#each caso.clientes as cliente}
							<div class="flex items-center justify-between p-2 rounded-lg bg-muted/50">
								<div class="flex items-center gap-2">
									<User class="h-4 w-4" />
									<span>{cliente.nome}</span>
								</div>
								<Button variant="ghost" size="sm" href="/plantao/atendidos-assistidos/{cliente.id}">
									<Eye class="h-4 w-5" />
								</Button>
							</div>
						{/each}
					</div>
				</Card.Content>
			</Card.Root>
		{/if}
		<InfoCard title="Informações de Auditoria" items={auditInfoData} />
	</div>
	<div class="grid gap-6 md:grid-cols-2">
		<Card.Root>
			<Card.Header>
				<Card.Title>Processos</Card.Title>
			</Card.Header>
			<Card.Content>
				<div class="space-y-2">
					{#if !caso.processos || caso.processos.length === 0}
						<div class="text-center py-8 text-muted-foreground">
							<p>Nenhum processo associado a este caso.</p>
						</div>
					{:else}
						{#each caso.processos as processo}
							<div class="flex items-center justify-between p-2 rounded-lg bg-muted/50">
								<div class="flex items-center gap-2">
									<File class="h-4 w-4" />
									<span>{processo.numero}</span>
								</div>
								<Button variant="ghost" size="sm" href="/casos/{caso.id}/processos/{processo.id}">
									<Eye class="h-4 w-5" />
								</Button>
							</div>
						{/each}
					{/if}
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title class="flex items-center justify-between">
					<span>Arquivos</span>
					<Button
						variant="default"
						size="sm"
						onclick={() => fileInput?.click()}
						disabled={isUploading}
					>
						<Upload class="h-4 w-4 mr-2" />
						{isUploading ? 'Enviando...' : 'Upload'}
					</Button>
				</Card.Title>
			</Card.Header>
			<Card.Content>
				<input type="file" bind:this={fileInput} onchange={handleFileUpload} class="hidden" />
				<div class="space-y-2">
					{#if !arquivos || arquivos.length === 0}
						<div class="text-center py-8 text-muted-foreground">
							<p>Nenhum arquivo anexado a este caso.</p>
						</div>
					{:else}
						{#each arquivos as arquivo}
							<div class="flex items-center justify-between p-3 rounded-lg bg-muted/50">
								<div class="flex items-center gap-2">
									<FileText class="h-5 w-5" />
									<span class="text-sm"
										>{arquivo.link_arquivo.split('/').pop()?.split('_').pop()}</span
									>
								</div>
								<div class="flex gap-1">
									<Button variant="ghost" size="sm" onclick={() => handleDownload(arquivo)}>
										<Download class="h-4 w-4" />
									</Button>
									<Button variant="ghost" size="sm" onclick={() => handleDelete(arquivo.id)}>
										<Trash2 class="h-4 w-4 text-destructive" />
									</Button>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</Card.Content>
		</Card.Root>
	</div>

	<Card.Root>
		<Card.Header>
			<Card.Title class="flex items-center justify-between">
				<span>Eventos</span>
				<Button variant="default" size="sm" onclick={() => (eventoDialogOpen = true)}>
					<Plus class="h-4 w-4" /> Novo Evento
				</Button>
			</Card.Title>
		</Card.Header>
		<Card.Content>
			<DataTable
				data={eventos}
				columns={eventoColumns}
				actions={{ buttons: eventoButtons }}
				emptyText="Nenhum evento associado a este caso."
			/>
		</Card.Content>
	</Card.Root>
</div>

<EventoDialog {eventoFormData} open={eventoDialogOpen} onSuccess={refreshEventos} />
