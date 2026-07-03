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

	type ReportRow = {
		area_direito?: string;
		situacao_deferimento?: string;
		quantidade: number;
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

	function toggleArea(area: string, checked: boolean) {
		selectedAreas = checked
			? [...selectedAreas, area]
			: selectedAreas.filter((a) => a !== area);
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
		try {
			const params = new URLSearchParams({
				data_inicio: dataInicio,
				data_final: dataFinal
			});
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

	function downloadCsv() {
		if (!rows || !generatedType) return;
		const header = `${generatedType.dimensionLabel};Quantidade`;
		const lines = rows.map((r) => `${dimensionLabelFor(r, generatedType!)};${r.quantidade}`);
		lines.push(`Total;${total}`);
		const csv = '﻿' + [header, ...lines].join('\n');
		const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `${generatedType.value}_${dataInicio}_${dataFinal}.csv`;
		a.click();
		URL.revokeObjectURL(url);
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

			<div class="flex justify-end">
				<Button onclick={generate} disabled={loading}>
					{loading ? 'Gerando...' : 'Gerar Relatório'}
				</Button>
			</div>
		</Card.Content>
	</Card.Root>

	{#if rows}
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
