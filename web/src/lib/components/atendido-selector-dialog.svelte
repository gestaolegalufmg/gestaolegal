<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import BaseSelectorDialog from './base-selector-dialog.svelte';
	import type { Atendido } from '$lib/types';
	import type { Snippet } from 'svelte';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';

	let {
		selectedAtendidosIds = $bindable([]),
		onSelect,
		trigger,
		form,
		name = 'atendidos_ids'
	}: {
		selectedAtendidosIds?: number[];
		onSelect?: (atendidos: Atendido[]) => void;
		trigger?: Snippet;
		form?: FieldProps<T, U>['form'];
		name?: string;
	} = $props();
</script>

<BaseSelectorDialog
	bind:selectedIds={selectedAtendidosIds}
	{onSelect}
	{trigger}
	{form}
	name={name as any as U}
	apiEndpoint="atendido"
	dialogTitle="Selecionar Atendidos"
	dialogDescription="Busque e selecione os atendidos para associar a esta orientação jurídica"
	buttonText="Selecionar Atendidos"
	emptyStateText="Nenhum atendido encontrado"
	searchPlaceholder="Buscar atendido por nome, CPF..."
/>
