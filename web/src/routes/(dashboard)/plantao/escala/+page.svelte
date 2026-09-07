<script lang="ts">
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import { ApiException } from '$lib/types';
	import { situacaoEscala } from '$lib/constants/escalas';
	import { invalidateAll } from '$app/navigation';
	import { unidadeAtiva } from '$lib/stores/unidade';
	import Calendar from '$lib/components/ui/calendar/calendar.svelte';
	import * as CalendarUI from '$lib/components/ui/calendar/index.js';
	import { Button, buttonVariants } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';
	import ConfirmAction from '$lib/components/confirm-action.svelte';
	import { CalendarDate, type DateValue } from '@internationalized/date';
	import { cn } from '$lib/utils';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	const me = $derived(data.me);
	const pagina = $derived(data.pagina);
	const unidade = $derived(
		me.unidades?.find((item) => item.id === $unidadeAtiva) ?? me.unidades?.[0]
	);
	let diaSelecionado = $state<DateValue | undefined>(undefined);
	let salvando = $state(false);

	$effect(() => {
		$unidadeAtiva;
		pagina.plantao.id;
		diaSelecionado = undefined;
	});

	const podeConfigurar = $derived(['admin', 'colab_proj'].includes(me.urole));
	const acoes: Record<string, string> = {
		criar: 'Criou a escala',
		configurar: 'Alterou a configuração',
		inscrever: 'Inscreveu-se',
		retirar_inscricoes: 'Retirou inscrições',
		cancelar: 'Cancelou a escala'
	};
	function resumoConfiguracao(config: {
		nome: string;
		dias: string[];
		data_abertura: string | null;
		data_fechamento: string | null;
	}) {
		return `${config.nome}. Dias: ${config.dias.map(formatData).join(', ')}. Inscrições: ${config.data_abertura?.replace('T', ' ')} até ${config.data_fechamento?.replace('T', ' ')} (Brasília).`;
	}

	/** Disponibilidade por dia aberto, indexada pela data ISO. */
	const porData = $derived(new Map(pagina.dias_abertos.map((d) => [d.data, d])));

	const dataSelecionadaISO = $derived(diaSelecionado ? diaSelecionado.toString() : null);

	const escaladosDoDia = $derived(
		dataSelecionadaISO ? pagina.escala.filter((e) => e.data === dataSelecionadaISO) : []
	);

	const diaAbertoSelecionado = $derived(
		dataSelecionadaISO ? porData.get(dataSelecionadaISO) : undefined
	);

	function formatData(iso: string): string {
		if (!iso) return 'Data não informada';
		const [ano, mes, dia] = iso.split('-');
		return `${dia}/${mes}/${ano}`;
	}

	function formatDiaExtenso(iso: string): string {
		const [ano, mes, dia] = iso.split('-').map(Number);
		return new CalendarDate(ano, mes, dia).toDate('UTC').toLocaleDateString('pt-BR', {
			day: 'numeric',
			month: 'long',
			timeZone: 'UTC'
		});
	}

	/** Cor da borda do dia no calendário: verde = tem vaga, vermelho = lotado. */
	function classeDoDia(dia: DateValue): string {
		const info = porData.get(dia.toString());
		if (!info) return '';
		return info.tem_vaga
			? 'border-2 border-green-500 rounded-md'
			: 'border-2 border-destructive rounded-md';
	}

	async function marcar() {
		if (!dataSelecionadaISO) {
			toast.error('Selecione uma data no calendário');
			return;
		}

		salvando = true;
		try {
			await api.post(`plantao/marcacoes?escala_id=${pagina.plantao.id}`, {
				data: dataSelecionadaISO
			});
			await invalidateAll();
			toast.success('Data de plantão cadastrada!');
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao marcar o dia de plantão');
		} finally {
			salvando = false;
		}
	}

	async function limpar() {
		try {
			await api.delete(`plantao/marcacoes?escala_id=${pagina.plantao.id}`);
			await invalidateAll();
			toast.success('Registro apagado. Selecione novamente os dias do seu plantão.');
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao apagar os dias de plantão');
		}
	}
