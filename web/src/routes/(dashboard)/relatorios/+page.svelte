<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import * as Select from '$lib/components/ui/select';
	import * as Table from '$lib/components/ui/table';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { AREA_DIREITO_OPTIONS } from '$lib/constants';
	import { SITUACAO_DEFERIMENTO_OPTIONS } from '$lib/constants/situacao-deferimento';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import Download from '@lucide/svelte/icons/download';

	import { getUserRoleLabel } from '$lib/constants/user-roles';

	type ReportRow = {
		area_direito?: string;
		situacao_deferimento?: string;
		quantidade: number;
	};

	// Relatório "Horário de chegada e saída dos usuários", herdado da v2.
	type PresencaRow = {
		id: number;
		id_usuario: number;
		nome: string;
		urole: string;
		data: string;
		entrada: string;
		saida: string;
		confirmacao: string;
	};
	type PlantaoRow = {
		id: number;
		id_usuario: number;
		nome: string;
		urole: string;
		data: string;
		confirmacao: string;
	};
	type HorariosResult = {
		presencas: PresencaRow[];
		plantoes: PlantaoRow[];
		total_presencas: number;
		total_plantoes: number;
	};
	type UsuarioOption = { id: number; nome: string; urole: string };

	const HORARIOS = 'horarios';

	const confirmacaoLabels: Record<string, string> = {
		aberto: 'Não conferido',
		confirmar: 'Confirmado',
		divergencia: 'Divergência',
		ausencia: 'Ausência'
	};

	const reportTypes = [
		{
			value: 'casos-por-orientacao',
			label: 'Casos por Orientação Jurídica',
			dimensionLabel: 'Área do Direito',
			dimensionKey: 'area_direito'
		},
		{
			value: 'casos-por-status',
			label: 'Casos por Situação',
			dimensionLabel: 'Situação',
			dimensionKey: 'situacao_deferimento'
		},
		{
			value: 'casos-cadastrados',
			label: 'Casos Cadastrados por Área',
			dimensionLabel: 'Área do Direito',
			dimensionKey: 'area_direito'
		},
		{
			value: HORARIOS,
			label: 'Horário de chegada e saída dos usuários',
			dimensionLabel: 'Usuário',
			dimensionKey: 'usuario'
		}
	] as const;

	const areaLabels = Object.fromEntries(AREA_DIREITO_OPTIONS.map((o) => [o.value, o.label]));
	const situacaoLabels = Object.fromEntries(
		SITUACAO_DEFERIMENTO_OPTIONS.map((o) => [o.value, o.label])
	);

	let reportType = $state<string>('casos-por-orientacao');
	let dataInicio = $state('');
	let dataFinal = $state('');
	let selectedAreas = $state<string[]>([]);
	let loading = $state(false);
	let rows = $state<ReportRow[] | null>(null);
	let total = $state(0);
	let generatedType = $state<(typeof reportTypes)[number] | null>(null);

	const currentType = $derived(reportTypes.find((r) => r.value === reportType)!);
	const isHorarios = $derived(reportType === HORARIOS);

	let usuarios = $state<UsuarioOption[] | null>(null);
	let selectedUsuarios = $state<number[]>([]);
	let horarios = $state<HorariosResult | null>(null);

	function toggleArea(area: string, checked: boolean) {
		selectedAreas = checked ? [...selectedAreas, area] : selectedAreas.filter((a) => a !== area);
	}

	function toggleUsuario(id: number, checked: boolean) {
		selectedUsuarios = checked
			? [...selectedUsuarios, id]
			: selectedUsuarios.filter((u) => u !== id);
	}

	// A lista de usuários só é buscada quando o relatório de horários é escolhido.
	$effect(() => {
		if (isHorarios && usuarios === null) {
			api
				.get<{ items: UsuarioOption[] }>('user/opcoes')
				.then((data) => (usuarios = data.items))
				.catch(() => {
					usuarios = [];
					toast.error('Erro ao carregar a lista de usuários');
				});
		}
	});

	function formatData(iso: string): string {
		const [ano, mes, dia] = iso.split('-');
		return `${dia}/${mes}/${ano}`;
	}

	function confirmacaoLabel(valor: string): string {
		return confirmacaoLabels[valor] ?? valor;
	}

	function dimensionLabelFor(row: ReportRow, type: (typeof reportTypes)[number]): string {
		if (type.dimensionKey === 'situacao_deferimento') {
			return situacaoLabels[row.situacao_deferimento ?? ''] ?? row.situacao_deferimento ?? '—';
		}
		return areaLabels[row.area_direito ?? ''] ?? row.area_direito ?? '—';
	}

	async function generate() {
		if (!dataInicio || !dataFinal) {
			toast.error('Informe a data inicial e final');
			return;
		}
		loading = true;
		rows = null;
		horarios = null;
		try {
			const params = new URLSearchParams({
				data_inicio: dataInicio,
				data_final: dataFinal
			});

			if (reportType === HORARIOS) {
				if (selectedUsuarios.length > 0) params.set('usuarios', selectedUsuarios.join(','));
				horarios = await api.get<HorariosResult>(`relatorio/horarios?${params.toString()}`);
				generatedType = currentType;
				return;
			}

			if (selectedAreas.length > 0) params.set('areas', selectedAreas.join(','));

			const data = await api.get<{ items: ReportRow[]; total: number }>(
				`relatorio/${reportType}?${params.toString()}`
			);
			rows = data.items;
			total = data.total;
			generatedType = currentType;
		} catch {
			toast.error('Erro ao gerar relatório');
		} finally {
			loading = false;
		}
	}

	function baixarCsv(nome: string, linhas: string[]) {
		// BOM para o Excel reconhecer UTF-8.
		const csv = '\ufeff' + linhas.join('\n');
		const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = nome;
		a.click();
		URL.revokeObjectURL(url);
	}

	function downloadCsv() {
		if (!generatedType) return;

		if (horarios) {
			const linhas = ['Presenças', 'Data;Nome;Cargo;Entrada;Saída;Conferência'];
			for (const p of horarios.presencas) {
				linhas.push(
					`${formatData(p.data)};${p.nome};${getUserRoleLabel(p.urole)};${p.entrada};${p.saida};${confirmacaoLabel(p.confirmacao)}`
				);
			}
			linhas.push('', 'Plantões', 'Data;Nome;Cargo;Conferência');
			for (const m of horarios.plantoes) {
				linhas.push(
					`${formatData(m.data)};${m.nome};${getUserRoleLabel(m.urole)};${confirmacaoLabel(m.confirmacao)}`
				);
			}
			baixarCsv(`horarios_${dataInicio}_${dataFinal}.csv`, linhas);
			return;
		}

		if (!rows) return;
		const header = `${generatedType.dimensionLabel};Quantidade`;
		const lines = rows.map((r) => `${dimensionLabelFor(r, generatedType!)};${r.quantidade}`);
		lines.push(`Total;${total}`);
		baixarCsv(`${generatedType.value}_${dataInicio}_${dataFinal}.csv`, [header, ...lines]);
	}
