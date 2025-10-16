<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import type { ListCaso } from '$lib/types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import {
		SITUACAO_DEFERIMENTO,
		SITUACAO_DEFERIMENTO_BADGE_MAP,
		SITUACAO_DEFERIMENTO_OPTIONS
	} from '$lib/constants/situacao-deferimento';
	import { AREA_BADGE_MAP } from '$lib/constants';
	import IndeferirCasoDialog from '$lib/components/indeferir-caso-dialog.svelte';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { createPaginatedList } from '$lib';

	let { data }: PageProps = $props();
	const { me } = data;

	const situacaoFilterOptions = [
		{ value: 'todos', label: 'Todos' },
		...SITUACAO_DEFERIMENTO_OPTIONS
	];

	let indeferirDialogOpen = $state(false);
	let casoToIndeferir = $state<number | null>(null);

	type CasoFilters = {
		search: string;
		show_inactive: boolean;
		situacao_deferimento: string;
	};

	const { tableData, filters, loadData, setFilters } = createPaginatedList<ListCaso, CasoFilters>({
		endpoint: 'caso',
		initialData: data.casos,
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			situacao_deferimento: page.url.searchParams.get('situacao_deferimento') ?? 'todos'
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			situacao_deferimento: f.situacao_deferimento
		})
	});

	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await api.delete(`caso/${id}`);

		await loadData(filters, 1);
	}

	async function handleDeferir(id: number) {
		const response = await api.patch(`caso/${id}/deferir`);

		if (!response.ok) {
			console.error('Failed to defer caso:', response.statusText);
			return;
		}

		await loadData(filters, 1);
	}

	function openIndeferirDialog(id: number) {
		casoToIndeferir = id;
		indeferirDialogOpen = true;
	}

	async function handleIndeferir(justificativa: string) {
		if (!casoToIndeferir) return;

		const response = await api.patch(`caso/${casoToIndeferir}/indeferir`, {
			justif_indeferimento: justificativa
		});

		if (!response.ok) {
			console.error('Failed to indefer caso:', response.statusText);
			return;
		}

		casoToIndeferir = null;
		await loadData(filters, 1);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold tracking-tight">Casos</h1>
		<Button variant="default" href="/casos/cadastrar-novo-caso">Novo Caso</Button>
	</div>

	<div class="grid gap-6">
		<div class="rounded-lg border bg-card p-6">
			<div class="mb-4 flex items-center justify-between">
				<div class="align-center flex w-full justify-between gap-2">
					<div class="flex items-center gap-2">
						<Input
							value={filters.search}
							oninput={(e) =>
								setFilters({ ...filters, search: (e.target as HTMLInputElement).value })}
							placeholder="Buscar casos..."
						/>
						<Select.Root
							bind:value={filters.situacao_deferimento}
							name="situacao_deferimento"
							type="single"
						>
							<Select.Trigger class="w-[200px] data-[placeholder]:text-foreground">
								{situacaoFilterOptions.find(
									(option) => option.value === filters.situacao_deferimento
								)?.label}
							</Select.Trigger>
							<Select.Content>
								{#each situacaoFilterOptions as option}
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
				data={tableData}
				onPageChange={(p) => {
					void loadData(filters, p);
				}}
				columns={[
					{ header: 'ID', key: 'id', class: 'w-[100px]' },
					{
						header: 'Área do Direito',
						key: 'area_direito',
						type: 'badge',
						class: 'w-[200px]',
						badgeMap: AREA_BADGE_MAP
					},
					{ header: 'Responsável', key: 'usuario_responsavel.nome', class: 'w-[200px]' },
					{
						header: 'Situação',
						key: 'situacao_deferimento',
						class: 'w-[150px]',
						badgeMap: SITUACAO_DEFERIMENTO_BADGE_MAP,
						type: 'badge'
					},
					{ header: 'Data', key: 'data_criacao', type: 'date', class: 'w-[120px]' },
					{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' }
				]}
				actions={{
					class: 'w-[180px] text-right',
					buttons: [
						{ title: 'Visualizar', href: (c) => `/casos/${c.id}`, icon: Eye },
						{ title: 'Editar', href: (c) => `/casos/${c.id}/editar`, icon: Edit },
						{
							title: 'Deferir',
							icon: Check,
							show: (c) =>
								c.situacao_deferimento === SITUACAO_DEFERIMENTO.AGUARDANDO_DEFERIMENTO &&
								!!c.status,
							onClick: async (c) => {
								await handleDeferir(c.id);
							},
							class: 'h-8 w-8 p-0 text-green-600 hover:text-green-700',
							variant: 'ghost'
						},
						{
							title: 'Indeferir',
							icon: X,
							show: (c) =>
								c.situacao_deferimento === SITUACAO_DEFERIMENTO.AGUARDANDO_DEFERIMENTO &&
								!!c.status,
							onClick: (c) => {
								openIndeferirDialog(c.id);
							},
							class: 'h-8 w-8 p-0 text-orange-600 hover:text-orange-700',
							variant: 'ghost'
						},
						{
							title: 'Desativar',
							icon: Trash2,
							show: (c) => c.status && isAdmin,
							onClick: async (c) => {
								await handleDelete(c.id);
							},
							class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
						}
					]
				}}
			/>
		</div>
	</div>
</div>

<IndeferirCasoDialog
	bind:open={indeferirDialogOpen}
	onConfirm={handleIndeferir}
	title="Indeferir Caso"
	description="Por favor, informe a justificativa para o indeferimento deste caso."
/>
