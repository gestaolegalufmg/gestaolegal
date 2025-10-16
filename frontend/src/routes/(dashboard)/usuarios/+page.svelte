<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DataTable from '$lib/components/data-table.svelte';
	import { useDebounce } from 'runed';
	import { superForm } from 'sveltekit-superforms';
	import type { PageProps } from './$types';
	import { SimpleInput, SimpleSelect, FilterCheckbox } from '$lib/components/forms';
	import { goto, invalidate } from '$app/navigation';
	import Eye from '@lucide/svelte/icons/eye';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { USER_ROLE_OPTIONS, USER_ROLE_BADGE_MAP } from '$lib/constants';

	let { data }: PageProps = $props();
	const { me, formData: initialFormData } = data;

	let tableData = $derived(data.users);
	const roleFilterOptions = [{ value: 'all', label: 'Todos' }, ...USER_ROLE_OPTIONS];

	let formRef = $state<HTMLFormElement | null>(null);

	let handleSearch = useDebounce(() => {
		form.submit(formRef);
	}, 500);

	let form = superForm(initialFormData, { onChange: handleSearch });

	let { form: formData } = form;
	const canManageUsers = $derived(data.canManageUsers ?? me.urole === 'admin');
</script>

<div class="space-y-6">
	<div class="flex justify-between items-center">
		<h1 class="text-3xl font-bold tracking-tight">Gestão de Usuários</h1>
		{#if canManageUsers}
			<Button href="/usuarios/novo-usuario">Novo Usuário</Button>
		{/if}
	</div>

	{#if canManageUsers}
		<div class="grid gap-6">
			<div class="bg-card rounded-lg border p-6 overflow-auto">
				<div class="flex justify-between items-center mb-4">
					<form
						method="GET"
						action="/usuarios"
						class="flex w-full align-center justify-between gap-2"
						bind:this={formRef}
						data-sveltekit-keepfocus
						data-sveltekit-replacestate
						data-sveltekit-noscroll
					>
						<div class="flex items-center gap-2">
							<SimpleInput
								label="Buscar"
								name="search"
								{form}
								bind:value={$formData.search}
								placeholder="Buscar usuários..."
							/>
							<SimpleSelect
								bind:value={$formData.funcao}
								{form}
								name="funcao"
								options={roleFilterOptions}
								placeholder="Função"
								label="Função"
							/>
						</div>
						<FilterCheckbox
							{form}
							value={$formData.show_inactive.toString()}
							label="Incluir inativos"
							name="show_inactive"
							bind:checked={$formData.show_inactive}
						/>
					</form>
				</div>

				<DataTable
					data={tableData}
					onPageChange={(page) => {
						const currentSearchParams = new URLSearchParams(window.location.search);
						currentSearchParams.set('page', page.toString());
						goto(`/usuarios?${currentSearchParams.toString()}`, {
							replaceState: true,
							keepFocus: true,
							noScroll: true,
							invalidateAll: true
						});
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
									await fetch(`/api/user/${u.id}`, { method: 'DELETE' });
									await invalidate('app:usuarios');
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
