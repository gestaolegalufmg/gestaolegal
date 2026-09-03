<script lang="ts">
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import {
		ApiException,
		CONFIRMACAO,
		type Confirmacao,
		type ConfirmacaoItem,
		type Pendencias
	} from '$lib/types';
	import { getUserRoleLabel } from '$lib/constants/user-roles';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Card from '$lib/components/ui/card';
	import * as Table from '$lib/components/ui/table';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	let pendencias = $state<Pendencias>(data.pendencias);
	let dataSelecionada = $state(data.pendencias.data);
	let carregando = $state(false);
	let salvando = $state(false);

	/** Escolhas ainda não salvas, por id de linha. */
	let escolhasPresenca = $state<Record<number, Confirmacao>>({});
	let escolhasPlantao = $state<Record<number, Confirmacao>>({});

	const OPCOES = [
		{ valor: CONFIRMACAO.CONFIRMAR, rotulo: 'Confirmar' },
		{ valor: CONFIRMACAO.DIVERGENCIA, rotulo: 'Divergência' },
		{ valor: CONFIRMACAO.AUSENCIA, rotulo: 'Ausência' }
	] as const;

	const hoje = new Date().toISOString().slice(0, 10);

	function formatHora(valor: string | null): string {
		if (!valor) return '—';
		return new Date(valor).toLocaleTimeString('pt-BR', {
			hour: '2-digit',
			minute: '2-digit',
			hour12: false
		});
	}

	async function carregar(data: string) {
		carregando = true;
		try {
			pendencias = await api.get<Pendencias>(`presenca/confirmacao?data=${data}`);
			escolhasPresenca = {};
			escolhasPlantao = {};
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao carregar as presenças da data');
		} finally {
			carregando = false;
		}
	}

	function onDataChange(event: Event) {
		const valor = (event.currentTarget as HTMLInputElement).value;
		if (!valor) return;
		dataSelecionada = valor;
		carregar(valor);
	}

	function paraLista(escolhas: Record<number, Confirmacao>): ConfirmacaoItem[] {
		return Object.entries(escolhas).map(([id, confirmacao]) => ({
			id: Number(id),
			confirmacao: confirmacao as ConfirmacaoItem['confirmacao']
		}));
	}

	async function salvar(tipo: 'presencas' | 'plantoes') {
		const itens = paraLista(tipo === 'presencas' ? escolhasPresenca : escolhasPlantao);
		if (itens.length === 0) {
			toast.error('Selecione ao menos uma linha antes de salvar');
			return;
		}

		salvando = true;
		try {
			await api.post('presenca/confirmacao', { [tipo]: itens });
			toast.success('Conferência salva com sucesso');
			await carregar(dataSelecionada);
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao salvar a conferência');
		} finally {
			salvando = false;
		}
	}
</script>

<div class="space-y-6">
	<h1 class="text-3xl font-bold tracking-tight">Confirmar Presença</h1>

	<Card.Root class="w-fit">
		<Card.Content class="flex items-center gap-3 py-4">
			<label for="data-conferencia" class="text-sm font-medium">Data:</label>
			<Input
				id="data-conferencia"
				type="date"
				value={dataSelecionada}
				max={hoje}
				onchange={onDataChange}
				class="w-44"
			/>
		</Card.Content>
	</Card.Root>

	<section class="space-y-3">
		<h2 class="text-2xl font-semibold">Presença</h2>
		{#if carregando}
			<p class="text-muted-foreground">Carregando...</p>
		{:else if pendencias.presencas.length === 0}
			<p class="text-muted-foreground">Nenhuma presença a ser confirmada!</p>
		{:else}
			<Card.Root>
				<Card.Content class="space-y-4 pt-6">
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>Nome</Table.Head>
								<Table.Head>Cargo</Table.Head>
								<Table.Head>Entrada</Table.Head>
								<Table.Head>Saída</Table.Head>
								{#each OPCOES as opcao (opcao.valor)}
									<Table.Head class="text-center">{opcao.rotulo}</Table.Head>
								{/each}
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each pendencias.presencas as presenca (presenca.id)}
								<Table.Row>
									<Table.Cell>{presenca.nome}</Table.Cell>
									<Table.Cell>{getUserRoleLabel(presenca.urole)}</Table.Cell>
									<Table.Cell>{formatHora(presenca.data_entrada)}</Table.Cell>
									<Table.Cell>{formatHora(presenca.data_saida)}</Table.Cell>
									{#each OPCOES as opcao (opcao.valor)}
										<Table.Cell class="text-center">
											<input
												type="radio"
												name="presenca_{presenca.id}"
												value={opcao.valor}
												aria-label="{opcao.rotulo} para {presenca.nome}"
												checked={escolhasPresenca[presenca.id] === opcao.valor}
												onchange={() => (escolhasPresenca[presenca.id] = opcao.valor)}
											/>
										</Table.Cell>
									{/each}
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
					<div class="flex justify-center">
						<Button onclick={() => salvar('presencas')} disabled={salvando}>Salvar</Button>
					</div>
				</Card.Content>
			</Card.Root>
		{/if}
	</section>

	<section class="space-y-3">
		<h2 class="text-2xl font-semibold">Plantão</h2>
		{#if carregando}
			<p class="text-muted-foreground">Carregando...</p>
		{:else if pendencias.plantoes.length === 0}
			<p class="text-muted-foreground">Nenhum plantão a ser confirmado!</p>
		{:else}
			<Card.Root>
				<Card.Content class="space-y-4 pt-6">
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>Nome</Table.Head>
								<Table.Head>Cargo</Table.Head>
								{#each OPCOES as opcao (opcao.valor)}
									<Table.Head class="text-center">{opcao.rotulo}</Table.Head>
								{/each}
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each pendencias.plantoes as plantao (plantao.id)}
								<Table.Row>
									<Table.Cell>{plantao.nome}</Table.Cell>
									<Table.Cell>{getUserRoleLabel(plantao.urole)}</Table.Cell>
									{#each OPCOES as opcao (opcao.valor)}
										<Table.Cell class="text-center">
											<input
												type="radio"
												name="plantao_{plantao.id}"
												value={opcao.valor}
												aria-label="{opcao.rotulo} para {plantao.nome}"
												checked={escolhasPlantao[plantao.id] === opcao.valor}
												onchange={() => (escolhasPlantao[plantao.id] = opcao.valor)}
											/>
										</Table.Cell>
									{/each}
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
					<div class="flex justify-center">
						<Button onclick={() => salvar('plantoes')} disabled={salvando}>Salvar</Button>
					</div>
				</Card.Content>
			</Card.Root>
		{/if}
	</section>
</div>