</script>

<div class="space-y-6">
	<Button variant="outline" href="/plantao/escalas">Voltar às escalas</Button>
	<h1 class="text-3xl font-bold tracking-tight">
		{pagina.plantao.nome}{unidade ? ` — ${unidade.nome}` : ''}
	</h1>

	<Card.Root>
		<Card.Content class="flex flex-wrap items-center justify-between gap-4 py-4">
			<span>Nome do funcionário: <span class="font-medium">{me.nome}</span></span>
			<div class="flex items-center gap-2">
				{#if podeConfigurar && !pagina.plantao.legado && !pagina.plantao.cancelado}
					<Button
						href={`/plantao/configurar-abertura?escala_id=${pagina.plantao.id}`}
						variant="outline">Configurar escala</Button
					>
					<ConfirmAction
						title="Cancelar esta escala?"
						description="As inscrições serão bloqueadas. Dias, marcações e confirmações permanecerão no histórico."
						confirmText="Cancelar escala"
						triggerText="Cancelar escala"
						onConfirm={async () => {
							try {
								await api.post(`plantao/escalas/${pagina.plantao.id}/cancelar`);
								await invalidateAll();
								toast.success('Escala cancelada');
							} catch (err) {
								toast.error(err instanceof ApiException ? err.message : 'Erro ao cancelar escala');
							}
						}}
					/>
				{/if}
				{#if pagina.pode_marcar}<ConfirmAction
						title="Deseja retirar suas inscrições desta escala?"
						description="Todos os dias que você marcou serão apagados e você poderá escolher novamente."
						confirmText="Apagar"
						triggerText="Alterar meus dias"
						triggerClass={buttonVariants({ variant: 'outline' })}
						onConfirm={limpar}
					/>{/if}
			</div>
		</Card.Content>
	</Card.Root>

	{#if !pagina.plantao.aberto}
		<Card.Root class="border-destructive">
			<Card.Content class="py-4 text-destructive">
				{situacaoEscala[pagina.plantao.situacao]}. A escala permanece disponível para consulta.
				{#if pagina.pode_marcar}
					<span class="text-muted-foreground">
						Seu perfil permite ajustes fora do prazo. As alterações ficam registradas no histórico.
					</span>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}

	<div class="grid gap-6 lg:grid-cols-3">
		<Card.Root>
			<Card.Content class="flex flex-col items-center gap-4 pt-6">
				<Calendar
					type="single"
					bind:value={diaSelecionado as never}
					captionLayout="dropdown"
					locale="pt-BR"
					calendarLabel="Dias de plantão"
				>
					{#snippet day({ day })}
						<CalendarUI.Day class={cn(classeDoDia(day))} />
					{/snippet}
				</Calendar>

				<div class="flex items-center gap-4 text-xs text-muted-foreground">
					<span class="flex items-center gap-1.5">
						<span class="h-3 w-3 rounded-sm border-2 border-green-500"></span> Com vaga
					</span>
					<span class="flex items-center gap-1.5">
						<span class="h-3 w-3 rounded-sm border-2 border-destructive"></span>
						Sem vaga
					</span>
				</div>

				<Button onclick={marcar} disabled={salvando || !pagina.pode_marcar} class="w-full">
					{salvando ? 'Salvando...' : 'Selecionar data'}
				</Button>
			</Card.Content>
		</Card.Root>

		<div class="space-y-6">
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-base font-normal">Dia do plantão:</Card.Title>
				</Card.Header>
				<Card.Content class="flex items-center justify-around">
					{#each Array(pagina.limite_dias) as _, indice (indice)}
						<span
							class={cn(
								'flex h-12 w-12 items-center justify-center rounded-full border-2 text-lg',
								pagina.numero_plantao === indice + 1
									? 'border-primary bg-primary text-primary-foreground'
									: 'border-muted-foreground/40 text-muted-foreground'
							)}
						>
							{indice + 1}º
						</span>
					{/each}
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title class="text-base font-normal">Usuários escalados:</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-3">
					{#if !dataSelecionadaISO}
						<p class="text-muted-foreground">Selecione um dia no calendário.</p>
					{:else if escaladosDoDia.length === 0}
						<p class="text-muted-foreground">
							Não há escalados para {formatDiaExtenso(dataSelecionadaISO)}.
						</p>
					{:else}
						<ul class="list-inside list-disc space-y-1">
							{#each escaladosDoDia as escalado (escalado.id)}
								<li>
									{escalado.nome} — {escalado.confirmacao}{#if !escalado.ativo}
										(registro inativo no legado){/if}
								</li>
							{/each}
						</ul>
					{/if}

					{#if diaAbertoSelecionado}
						<p class="text-sm text-muted-foreground">
							Vagas disponíveis: {diaAbertoSelecionado.vagas_restantes ?? 'Sem limites'}
						</p>
					{:else if dataSelecionadaISO}
						<p class="text-sm text-muted-foreground">Esta data não foi aberta para plantão.</p>
					{/if}
				</Card.Content>
			</Card.Root>
		</div>

		<Card.Root>
			<Card.Header>
				<Card.Title class="text-base font-normal">Seus dias de plantão:</Card.Title>
			</Card.Header>
			<Card.Content>
				{#if pagina.meus_dias.length === 0}
					<p class="text-muted-foreground">Ainda não escolheu os dias de plantão</p>
				{:else}
					<ul class="space-y-2">
						{#each pagina.meus_dias as marcacao (marcacao.id)}
							<li class="flex items-center justify-between gap-2">
								<span>{formatData(marcacao.data_marcada)}</span>
								{#if marcacao.confirmacao !== 'aberto'}
									<Badge variant="secondary">{marcacao.confirmacao}</Badge>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</Card.Content>
		</Card.Root>
	</div>
</div>

{#if pagina.plantao.legado}
	<p class="my-4 text-muted-foreground">
		Registros anteriores à organização por escalas. Os períodos originais não podem ser
		reconstruídos com segurança. Datas, confirmações e estados foram preservados; este agrupamento é
		somente para consulta.
	</p>
	<div class="overflow-x-auto rounded-lg border">
		<table class="w-full text-left text-sm">
			<thead
				><tr
					><th class="p-3">Data</th><th class="p-3">Usuário</th><th class="p-3">Confirmação</th><th
						class="p-3">Registro original</th
					></tr
				></thead
			><tbody>
				{#each pagina.escala as item (item.id)}<tr class="border-t"
						><td class="p-3">{formatData(item.data)}</td><td class="p-3">{item.nome}</td><td
							class="p-3">{item.confirmacao}</td
						><td class="p-3">{item.ativo ? 'Ativo' : 'Inativo'}</td></tr
					>{:else}<tr><td colspan="4" class="p-4">Nenhuma marcação no legado desta escala.</td></tr
					>{/each}
			</tbody>
		</table>
	</div>
{/if}
{#if podeConfigurar && pagina.historico.length}
	<details class="mt-6 rounded-lg border p-4">
		<summary class="cursor-pointer font-medium">Histórico de alterações</summary>
		<ul class="mt-4 space-y-2">
			{#each pagina.historico as item}<li>
					{item.data.slice(0, 19).replace('T', ' ')} — {item.usuario_nome}: {acoes[item.acao] ??
						item.acao}
					{#if item.detalhes?.dia}
						em {formatData(item.detalhes.dia)}{/if}
					{#if item.detalhes?.fora_do_prazo}
						(ajuste administrativo fora do prazo){/if}
					{#if item.detalhes?.quantidade !== undefined}
						— {item.detalhes.quantidade} inscrição(ões){/if}
					{#if item.detalhes?.depois}<details>
							<summary>Configuração registrada</summary>
							{#if item.detalhes.antes}<p class="mt-2 text-sm">
									Anterior: {resumoConfiguracao(item.detalhes.antes)}
								</p>{/if}
							<p class="mt-2 text-sm">Salva: {resumoConfiguracao(item.detalhes.depois)}</p>
						</details>{/if}
				</li>{/each}
		</ul>
	</details>
{/if}
