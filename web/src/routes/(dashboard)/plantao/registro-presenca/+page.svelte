<script lang="ts">
	import type { PageData } from './$types';
	import { api } from '$lib/api-client';
	import { ApiException, type EstadoPresenca, type RegistroPresencaResultado } from '$lib/types';
	import { getUserRoleLabel } from '$lib/constants/user-roles';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Card from '$lib/components/ui/card';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	const me = $derived(data.me);
	let estado = $state<EstadoPresenca>(data.estado);
	let hora = $state(data.estado.hora_sugerida);
	let salvando = $state(false);

	const acao = $derived(estado.status_presenca === 'entrada' ? 'Entrada' : 'Saída');

	function formatData(iso: string): string {
		const [ano, mes, dia] = iso.split('-');
		return `${dia}/${mes}/${ano}`;
	}

	async function registrar() {
		salvando = true;
		try {
			const resultado = await api.post<RegistroPresencaResultado>('presenca/registro', { hora });
			estado = resultado;
			hora = resultado.hora_sugerida;
			toast.success(
				resultado.acao === 'entrada'
					? 'Hora de entrada registrada com sucesso!'
					: 'Hora de saída registrada com sucesso!'
			);
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao registrar presença');
		} finally {
			salvando = false;
		}
	}
</script>

<div class="space-y-6">
	<h1 class="text-3xl font-bold tracking-tight">Registro de Presença do Plantão</h1>

	<Card.Root>
		<Card.Content class="py-4">
			<span class="font-medium">{me.nome}</span>
			<span class="text-muted-foreground"> — {getUserRoleLabel(me.urole)}</span>
		</Card.Content>
	</Card.Root>

	<div class="grid gap-4 md:grid-cols-3">
		<Card.Root>
			<Card.Header>
				<Card.Title class="text-center text-base font-normal">Data de hoje:</Card.Title>
			</Card.Header>
			<Card.Content class="text-center text-lg">
				{formatData(estado.data_hoje)}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title class="text-center text-base font-normal">Registrando</Card.Title>
			</Card.Header>
			<Card.Content class="text-center text-lg font-semibold text-destructive">
				{acao}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title class="text-center text-base font-normal">Horário:</Card.Title>
			</Card.Header>
			<Card.Content class="flex justify-center">
				<Input
					type="time"
					bind:value={hora}
					aria-label="Horário do registro"
					class="w-40 text-center"
				/>
			</Card.Content>
		</Card.Root>
	</div>

	<div class="flex justify-center">
		<Button onclick={registrar} disabled={salvando} class="min-w-64">
			{salvando ? 'Registrando...' : 'Registrar'}
		</Button>
	</div>
</div>
