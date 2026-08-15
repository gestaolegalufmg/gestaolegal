<script lang="ts">
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import { ApiException, type PaginaPlantao } from '$lib/types';
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
	let pagina = $state<PaginaPlantao>(data.pagina);
	let diaSelecionado = $state<DateValue | undefined>(undefined);
	let salvando = $state(false);

	const podeConfigurar = $derived(['admin', 'colab_proj'].includes(me.urole));

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
		const [ano, mes, dia] = iso.split('-');
		return `${dia}/${mes}/${ano}`;
	}

	function formatDiaExtenso(iso: string): string {
		const [ano, mes, dia] = iso.split('-').map(Number);
		return new CalendarDate(ano, mes, dia)
			.toDate('UTC')
			.toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', timeZone: 'UTC' });
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
			pagina = await api.post<PaginaPlantao>('plantao/marcacoes', { data: dataSelecionadaISO });
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
			pagina = await api.delete<PaginaPlantao>('plantao/marcacoes');
			toast.success('Registro apagado. Selecione novamente os dias do seu plantão.');
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao apagar os dias de plantão');
		}
	}
</script>

<div class="space-y-6">
	<h1 class="text-3xl font-bold tracking-tight">Escala do Plantão</h1>

	<Card.Root>
		<Card.Content class="flex flex-wrap items-center justify-between gap-4 py-4">
			<span>Nome do funcionário: <span class="font-medium">{me.nome}</span></span>
			<div class="flex items-center gap-2">
				{#if podeConfigurar}
					<Button href="/plantao/configurar-abertura" variant="outline">Configurar Abertura</Button>
				{/if}
				<ConfirmAction
					title="Deseja apagar seus dias de plantão?"
					description="Todos os dias que você marcou serão apagados e você poderá escolher novamente."
					confirmText="Apagar"
					triggerText="Editar"
					triggerClass={buttonVariants({ variant: 'outline' })}
					onConfirm={limpar}
				/>
			</div>
		</Card.Content>
	</Card.Root>

	{#if !pagina.plantao.aberto}
		<Card.Root class="border-destructive">
			<Card.Content class="text-destructive py-4">
				O plantão não está aberto!
				{#if pagina.pode_marcar}
					<span class="text-muted-foreground">
						Como administrador, você ainda pode marcar os dias disponíveis.
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

				<div class="text-muted-foreground flex items-center gap-4 text-xs">
					<span class="flex items-center gap-1.5">
						<span class="h-3 w-3 rounded-sm border-2 border-green-500"></span> Com vaga
					</span>
					<span class="flex items-center gap-1.5">
						<span class="border-destructive h-3 w-3 rounded-sm border-2"></span> Sem vaga
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
							{#each escaladosDoDia as escalado (escalado.id_usuario + escalado.data)}
								<li>{escalado.nome}</li>
							{/each}
						</ul>
					{/if}

					{#if diaAbertoSelecionado}
						<p class="text-muted-foreground text-sm">
							Vagas disponíveis: {diaAbertoSelecionado.vagas_restantes ?? 'Sem limites'}
						</p>
					{:else if dataSelecionadaISO}
						<p class="text-muted-foreground text-sm">Esta data não foi aberta para plantão.</p>
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
