<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { REGION_BADGE_MAP } from '$lib/constants';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { usePaginatedFilters } from '$lib';

	let { data }: PageProps = $props();
	const { assistencias, me } = $derived(data);

	const areaFilterOptions = [
		{ value: 'todas', label: 'Todas as Áreas' },
		{ value: 'administrativo', label: 'Administrativo' },
		{ value: 'ambiental', label: 'Ambiental' },
		{ value: 'civel', label: 'Cível' },
		{ value: 'empresarial', label: 'Empresarial' },
		{ value: 'penal', label: 'Penal' },
		{ value: 'trabalhista', label: 'Trabalhista' }
	];

	const regiaoFilterOptions = [
		{ value: 'todas', label: 'Todas as Regiões' },
		{ value: 'norte', label: 'Norte' },
		{ value: 'sul', label: 'Sul' },
		{ value: 'leste', label: 'Leste' },
		{ value: 'oeste', label: 'Oeste' },
		{ value: 'noroeste', label: 'Noroeste' },
		{ value: 'centro_sul', label: 'Centro-Sul' },
		{ value: 'nordeste', label: 'Nordeste' },
		{ value: 'pampulha', label: 'Pampulha' },
		{ value: 'barreiro', label: 'Barreiro' },
		{ value: 'venda_nova', label: 'Venda Nova' },
		{ value: 'contagem', label: 'Contagem' },
		{ value: 'betim', label: 'Betim' }
	];

	type AjFilters = {
		search: string;
		show_inactive: boolean;
		area: string;
		regiao: string;
	};

	const { filters, applyFilters, setFilters } = usePaginatedFilters<AjFilters>({
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			area: page.url.searchParams.get('area') ?? 'todas',
			regiao: page.url.searchParams.get('regiao') ?? 'todas'
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			area: f.area,
			regiao: f.regiao
		})
	});

	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;
		await api.delete(`assistencia_judiciaria/${id}`);
		applyFilters();
	}
</script>

<div class="space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<h1 class="min-w-0 text-3xl font-bold tracking-tight">Assistências Judiciárias</h1>
		<Button
			variant="default"
			class="shrink-0 whitespace-nowrap"
			href="/plantao/assistencias-judiciarias/nova-assistencia-judiciaria"
		>
			Nova Assistência Judiciária
		</Button>
	</div>

	<div class="grid gap-6">
		<div class="min-w-0 rounded-lg border bg-card p-6">
			<div class="mb-4 flex items-center justify-between">
				<div class="align-center flex w-full justify-between gap-2">
					<div class="flex items-center gap-2">
						<Input
							bind:value={filters.search}
							ondebounceinput={() => {
								setFilters({ search: filters.search });
								applyFilters();
							}}
							debounceMs={500}
							placeholder="Buscar assistência..."
						/>
						<Select.Root
							bind:value={filters.area}
							name="area"
							type="single"
							onValueChange={() => applyFilters()}
						>
							<Select.Trigger class="w-[180px] data-[placeholder]:text-foreground">
								{areaFilterOptions.find((option) => option.value === filters.area)?.label}
							</Select.Trigger>
							<Select.Content>
								{#each areaFilterOptions as option}
									<Select.Item value={option.value}>{option.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
						<Select.Root
							bind:value={filters.regiao}
							name="regiao"
							type="single"
							onValueChange={() => applyFilters()}
						>
							<Select.Trigger class="w-[180px] data-[placeholder]:text-foreground">
								{regiaoFilterOptions.find((option) => option.value === filters.regiao)?.label}
							</Select.Trigger>
							<Select.Content>
								{#each regiaoFilterOptions as option}
									<Select.Item value={option.value}>{option.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>
					<label class="flex cursor-pointer items-center gap-2">
						<Checkbox bind:checked={filters.show_inactive} onCheckedChange={() => applyFilters()} />
						<span class="text-sm">Incluir inativos</span>
					</label>
				</div>
			</div>

			<DataTable
				data={assistencias}
				onPageChange={(page) => applyFilters({ page })}
				columns={[
					{ header: 'Nome', key: 'nome', class: 'w-[220px]' },
					{ header: 'Região', key: 'regiao', type: 'badge', class: 'w-[130px]', badgeMap: REGION_BADGE_MAP },
					{ header: 'Áreas Atendidas', key: 'areas_atendidas', type: 'array', class: 'w-[200px]' },
					{ header: 'Cidade', key: 'cidade', class: 'w-[130px]' },
					{ header: 'Telefone', key: 'telefone', type: 'tel', class: 'w-[140px]' },
					{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' }
				]}
				actions={{
					class: 'w-[120px] text-right',
					buttons: [
						{
							title: 'Visualizar',
							href: (a) => `/plantao/assistencias-judiciarias/${a.id}`,
							icon: Eye
						},
						{
							title: 'Editar',
							href: (a) => `/plantao/assistencias-judiciarias/${a.id}/editar`,
							icon: Edit
						},
						{
							title: 'Desativar',
							icon: Trash2,
							show: (a) => a.status && isAdmin,
							onClick: async (a) => {
								await handleDelete(a.id);
							},
							class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
						}
					]
				}}
			/>
		</div>
	</div>
</div>
