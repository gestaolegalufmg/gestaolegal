<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { SUB_AREA_BADGE_MAP } from '$lib/constants';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { usePaginatedFilters } from '$lib';

	let { data }: PageProps = $props();
	const { orientacoes, me } = $derived(data);

	const areaFilterOptions = [
		{ value: 'todas', label: 'Todas as Áreas' },
		{ value: 'administrativo', label: 'Administrativo' },
		{ value: 'ambiental', label: 'Ambiental' },
		{ value: 'civel', label: 'Cível' },
		{ value: 'empresarial', label: 'Empresarial' },
		{ value: 'penal', label: 'Penal' },
		{ value: 'trabalhista', label: 'Trabalhista' }
	];

	type OrientacaoFilters = {
		search: string;
		show_inactive: boolean;
		area: string;
	};

	const { filters, applyFilters, setFilters } = usePaginatedFilters<OrientacaoFilters>({
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			area: page.url.searchParams.get('area') ?? 'todas'
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			area: f.area
		})
	});

	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await api.delete(`orientacao_juridica/${id}`);

		applyFilters();
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold tracking-tight">Orientações Jurídicas</h1>
		<Button variant="default" href="/plantao/orientacoes-juridicas/nova-orientacao-juridica">
			Nova Orientação Jurídica
		</Button>
	</div>

	<div class="grid gap-6">
		<div class="rounded-lg border bg-card p-6">
			<div class="mb-4 flex items-center justify-between">
				<div class="align-center flex w-full justify-between gap-2">
					<div class="flex items-center gap-2">
					<Input
						bind:value={filters.search}
						ondebounceinput={() => {setFilters({ search: filters.search }); applyFilters();}}
						debounceMs={500}
						placeholder="Buscar orientação..."
					/>
						<Select.Root bind:value={filters.area} name="area" type="single">
							<Select.Trigger class="w-[200px] data-[placeholder]:text-foreground">
								{areaFilterOptions.find((option) => option.value === filters.area)?.label}
							</Select.Trigger>
							<Select.Content>
								{#each areaFilterOptions as option}
									<Select.Item value={option.value}>{option.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>
					<label class="flex cursor-pointer items-center gap-2">
						<Checkbox bind:checked={filters.show_inactive} />
						<span class="text-sm">Incluir inativos</span>
					</label>
				</div>
			</div>

		<DataTable
			data={orientacoes}
			onPageChange={(page) => applyFilters({ page })}
				columns={[
					{
						header: 'Área do Direito',
						key: 'area_direito',
						type: 'badge',
						class: 'w-[150px]',
						badgeMap: {
							administrativo: { text: 'Administrativo', variant: 'secondary' },
							ambiental: { text: 'Ambiental', variant: 'secondary' },
							civel: { text: 'Cível', variant: 'secondary' },
							empresarial: { text: 'Empresarial', variant: 'secondary' },
							penal: { text: 'Penal', variant: 'secondary' },
							trabalhista: { text: 'Trabalhista', variant: 'secondary' }
						}
					},
					{
						header: 'Sub-área',
						key: 'sub_area',
						class: 'w-[150px]',
						type: 'badge',
						badgeMap: SUB_AREA_BADGE_MAP
					},
					{ header: 'Partes Envolvidas', key: 'atendidos', type: 'array', class: 'w-[250px]' },
					{ header: 'Data de Criação', key: 'data_criacao', type: 'datetime', class: 'w-[150px]' },
					{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' }
				]}
				actions={{
					class: 'w-[120px] text-right',
					buttons: [
						{
							title: 'Visualizar',
							href: (o) => `/plantao/orientacoes-juridicas/${o.id}`,
							icon: Eye
						},
						{
							title: 'Editar',
							href: (o) => `/plantao/orientacoes-juridicas/${o.id}/editar`,
							icon: Edit
						},
						{
							title: 'Desativar',
							icon: Trash2,
							show: (o) => o.status && isAdmin,
							onClick: async (o) => {
								await handleDelete(o.id);
							},
							class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
						}
					]
				}}
			/>
		</div>
	</div>
</div>
