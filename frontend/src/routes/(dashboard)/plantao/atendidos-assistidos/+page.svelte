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
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import type { ListAtendido, Paginated } from '$lib/types';

	let { data }: PageProps = $props();
	const { formData: initialFormData, me } = data;

	const tipoBuscaFilterOptions = [
		{ value: 'todos', label: 'Todos' },
		{ value: 'atendidos', label: 'Apenas Atendidos' },
		{ value: 'assistidos', label: 'Assistidos' }
	];

	let tableData = $derived(data.atendidos);
	let formRef = $state<HTMLFormElement | null>(null);

	let handleSearch = useDebounce(async () => {
		const response = await fetch(
			`/api/atendido?search=${$formData.search}&show_inactive=${$formData.show_inactive}&tipo_busca=${$formData.tipo_busca}`
		);
		const responseData: Paginated<ListAtendido> = await response.json();

		tableData = responseData;

		form.submit(formRef);
	}, 500);

	let form = superForm(initialFormData, { onChange: handleSearch });

	let { form: formData } = form;
	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await fetch(`/api/atendido/${id}`, {
			method: 'DELETE'
		});

		await invalidate('app:atendidos');
	}
</script>

<div class="space-y-6">
	<div class="flex justify-between items-center">
		<h1 class="text-3xl font-bold tracking-tight">Atendidos e Assistidos</h1>
		<Button variant="default" href="/plantao/atendidos-assistidos/novo-atendido">
			Novo Atendido
		</Button>
	</div>

	<div class="grid gap-6">
		<div class="bg-card rounded-lg border p-6">
			<div class="flex justify-between items-center mb-4">
				<form
					method="GET"
					action="/plantao/atendidos-assistidos"
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
							placeholder="Buscar atendido..."
						/>
						<SimpleSelect
							bind:value={$formData.tipo_busca}
							{form}
							name="tipo_busca"
							options={tipoBuscaFilterOptions}
							placeholder="Tipo"
							label="Tipo"
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
					goto(`/plantao/atendidos-assistidos?${currentSearchParams.toString()}`, {
						replaceState: true,
						keepFocus: true,
						noScroll: true,
						invalidateAll: true
					});
				}}
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
