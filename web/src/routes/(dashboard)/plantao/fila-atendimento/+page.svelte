<script lang="ts">
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import {
		ApiException,
		FilaStatus,
		type FilaHoje,
		type FilaItem,
		type Atendido
	} from '$lib/types';
	import { getPrioridadeRowClass } from '$lib/constants/fila-atendimento';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as Table from '$lib/components/ui/table';
	import BaseSelectorDialog from '$lib/components/base-selector-dialog.svelte';
	import SenhaModal from '$lib/components/senha-modal.svelte';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import ListPlus from '@lucide/svelte/icons/list-plus';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	let filaData = $state<FilaHoje>(data.fila);
	const fila = $derived(filaData.fila);
	const concluidos = $derived(filaData.atendidos_cancelados);
	const dataFila = $derived(filaData.data);

	let showConcluidos = $state(false);
	let senhaModalOpen = $state(false);
	let atendidoSelecionado = $state<Atendido | null>(null);

	function formatData(iso: string): string {
		const [ano, mes, dia] = iso.split('-');
		return `${dia}/${mes}/${ano}`;
	}

	function formatHora(iso: string | null): string {
		if (!iso) return '—';
		return new Date(iso).toLocaleTimeString('pt-BR', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		});
	}

	async function refresh() {
		try {
			filaData = await api.get<FilaHoje>('fila_atendimento');
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
		}
	}

	async function chamar(item: FilaItem) {
		try {
			await api.post(`fila_atendimento/${item.id}/chamar`);
			toast.success(`Senha ${item.senha} chamada`);
			await refresh();
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao chamar atendido');
		}
	}

	async function tirarDaFila(item: FilaItem) {
		try {
			await api.post(`fila_atendimento/${item.id}/cancelar`);
			toast.success(`Senha ${item.senha} removida da fila`);
			await refresh();
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao remover atendido da fila');
		}
	}

	function onAtendidoSelecionado(atendidos: Atendido[]) {
		if (atendidos[0]) {
			atendidoSelecionado = atendidos[0];
			senhaModalOpen = true;
		}
	}
</script>

<div class="space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">
				Fila de Atendimento — Hoje — {formatData(dataFila)}
			</h1>
			<p class="text-muted-foreground">Gerencie a fila de pessoas aguardando atendimento</p>
		</div>
		<div class="flex items-center gap-4">
			<div class="flex items-center gap-4 text-sm">
				<span class="flex items-center gap-1.5">
					<span class="h-3 w-3 rounded-sm bg-orange-400"></span> Super Prioridade
				</span>
				<span class="flex items-center gap-1.5">
					<span class="h-3 w-3 rounded-sm bg-blue-400"></span> Prioridade
				</span>
				<span class="flex items-center gap-1.5">
					<span class="h-3 w-3 rounded-sm border bg-card"></span> Normal
				</span>
			</div>
		</div>
	</div>

	<div class="flex justify-end">
		<BaseSelectorDialog
			apiEndpoint="atendido"
			multiSelect={false}
			dialogTitle="Selecionar Atendido"
			dialogDescription="Busque e selecione o atendido para incluir na fila de atendimento"
			buttonText="Incluir na Fila de Atendimento"
			emptyStateText="Nenhum atendido encontrado"
			searchPlaceholder="Buscar atendido por nome, CPF..."
			onSelect={onAtendidoSelecionado}
		>
			{#snippet trigger()}
				<ListPlus class="mr-2 h-4 w-4" />
				Incluir na Fila de Atendimento
			{/snippet}
		</BaseSelectorDialog>
	</div>

	<div class="rounded-lg border bg-card">
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head class="w-16">#</Table.Head>
					<Table.Head>Nome</Table.Head>
					<Table.Head>Senha</Table.Head>
					<Table.Head>Hora</Table.Head>
					<Table.Head>Psicologia</Table.Head>
					<Table.Head class="text-right">Ações</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each fila as item, index (item.id)}
					<Table.Row class={getPrioridadeRowClass(item.prioridade)}>
						<Table.Cell class="font-medium">#{index + 1}</Table.Cell>
						<Table.Cell>{item.nome ?? '—'}</Table.Cell>
						<Table.Cell class="font-mono font-semibold">{item.senha}</Table.Cell>
						<Table.Cell>{formatHora(item.data_criacao)}</Table.Cell>
						<Table.Cell>{item.psicologia ? 'Sim' : 'Não'}</Table.Cell>
						<Table.Cell>
							<div class="flex justify-end gap-2">
								<Button variant="outline" size="sm" onclick={() => chamar(item)}>Chamar</Button>
								<Button
									variant="outline"
									size="sm"
									class="border-destructive/50 text-destructive hover:bg-destructive/10 hover:text-destructive"
									onclick={() => tirarDaFila(item)}
								>
									Tirar da fila
								</Button>
							</div>
						</Table.Cell>
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={6} class="py-8 text-center text-muted-foreground">
							Nenhum atendido na fila no momento.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>

	<div class="space-y-3">
		<div class="flex items-center gap-3">
			<h2 class="text-xl font-semibold">Atendidos e cancelados</h2>
			<Button variant="outline" size="sm" onclick={() => (showConcluidos = !showConcluidos)}>
				{#if showConcluidos}
					Ocultar <ChevronUp class="ml-1 h-4 w-4" />
				{:else}
					Expandir <ChevronDown class="ml-1 h-4 w-4" />
				{/if}
			</Button>
		</div>

		{#if showConcluidos}
			<div class="rounded-lg border bg-card">
				<Table.Root>
					<Table.Header>
						<Table.Row>
							<Table.Head class="w-16">#</Table.Head>
							<Table.Head>Nome</Table.Head>
							<Table.Head>Senha</Table.Head>
							<Table.Head>Hora</Table.Head>
							<Table.Head>Psicologia</Table.Head>
							<Table.Head>Chamado/Cancelado às</Table.Head>
							<Table.Head class="text-right">Ações</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each concluidos as item, index (item.id)}
							<Table.Row class={getPrioridadeRowClass(item.prioridade)}>
								<Table.Cell class="font-medium">#{index + 1}</Table.Cell>
								<Table.Cell>{item.nome ?? '—'}</Table.Cell>
								<Table.Cell class="font-mono font-semibold">{item.senha}</Table.Cell>
								<Table.Cell>{formatHora(item.data_criacao)}</Table.Cell>
								<Table.Cell>{item.psicologia ? 'Sim' : 'Não'}</Table.Cell>
								<Table.Cell>{formatHora(item.data_saida ?? item.data_criacao)}</Table.Cell>
								<Table.Cell>
									<div class="flex justify-end">
										{#if item.status === FilaStatus.CHAMADO}
											<Badge
												variant="outline"
												class="border-green-600 text-green-700 dark:text-green-400"
											>
												Chamado
											</Badge>
										{:else}
											<Badge
												variant="outline"
												class="border-red-600 text-red-700 dark:text-red-400"
											>
												Cancelado
											</Badge>
										{/if}
									</div>
								</Table.Cell>
							</Table.Row>
						{:else}
							<Table.Row>
								<Table.Cell colspan={7} class="py-8 text-center text-muted-foreground">
									Nenhum atendido chamado ou cancelado hoje.
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		{/if}
	</div>
</div>

{#if atendidoSelecionado}
	<SenhaModal
		bind:open={senhaModalOpen}
		atendidoId={atendidoSelecionado.id}
		atendidoNome={atendidoSelecionado.nome}
		onIncluded={refresh}
	/>
{/if}
