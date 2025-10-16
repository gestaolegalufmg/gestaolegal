<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import BaseSelectorDialog from './base-selector-dialog.svelte';
	import type { User, Atendido } from '$lib/types';
	import type { Snippet } from 'svelte';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';

	let {
		selectedUsuarioId = $bindable(null),
		onSelect,
		trigger,
		form,
		name = 'id_usuario_responsavel'
	}: {
		selectedUsuarioId?: number | null;
		onSelect?: (usuario: User | null) => void;
		trigger?: Snippet;
		form?: FieldProps<T, U>['form'];
		name?: string;
	} = $props();

	let selectedIds = $derived(selectedUsuarioId ? [selectedUsuarioId] : []);

	function handleSelect(items: Atendido[]) {
		if (items.length > 0) {
			selectedUsuarioId = items[0].id;
			onSelect?.(items[0] as unknown as User);
		} else {
			selectedUsuarioId = null;
			onSelect?.(null);
		}
	}
</script>

<BaseSelectorDialog
	bind:selectedIds
	onSelect={handleSelect}
	{trigger}
	{form}
	name={name as any as U}
	apiEndpoint="user"
	dialogTitle="Selecionar Usuário Responsável"
	dialogDescription="Busque e selecione o usuário responsável pelo evento"
	buttonText="Selecionar Usuário"
	emptyStateText="Nenhum usuário encontrado"
	searchPlaceholder="Buscar usuário por nome, email..."
	multiSelect={false}
/>
