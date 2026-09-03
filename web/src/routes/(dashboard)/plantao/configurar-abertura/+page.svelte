<script lang="ts">
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

	/** Separa o datetime RFC-1123 da API nas partes que os inputs esperam. */
	function separarDataHora(valor: string | null): { data: string; hora: string } {
		if (!valor) return { data: '', hora: '' };
		const d = new Date(valor);
		if (Number.isNaN(d.getTime())) return { data: '', hora: '' };
		const pad = (n: number) => String(n).padStart(2, '0');
		return {
			data: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
			hora: `${pad(d.getHours())}:${pad(d.getMinutes())}`
		};
	}

	const abertura = separarDataHora(data.configuracao.data_abertura);
	const fechamento = separarDataHora(data.configuracao.data_fechamento);

	let diasSelecionados = $state<DateValue[]>(data.configuracao.dias.map(paraCalendarDate));
	let dataAbertura = $state(abertura.data);
	let horaAbertura = $state(abertura.hora);
	let dataFechamento = $state(fechamento.data);
	let horaFechamento = $state(fechamento.hora);
	let salvando = $state(false);

	const diasISO = $derived(
		[...diasSelecionados].map((d) => d.toString()).sort((a, b) => a.localeCompare(b))
	);

	const tituloMes = $derived.by(() => {
		const agora = new Date();
		return `${String(agora.getMonth() + 1).padStart(2, '0')}/${agora.getFullYear()}`;
	});

	function validar(): string | null {
		if (!dataAbertura || !horaAbertura) return 'Informe a data e o horário de abertura';
		if (!dataFechamento || !horaFechamento) return 'Informe a data e o horário de fechamento';
		if (`${dataFechamento}T${horaFechamento}` <= `${dataAbertura}T${horaAbertura}`) {
			return 'O fechamento deve ser posterior à abertura';
		}
		return null;
	}

	async function salvar() {
		const erro = validar();
		if (erro) {
			toast.error(erro);
			return;
		}

		salvando = true;
		try {
			await api.put<ConfiguracaoPlantao>('plantao/configuracao', {
				dias: diasISO,
				data_abertura: `${dataAbertura}T${horaAbertura}:00`,
				data_fechamento: `${dataFechamento}T${horaFechamento}:00`
			});
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
	<h1 class="text-3xl font-bold tracking-tight">Configurar abertura - {tituloMes}</h1>

	<div class="grid gap-6 lg:grid-cols-2">
		<Card.Root>
			<Card.Header>
				<Card.Title class="text-center">Duração do Plantão</Card.Title>
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
					<Card.Title>Abertura do Plantão</Card.Title>
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
					<Card.Title>Fechamento do Plantão</Card.Title>
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
			title="Deseja confirmar a duração do plantão?"
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
