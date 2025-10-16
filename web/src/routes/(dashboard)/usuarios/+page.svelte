<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import type { PageProps } from './$types';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { USER_ROLE_OPTIONS, USER_ROLE_BADGE_MAP } from '$lib/constants';
	import type { User } from '$lib/types';
	import { api } from '$lib/api-client';
	import Input from '$lib/components/ui/input/input.svelte';
	import { page } from '$app/state';
	import * as Select from '$lib/components/ui/select';
	import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
	import { createPaginatedList } from '$lib';

	let { data }: PageProps = $props();
	const { me } = data;

	const roleFilterOptions = [{ value: 'all', label: 'Todos' }, ...USER_ROLE_OPTIONS];

	type UserFilters = {
		search: string;
		show_inactive: boolean;
		funcao: string;
	};

	const { tableData, filters, loadData, setFilters } = createPaginatedList<User, UserFilters>({
		endpoint: 'user',
		initialData: data.users,
		initialFilters: {
			search: page.url.searchParams.get('search') ?? '',
			show_inactive: page.url.searchParams.get('show_inactive') === 'true',
			funcao: page.url.searchParams.get('funcao') ?? 'all'
		},
		buildParams: (f) => ({
			search: f.search,
			show_inactive: f.show_inactive ? 'true' : 'false',
			funcao: f.funcao
		})
	});

	const canManageUsers = $derived(data.canManageUsers ?? me.urole === 'admin');
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold tracking-tight">Gestão de Usuários</h1>
		{#if canManageUsers}
			<Button href="/usuarios/novo-usuario">Novo Usuário</Button>
		{/if}
	</div>

	{#if canManageUsers}
		<div class="grid gap-6">
			<div class="overflow-auto rounded-lg border bg-card p-6">
				<div class="mb-4 flex items-center justify-between">
					<div class="align-center flex w-full justify-between gap-2">
						<div class="flex items-center gap-2">
							<Input
								value={filters.search}
								oninput={(e) =>
									setFilters({ ...filters, search: (e.target as HTMLInputElement).value })}
								placeholder="Buscar usuários..."
							/>
							<Select.Root bind:value={filters.funcao} name="funcao" type="single">
								<Select.Trigger class="w-[180px] data-[placeholder]:text-foreground">
									{roleFilterOptions.find((option) => option.value === filters.funcao)?.label}
								</Select.Trigger>
								<Select.Content>
									{#each roleFilterOptions as option}
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
						{ header: 'Nome', key: 'nome', class: 'w-[200px]' },
						{ header: 'Email', key: 'email', class: 'w-[250px]' },
						{
							header: 'Função',
							key: 'urole',
							type: 'badge',
							class: 'w-[120px]',
							badgeMap: USER_ROLE_BADGE_MAP
						},
						{ header: 'Status', key: 'status', type: 'status', class: 'w-[100px]' },
						{ header: 'Data de Entrada', key: 'data_entrada', type: 'date', class: 'w-[150px]' }
					]}
					actions={{
						class: 'w-[120px] text-right',
						buttons: [
							{
								title: 'Visualizar',
								href: (u) => `/usuarios/${u.id}`,
								icon: Eye
							},
							{
								title: 'Editar',
								href: (u) => `/usuarios/${u.id}/editar`,
								icon: Edit,
								show: () => canManageUsers
							},
							{
								title: 'Desativar',
								icon: Trash2,
								show: (u) => u.status && canManageUsers,
								onClick: async (u) => {
									await api.delete(`user/${u.id}`);
									await loadData(filters, 1);
								},
								class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
							}
						]
					}}
				/>
			</div>
		</div>
	{:else}
		<p class="text-muted-foreground">Você não tem permissão para visualizar usuários.</p>
	{/if}
</div>
