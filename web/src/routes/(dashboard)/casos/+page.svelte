<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import {
		SITUACAO_DEFERIMENTO_BADGE_MAP,
		SITUACAO_DEFERIMENTO_OPTIONS
	} from '$lib/constants/situacao-deferimento';
	import { AREA_BADGE_MAP } from '$lib/constants';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { usePaginatedFilters } from '$lib';

	let { data }: PageProps = $props();
	const { data: casos, me } = $derived(data);

	const situacaoFilterOptions = [
		{ value: 'todos', label: 'Todos' },
		...SITUACAO_DEFERIMENTO_OPTIONS
	];

	type CasoFilters = {
		search: string;
		show_inactive: boolean;
		situacao_deferimento: string;
		user: string;
	};

	const { filters, applyFilters, setFilters } = usePaginatedFilters<CasoFilters>({
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			situacao_deferimento: page.url.searchParams.get('situacao_deferimento') ?? 'todos',
			user: page.url.searchParams.get('user') ?? ''
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			situacao_deferimento: f.situacao_deferimento,
			user: f.user
		})
	});

	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await api.delete(`caso/${id}`);

		applyFilters();
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
							bind:value={filters.search}
							ondebounceinput={() => {
								setFilters({ search: filters.search });
								applyFilters();
							}}
							debounceMs={500}
							placeholder="Buscar casos..."
						/>
						<Select.Root
							bind:value={filters.situacao_deferimento}
							name="situacao_deferimento"
							type="single"
							onValueChange={() => applyFilters()}
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
					<div class="flex items-center gap-4">
						<label class="flex cursor-pointer items-center gap-2">
							<Checkbox
								checked={filters.user === 'me'}
								onCheckedChange={(checked) => {
									setFilters({ user: checked ? 'me' : '' });
									applyFilters();
								}}
							/>
							<span class="text-sm">Apenas meus casos</span>
						</label>
						<label class="flex cursor-pointer items-center gap-2">
							<Checkbox
								bind:checked={filters.show_inactive}
								onCheckedChange={() => applyFilters()}
							/>
							<span class="text-sm">Incluir inativos</span>
						</label>
					</div>
				</div>
			</div>

			<DataTable
				data={casos}
				onPageChange={(page) => applyFilters({ page })}
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
					{ header: 'Data', key: 'data_criacao', type: 'datetime', class: 'w-[150px]' },
					{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' }
				]}
				actions={{
					class: 'w-[180px] text-right',
					buttons: [
						{ title: 'Visualizar', href: (c) => `/casos/${c.id}`, icon: Eye },
						{ title: 'Editar', href: (c) => `/casos/${c.id}/editar`, icon: Edit },
						{
							title: 'Desativar',
							icon: Trash2,
							show: (c) => c.status && isAdmin,
							onClick: async (c) => {
								await handleDelete(c.id);
							},
							confirm: {
								title: 'Desativar caso?',
								description:
									'O caso será inativado. Você poderá reativá-lo depois exibindo os registros inativos.',
								confirmText: 'Desativar'
							},
							class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
						}
					]
				}}
			/>
		</div>
	</div>
</div>
