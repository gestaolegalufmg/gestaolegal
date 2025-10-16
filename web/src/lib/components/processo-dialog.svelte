<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import ProcessoForm from '$lib/forms/processo-form.svelte';
	import type { Processo } from '$lib/types';
	import type { Infer, SuperValidated } from 'sveltekit-superforms';
	import type { ProcessoCreateFormSchema } from '$lib/forms/schemas/processo-schema';

	let {
		processo,
		formData,
		open = $bindable(false)
	}: {
		formData: SuperValidated<Infer<ProcessoCreateFormSchema>>;
		processo?: Processo;
		open?: boolean;
	} = $props();

	const isEditMode = $derived(!!processo);
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-[70vw]">
		<Dialog.Header>
			<Dialog.Title>
				{isEditMode ? 'Editar Processo' : 'Novo Processo'}
			</Dialog.Title>
			<Dialog.Description>
				{isEditMode ? 'Atualize as informações do processo' : 'Adicione um novo processo ao caso'}
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-4">
			<form class="space-y-6">
				<ProcessoForm data={formData} isCreateMode={!isEditMode} />
			</form>
		</div>
	</Dialog.Content>
</Dialog.Root>
