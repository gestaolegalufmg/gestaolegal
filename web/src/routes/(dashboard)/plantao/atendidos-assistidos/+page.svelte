<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import { usePaginatedFilters } from '$lib';

	let { data }: PageProps = $props();
	const { atendidos, me } = $derived(data);

	const tipoBuscaFilterOptions = [
		{ value: 'todos', label: 'Todos' },
		{ value: 'atendidos', label: 'Apenas Atendidos' },
		{ value: 'assistidos', label: 'Assistidos' }
	];

	type AtendidoFilters = {
		search: string;
		show_inactive: boolean;
		tipo_busca: string;
	};

	const { filters, applyFilters, setFilters } = usePaginatedFilters<AtendidoFilters>({
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			tipo_busca: page.url.searchParams.get('tipo_busca') ?? 'todos'
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			tipo_busca: f.tipo_busca
		})
	});

	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await api.delete(`atendido/${id}`);

		applyFilters();
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold tracking-tight">Atendidos e Assistidos</h1>
		<Button variant="default" href="/plantao/atendidos-assistidos/novo-atendido">
			Novo Atendido
		</Button>
	</div>

	<div class="grid gap-6">
		<div class="rounded-lg border bg-card p-6">
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
							placeholder="Buscar atendido..."
						/>
						<Select.Root bind:value={filters.tipo_busca} name="tipo_busca" type="single">
							<Select.Trigger class="w-full data-[placeholder]:text-foreground">
								{tipoBuscaFilterOptions.find((option) => option.value === filters.tipo_busca)
									?.label}
							</Select.Trigger>
							<Select.Content>
								{#each tipoBuscaFilterOptions as option}
									<Select.Item value={option.value}>{option.label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>
				</div>
			</div>

			<DataTable
				data={atendidos}
				onPageChange={(page) => applyFilters({ page })}
				columns={[
					{ header: 'Nome', key: 'nome', class: 'w-[200px]' },
					{ header: 'CPF', key: 'cpf', class: 'w-[120px]' },
					{ header: 'Contato', key: 'celular', class: 'w-[150px]' },
					{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' },
					{
						header: 'Tipo',
						key: 'is_assistido',
						type: 'badge',
						class: 'w-[100px]',
						badgeMap: {
							true: { text: 'Assistido', variant: 'default' },
							false: { text: 'Atendido', variant: 'outline' }
						}
					}
				]}
				actions={{
					class: 'w-[120px] text-right',
					buttons: [
						{
							title: 'Visualizar',
							href: (a) => `/plantao/atendidos-assistidos/${a.id}`,
							icon: Eye
						},
						{
							title: 'Editar',
							href: (a) => `/plantao/atendidos-assistidos/${a.id}/editar`,
							icon: Edit
						},
						{
							title: 'Tornar Assistido',
							href: (a) => `/plantao/atendidos-assistidos/${a.id}/tornar-assistido`,
							icon: UserPlus,
							show: (a) => !a.is_assistido
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