</script>

<div class="max-w-4xl space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Relatórios</h1>
		<p class="mt-2 text-muted-foreground">
			Gere relatórios por intervalo de datas e área do direito.
		</p>
	</div>

	<Card.Root>
		<Card.Header>
			<Card.Title>Parâmetros</Card.Title>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div class="grid gap-4 md:grid-cols-3">
				<div class="space-y-1">
					<Label>Tipo de Relatório</Label>
					<Select.Root type="single" bind:value={reportType}>
						<Select.Trigger class="w-full">{currentType.label}</Select.Trigger>
						<Select.Content>
							{#each reportTypes as rt}
								<Select.Item value={rt.value}>{rt.label}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>
				<div class="space-y-1">
					<Label for="data-inicio">Data Inicial</Label>
					<Input id="data-inicio" type="date" bind:value={dataInicio} />
				</div>
				<div class="space-y-1">
					<Label for="data-final">Data Final</Label>
					<Input id="data-final" type="date" bind:value={dataFinal} />
				</div>
			</div>

			{#if isHorarios}
				<div class="space-y-2">
					<Label>Usuários (opcional — vazio = todos)</Label>
					{#if usuarios === null}
						<p class="text-sm text-muted-foreground">Carregando usuários...</p>
					{:else if usuarios.length === 0}
						<p class="text-sm text-muted-foreground">Nenhum usuário ativo encontrado.</p>
					{:else}
						<div
							class="grid max-h-64 gap-2 overflow-y-auto rounded-md border p-3 sm:grid-cols-2 lg:grid-cols-3"
						>
							{#each usuarios as usuario (usuario.id)}
								<label class="flex cursor-pointer items-center gap-2">
									<Checkbox
										checked={selectedUsuarios.includes(usuario.id)}
										onCheckedChange={(c) => toggleUsuario(usuario.id, !!c)}
									/>
									<span class="truncate text-sm" title={usuario.nome}>
										{usuario.nome}
										<span class="text-muted-foreground"> · {getUserRoleLabel(usuario.urole)}</span>
									</span>
								</label>
							{/each}
						</div>
					{/if}
				</div>
			{:else}
				<div class="space-y-2">
					<Label>Áreas do Direito (opcional — vazio = todas)</Label>
					<div class="flex flex-wrap gap-4">
						{#each AREA_DIREITO_OPTIONS as area}
							<label class="flex cursor-pointer items-center gap-2">
								<Checkbox
									checked={selectedAreas.includes(area.value)}
									onCheckedChange={(c) => toggleArea(area.value, !!c)}
								/>
								<span class="text-sm">{area.label}</span>
							</label>
						{/each}
					</div>
				</div>
			{/if}

			<div class="flex justify-end">
				<Button onclick={generate} disabled={loading}>
					{loading ? 'Gerando...' : 'Gerar Relatório'}
				</Button>
			</div>
		</Card.Content>
	</Card.Root>

	{#if horarios}
		<Card.Root>
			<Card.Header>
				<Card.Title class="flex items-center justify-between">
					<span>{generatedType?.label}</span>
					<Button
						variant="outline"
						size="sm"
						onclick={downloadCsv}
						disabled={horarios.total_presencas + horarios.total_plantoes === 0}
					>
						<Download class="mr-2 h-4 w-4" /> Baixar CSV
					</Button>
				</Card.Title>
			</Card.Header>
			<Card.Content class="space-y-6">
				<section class="space-y-2">
					<h3 class="text-lg font-semibold">Presenças ({horarios.total_presencas})</h3>
					{#if horarios.presencas.length === 0}
						<p class="text-sm text-muted-foreground">Nenhum registro de presença no período.</p>
					{:else}
						<Table.Root>
							<Table.Header>
								<Table.Row>
									<Table.Head>Data</Table.Head>
									<Table.Head>Nome</Table.Head>
									<Table.Head>Cargo</Table.Head>
									<Table.Head>Entrada</Table.Head>
									<Table.Head>Saída</Table.Head>
									<Table.Head>Conferência</Table.Head>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each horarios.presencas as p (p.id)}
									<Table.Row>
										<Table.Cell>{formatData(p.data)}</Table.Cell>
										<Table.Cell>{p.nome}</Table.Cell>
										<Table.Cell>{getUserRoleLabel(p.urole)}</Table.Cell>
										<Table.Cell>{p.entrada}</Table.Cell>
										<Table.Cell>{p.saida}</Table.Cell>
										<Table.Cell>
											<Badge variant="secondary">{confirmacaoLabel(p.confirmacao)}</Badge>
										</Table.Cell>
									</Table.Row>
								{/each}
							</Table.Body>
						</Table.Root>
					{/if}
				</section>

				<section class="space-y-2">
					<h3 class="text-lg font-semibold">Plantões ({horarios.total_plantoes})</h3>
					{#if horarios.plantoes.length === 0}
						<p class="text-sm text-muted-foreground">Nenhum dia de plantão marcado no período.</p>
					{:else}
						<Table.Root>
							<Table.Header>
								<Table.Row>
									<Table.Head>Data</Table.Head>
									<Table.Head>Nome</Table.Head>
									<Table.Head>Cargo</Table.Head>
									<Table.Head>Conferência</Table.Head>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each horarios.plantoes as m (m.id)}
									<Table.Row>
										<Table.Cell>{formatData(m.data)}</Table.Cell>
										<Table.Cell>{m.nome}</Table.Cell>
										<Table.Cell>{getUserRoleLabel(m.urole)}</Table.Cell>
										<Table.Cell>
											<Badge variant="secondary">{confirmacaoLabel(m.confirmacao)}</Badge>
										</Table.Cell>
									</Table.Row>
								{/each}
							</Table.Body>
						</Table.Root>
					{/if}
				</section>
			</Card.Content>
		</Card.Root>
	{:else if rows}
		<Card.Root>
			<Card.Header>
				<Card.Title class="flex items-center justify-between">
					<span>{generatedType?.label}</span>
					<Button variant="outline" size="sm" onclick={downloadCsv} disabled={rows.length === 0}>
						<Download class="mr-2 h-4 w-4" /> Baixar CSV
					</Button>
				</Card.Title>
			</Card.Header>
			<Card.Content>
				{#if rows.length === 0}
					<p class="text-sm text-muted-foreground">
						Nenhum resultado para o período e filtros selecionados.
					</p>
				{:else}
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>{generatedType?.dimensionLabel}</Table.Head>
								<Table.Head class="text-right">Quantidade</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each rows as row}
								<Table.Row>
									<Table.Cell>
										<Badge variant="secondary">{dimensionLabelFor(row, generatedType!)}</Badge>
									</Table.Cell>
									<Table.Cell class="text-right font-medium">{row.quantidade}</Table.Cell>
								</Table.Row>
							{/each}
							<Table.Row class="border-t-2">
								<Table.Cell class="font-bold">Total</Table.Cell>
								<Table.Cell class="text-right font-bold">{total}</Table.Cell>
							</Table.Row>
						</Table.Body>
					</Table.Root>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</div>
