<script lang="ts">
	import { goto } from '$app/navigation';
	import { unidadeAtiva } from '$lib/stores/unidade';
	import { Button } from '$lib/components/ui/button';
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import { ApiException, type ConfiguracaoPlantao } from '$lib/types';
	import Calendar from '$lib/components/ui/calendar/calendar.svelte';
	import { buttonVariants } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import * as Card from '$lib/components/ui/card';
	import ConfirmAction from '$lib/components/confirm-action.svelte';
	import { CalendarDate, type DateValue } from '@internationalized/date';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	function paraCalendarDate(iso: string): CalendarDate {
		const [ano, mes, dia] = iso.split('-').map(Number);
		return new CalendarDate(ano, mes, dia);
	}

	// API returns local ISO timestamps in Brasília; do not apply browser timezone.
	function separarDataHora(valor: string | null) {
		return { data: valor?.slice(0, 10) ?? '', hora: valor?.slice(11, 16) ?? '' };
	}
	const unidade = $derived(data.me.unidades?.find((u) => u.id === $unidadeAtiva));
	let nome = $state('');
	let diasSelecionados = $state<DateValue[]>([]);
	let dataAbertura = $state('');
	let horaAbertura = $state('');
	let dataFechamento = $state('');
	let horaFechamento = $state('');
	let salvando = $state(false);
	$effect(() => {
		const config = data.configuracao;
		nome = config.nome;
		diasSelecionados = config.dias.map(paraCalendarDate);
		const abertura = separarDataHora(config.data_abertura);
		const fechamento = separarDataHora(config.data_fechamento);
		dataAbertura = abertura.data;
		horaAbertura = abertura.hora;
		dataFechamento = fechamento.data;
		horaFechamento = fechamento.hora;
	});

	const diasISO = $derived(
		[...diasSelecionados].map((d) => d.toString()).sort((a, b) => a.localeCompare(b))
	);

	function validar(): string | null {
		if (!nome.trim()) return 'Informe o nome da escala';
		if (!diasISO.length) return 'Selecione ao menos um dia de plantão';
		if (!dataAbertura || !horaAbertura) return 'Informe a data e o horário de abertura';
		if (!dataFechamento || !horaFechamento) return 'Informe a data e o horário de fechamento';
		if (`${dataFechamento}T${horaFechamento}` <= `${dataAbertura}T${horaAbertura}`) {
			return 'O fechamento deve ser posterior à abertura';
		}
		return null;
	}

	async function salvar() {
		if (salvando) return;
		const erro = validar();
		if (erro) {
			toast.error(erro);
			return;
		}

		salvando = true;
		try {
			const payload = {
				nome: nome.trim(),
				dias: diasISO,
				data_abertura: `${dataAbertura}T${horaAbertura}:00`,
				data_fechamento: `${dataFechamento}T${horaFechamento}:00`
			};
			const resultado = data.configuracao.id
				? await api.put<ConfiguracaoPlantao>(
						`plantao/configuracao?escala_id=${data.configuracao.id}`,
						payload
					)
				: await api.post<ConfiguracaoPlantao>('plantao/escalas', payload);
			await goto(`/plantao/escala?escala_id=${resultado.id}`, { invalidateAll: true });
			toast.success('Configuração do plantão salva com sucesso');
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao salvar a configuração do plantão');
		} finally {
			salvando = false;
		}
	}
</script>

<div class="space-y-6">
	<Button href="/plantao/escalas" variant="outline">Voltar às escalas</Button>
	<h1 class="text-3xl font-bold tracking-tight">
		{data.configuracao.id ? 'Configurar escala' : 'Nova escala'}{unidade
			? ` — ${unidade.nome}`
			: ''}
	</h1>
	<p class="text-muted-foreground">
		Selecione os dias de atendimento e o prazo em que os usuários poderão escolher seus dias.
		Horários de Brasília. Encerrar inscrições preserva a escala.
	</p>
	<Label for="nome-escala">Nome da escala</Label><Input
		id="nome-escala"
		bind:value={nome}
		maxlength={150}
		placeholder="Ex.: Plantões de setembro/2026"
	/>

	<div class="grid gap-6 lg:grid-cols-2">
		<Card.Root>
			<Card.Header>
				<Card.Title class="text-center">Dias de atendimento</Card.Title>
				<Card.Description class="text-center">
					Selecione os dias em que haverá plantão
				</Card.Description>
			</Card.Header>
			<Card.Content class="flex justify-center">
				<Calendar
					type="multiple"
					bind:value={diasSelecionados as never}
					captionLayout="dropdown"
					locale="pt-BR"
					calendarLabel="Dias de plantão"
				/>
			</Card.Content>
			<Card.Footer class="justify-center text-sm text-muted-foreground">
				{diasISO.length}
				{diasISO.length === 1 ? 'dia selecionado' : 'dias selecionados'}
			</Card.Footer>
		</Card.Root>

		<div class="space-y-6">
			<Card.Root>
				<Card.Header>
					<Card.Title>Início das inscrições</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-4">
					<div class="flex items-center justify-between gap-4">
						<Label for="data-abertura"
							>Data de abertura <span class="text-destructive">*</span></Label
						>
						<Input id="data-abertura" type="date" bind:value={dataAbertura} class="w-44" />
					</div>
					<div class="flex items-center justify-between gap-4">
						<Label for="hora-abertura">
							Horário de abertura <span class="text-destructive">*</span>
						</Label>
						<Input id="hora-abertura" type="time" bind:value={horaAbertura} class="w-44" />
					</div>
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>Fim das inscrições</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-4">
					<div class="flex items-center justify-between gap-4">
						<Label for="data-fechamento">
							Data de fechamento <span class="text-destructive">*</span>
						</Label>
						<Input id="data-fechamento" type="date" bind:value={dataFechamento} class="w-44" />
					</div>
					<div class="flex items-center justify-between gap-4">
						<Label for="hora-fechamento">
							Horário de fechamento <span class="text-destructive">*</span>
						</Label>
						<Input id="hora-fechamento" type="time" bind:value={horaFechamento} class="w-44" />
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	</div>

	<div class="flex justify-center">
		<ConfirmAction
			title="Salvar esta escala?"
			description="Os dias selecionados ficarão disponíveis para marcação dentro da janela informada."
			confirmText="Confirmar"
			buttonVariant="default"
			buttonSize="default"
			triggerText={salvando ? 'Salvando...' : 'Salvar'}
			triggerClass="{buttonVariants({ variant: 'default' })} min-w-64"
			onConfirm={salvar}
		/>
	</div>
</div>
