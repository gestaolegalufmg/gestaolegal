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
	import { SUB_AREA_BADGE_MAP } from '$lib/constants';

	let { data }: PageProps = $props();
	const { formData: initialFormData, orientacoes, me } = data;

	const areaFilterOptions = [
		{ value: 'todas', label: 'Todas as Áreas' },
		{ value: 'administrativo', label: 'Administrativo' },
		{ value: 'ambiental', label: 'Ambiental' },
		{ value: 'civel', label: 'Cível' },
		{ value: 'empresarial', label: 'Empresarial' },
		{ value: 'penal', label: 'Penal' },
		{ value: 'trabalhista', label: 'Trabalhista' }
	];

	let tableData = $derived(data.orientacoes);
	let formRef = $state<HTMLFormElement | null>(null);

	let handleSearch = useDebounce(async () => {
		const response = await fetch(
			`/api/orientacao_juridica?search=${$formData.search}&show_inactive=${$formData.show_inactive}&area=${$formData.area}`
		);
		const responseData = await response.json();

		tableData = responseData;

		form.submit(formRef);
	}, 500);

	let form = superForm(initialFormData, { onChange: handleSearch });

	let { form: formData } = form;
	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await fetch(`/api/orientacao_juridica/${id}`, {
			method: 'DELETE'
		});

		await invalidate('app:orientacoes-juridicas');
	}
</script>

<div class="space-y-6">
	<div class="flex justify-between items-center">
		<h1 class="text-3xl font-bold tracking-tight">Orientações Jurídicas</h1>
		<Button variant="default" href="/plantao/orientacoes-juridicas/nova-orientacao-juridica">
			Nova Orientação Jurídica
		</Button>
	</div>

	<div class="grid gap-6">
		<div class="bg-card rounded-lg border p-6">
			<div class="flex justify-between items-center mb-4">
				<form
					method="GET"
					action="/plantao/orientacoes-juridicas"
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
							placeholder="Buscar orientação..."
						/>
						<SimpleSelect
							bind:value={$formData.area}
							{form}
							name="area"
							options={areaFilterOptions}
							placeholder="Área"
							label="Área do Direito"
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
					goto(`/plantao/orientacoes-juridicas?${currentSearchParams.toString()}`, {
						replaceState: true,
						keepFocus: true,
						noScroll: true,
						invalidateAll: true
					});
				}}
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
