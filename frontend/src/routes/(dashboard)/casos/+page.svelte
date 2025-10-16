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
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import {
		SITUACAO_DEFERIMENTO,
		SITUACAO_DEFERIMENTO_BADGE_MAP,
		SITUACAO_DEFERIMENTO_OPTIONS
	} from '$lib/constants/situacao-deferimento';
	import { AREA_BADGE_MAP } from '$lib/constants';
	import IndeferirCasoDialog from '$lib/components/indeferir-caso-dialog.svelte';

	let { data }: PageProps = $props();
	const { formData: initialFormData, casos, me } = data;

	const situacaoFilterOptions = [
		{ value: 'todos', label: 'Todos' },
		...SITUACAO_DEFERIMENTO_OPTIONS
	];

	let indeferirDialogOpen = $state(false);
	let casoToIndeferir = $state<number | null>(null);

	let tableData = $derived(data.casos);
	let formRef = $state<HTMLFormElement | null>(null);

	let handleSearch = useDebounce(async () => {
		const response = await fetch(
			`/api/caso?search=${$formData.search}&show_inactive=${$formData.show_inactive}&situacao_deferimento=${$formData.situacao_deferimento}`
		);
		const responseData = await response.json();

		tableData = responseData.items || responseData;

		form.submit(formRef);
	}, 500);

	let form = superForm(initialFormData, { onChange: handleSearch });

	let { form: formData } = form;
	const isAdmin = $derived(me.urole === 'admin');

	async function handleDelete(id: number) {
		if (!isAdmin) return;

		await fetch(`/api/caso/${id}`, {
			method: 'DELETE'
		});

		await invalidate('app:casos');
	}

	async function handleDeferir(id: number) {
		const response = await fetch(`/api/caso/${id}/deferir`, {
			method: 'PATCH'
		});

		if (!response.ok) {
			console.error('Failed to defer caso:', response.statusText);
			return;
		}

		await invalidate('app:casos');
	}

	function openIndeferirDialog(id: number) {
		casoToIndeferir = id;
		indeferirDialogOpen = true;
	}

	async function handleIndeferir(justificativa: string) {
		if (!casoToIndeferir) return;

		const response = await fetch(`/api/caso/${casoToIndeferir}/indeferir`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ justif_indeferimento: justificativa })
		});

		if (!response.ok) {
			console.error('Failed to indefer caso:', response.statusText);
			return;
		}

		casoToIndeferir = null;
		await invalidate('app:casos');
	}
</script>

<div class="space-y-6">
	<div class="flex justify-between items-center">
		<h1 class="text-3xl font-bold tracking-tight">Casos</h1>
		<Button variant="default" href="/casos/cadastrar-novo-caso">Novo Caso</Button>
	</div>

	<div class="grid gap-6">
		<div class="bg-card rounded-lg border p-6">
			<div class="flex justify-between items-center mb-4">
				<form
					method="GET"
					action="/casos"
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
							placeholder="Buscar casos..."
						/>
						<SimpleSelect
							bind:value={$formData.situacao_deferimento}
							{form}
							name="situacao_deferimento"
							options={situacaoFilterOptions}
							placeholder="Situação"
							label="Situação"
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
					goto(`/casos?${currentSearchParams.toString()}`, {
						replaceState: true,
						keepFocus: true,
						noScroll: true,
						invalidateAll: true
					});
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
