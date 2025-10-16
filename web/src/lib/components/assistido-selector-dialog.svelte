<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import BaseSelectorDialog from './base-selector-dialog.svelte';
	import type { Atendido } from '$lib/types';
	import type { Snippet } from 'svelte';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';

	let {
		selectedAssistidosIds = $bindable([]),
		onSelect,
		trigger,
		form,
		name = 'ids_clientes'
	}: {
		selectedAssistidosIds?: number[];
		onSelect?: (assistidos: Atendido[]) => void;
		trigger?: Snippet;
		form?: FieldProps<T, U>['form'];
		name?: string;
	} = $props();
</script>

<BaseSelectorDialog
	bind:selectedIds={selectedAssistidosIds}
	{onSelect}
	{trigger}
	{form}
	name={name as any as U}
	apiEndpoint="atendido?tipo_busca=assistidos"
	dialogTitle="Selecionar Assistidos"
	dialogDescription="Busque e selecione os assistidos para associar a este caso"
	buttonText="Selecionar Assistidos"
	emptyStateText="Nenhum assistido encontrado"
	searchPlaceholder="Buscar assistido por nome, CPF..."
/>
