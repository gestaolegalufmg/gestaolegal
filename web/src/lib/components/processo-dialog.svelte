<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import ProcessoForm from '$lib/forms/processo-form.svelte';
	import type { Processo } from '$lib/types';
	import type { Infer, SuperValidated } from 'sveltekit-superforms';
	import type { ProcessoCreateFormSchema } from '$lib/forms/schemas/processo-schema';
	import { toISODateInput } from '$lib/utils/date';

	let {
		casoId,
		processo,
		formData,
		open = $bindable(false),
		onSuccess
	}: {
		casoId: number;
		formData: SuperValidated<Infer<ProcessoCreateFormSchema>>;
		processo?: Processo;
		open?: boolean;
		onSuccess?: () => void | Promise<void>;
	} = $props();

	const isEditMode = $derived(!!processo);

	// When editing, seed the form with the existing processo's values. Dates come
	// from the API as GMT strings and must be normalised to ISO for the inputs.
	const seededForm = $derived(
		processo
			? {
					...formData,
					data: {
						...formData.data,
						especie: processo.especie,
						numero: processo.numero ?? null,
						identificacao: processo.identificacao ?? null,
						vara: processo.vara ?? null,
						link: processo.link ?? null,
						probabilidade: processo.probabilidade ?? null,
						posicao_assistido: processo.posicao_assistido ?? null,
						valor_causa_inicial: processo.valor_causa_inicial ?? null,
						valor_causa_atual: processo.valor_causa_atual ?? null,
						data_distribuicao: toISODateInput(processo.data_distribuicao) ?? null,
						data_transito_em_julgado: toISODateInput(processo.data_transito_em_julgado) ?? null,
						obs: processo.obs ?? null,
						status: processo.status ?? true
					}
				}
			: formData
	);

	async function handleSuccess() {
		open = false;
		await onSuccess?.();
	}
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
			{#key `${processo?.id ?? 'novo'}-${open}`}
				<ProcessoForm
					data={seededForm}
					isCreateMode={!isEditMode}
					{casoId}
					processoId={processo?.id}
					onUpdate={handleSuccess}
					onCancel={() => (open = false)}
				/>
			{/key}
		</div>
	</Dialog.Content>
</Dialog.Root>
