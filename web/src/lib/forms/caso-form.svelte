<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Button } from '$lib/components/ui/button';
	import { FormSection, SimpleSelect, SimpleTextArea } from '$lib/components/forms';
	import { casoCreateFormSchema } from './schemas/caso-schema';
	import { intProxy, superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import {
		AREA_DIREITO,
		AREA_DIREITO_OPTIONS,
		SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS,
		SUB_AREA_DIREITO_CIVEL_OPTIONS
	} from '$lib/constants/area_direito';
	import { SITUACAO_DEFERIMENTO_OPTIONS } from '$lib/constants/situacao-deferimento';
	import type { User, Atendido } from '$lib/types';
	import AssistidoSelectorDialog from '$lib/components/assistido-selector-dialog.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import X from '@lucide/svelte/icons/x';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { get } from 'svelte/store';

	let {
		data,
		onUpdate,
		onError,
		isCreateMode = false,
		casoId,
		usuarios = [],
		assistidos = []
	}: {
		data: SuperValidated<Infer<typeof casoCreateFormSchema>>;
		isCreateMode?: boolean;
		casoId?: number;
		onUpdate?: (data: any) => void;
		onError?: (error: any) => void;
		usuarios?: User[];
		assistidos?: Atendido[];
	} = $props();

	const casoForm = superForm(data, {
		SPA: true,
		dataType: 'json',
		validators: zod4Client(casoCreateFormSchema),
		resetForm: false,
		taintedMessage: 'Tem certeza que deseja sair? Você perderá qualquer alteração não salva.',
		onSubmit: async () => {
			const rawData = get(formData);
			const payload =
				typeof structuredClone === 'function'
					? structuredClone(rawData)
					: JSON.parse(JSON.stringify(rawData));

			try {
				const response = isCreateMode
					? await api.post('caso', payload)
					: await api.put(`caso/${casoId}`, payload);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar caso');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(isCreateMode ? 'Caso criado com sucesso!' : 'Caso atualizado com sucesso!');

				// Use custom onUpdate callback if provided
				if (onUpdate) {
					onUpdate(responseData);
				} else {
					goto(`/casos/${responseData.id}`);
				}
			} catch (error) {
				console.error('Caso form error:', error);
				toast.error('Erro ao salvar caso. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = casoForm;

	const usuariosOptions = $derived(
		usuarios.map((u) => ({ value: u.id.toString(), label: u.nome }))
	);

	const usuarioProxy = intProxy(formData, 'id_usuario_responsavel');

	let selectedAssistidos = $state<Atendido[]>(assistidos || []);

	function handleAssistidosSelected(newAssistidos: Atendido[]) {
		selectedAssistidos = newAssistidos;
		$formData.ids_clientes = newAssistidos.map((a) => a.id);
	}

	function removeAssistido(assistidoId: number) {
		selectedAssistidos = selectedAssistidos.filter((a) => a.id !== assistidoId);
		$formData.ids_clientes = selectedAssistidos.map((a) => a.id);
	}
</script>

<form method="POST" use:enhance class="space-y-8">
	<FormSection title="Dados do Caso" description="Informações principais sobre o caso" columns="2">
		<SimpleSelect
			label="Área do Direito"
			name="area_direito"
			form={casoForm}
			bind:value={$formData.area_direito}
			options={AREA_DIREITO_OPTIONS}
			placeholder="Selecione a área do direito"
		/>

		{#if $formData.area_direito === AREA_DIREITO.ADMINISTRATIVO}
			<SimpleSelect
				label="Sub-área"
				name="sub_area"
				form={casoForm}
				bind:value={$formData.sub_area}
				options={SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS}
			/>
		{/if}
		{#if $formData.area_direito === AREA_DIREITO.CIVEL}
			<SimpleSelect
				label="Sub-área"
				name="sub_area"
				form={casoForm}
				bind:value={$formData.sub_area}
				options={SUB_AREA_DIREITO_CIVEL_OPTIONS}
			/>
		{/if}

		<SimpleSelect
			label="Situação do Deferimento"
			name="situacao_deferimento"
			form={casoForm}
			bind:value={$formData.situacao_deferimento}
			options={SITUACAO_DEFERIMENTO_OPTIONS}
			placeholder="Selecione a situação"
		/>
	</FormSection>

	<FormSection title="Assistidos" description="Selecione os assistidos para este caso" columns="1">
		<div class="space-y-4">
			<AssistidoSelectorDialog
				form={casoForm}
				name="ids_clientes"
				bind:selectedAssistidosIds={$formData.ids_clientes}
				onSelect={handleAssistidosSelected}
			>
				{#snippet trigger()}
					<UserPlus class="mr-2 h-4 w-4" />
					Adicionar Assistidos
				{/snippet}
			</AssistidoSelectorDialog>

			{#if selectedAssistidos.length > 0}
				<div class="space-y-2">
					<p class="text-sm font-medium">
						{selectedAssistidos.length} assistido(s) selecionado(s):
					</p>
					<div class="flex flex-wrap gap-2">
						{#each selectedAssistidos as assistido (assistido.id)}
							<Badge variant="secondary" class="py-1 pr-1 pl-3">
								<span class="mr-2">{assistido.nome}</span>
								<Button
									variant="ghost"
									size="sm"
									class="h-4 w-4 p-0 hover:bg-transparent"
									onclick={() => removeAssistido(assistido.id)}
									type="button"
								>
									<X class="h-3 w-3" />
								</Button>
							</Badge>
						{/each}
					</div>
				</div>
			{:else}
				<p class="text-sm text-muted-foreground">Nenhum assistido selecionado</p>
			{/if}
		</div>
	</FormSection>

	<FormSection title="Responsáveis" description="Defina os responsáveis pelo caso" columns="2">
		<SimpleSelect
			label="Usuário Responsável"
			name="id_usuario_responsavel"
			form={casoForm}
			bind:value={$usuarioProxy}
			options={usuariosOptions}
			placeholder="Selecione o responsável"
		/>

		<SimpleSelect
			label="Orientador"
			name="id_orientador"
			form={casoForm}
			bind:value={$formData.id_orientador}
			options={usuariosOptions}
			placeholder="Selecione o orientador (opcional)"
		/>

		<SimpleSelect
			label="Estagiário"
			name="id_estagiario"
			form={casoForm}
			bind:value={$formData.id_estagiario}
			options={usuariosOptions}
			placeholder="Selecione o estagiário (opcional)"
		/>

		<SimpleSelect
			label="Colaborador"
			name="id_colaborador"
			form={casoForm}
			bind:value={$formData.id_colaborador}
			options={usuariosOptions}
			placeholder="Selecione o colaborador (opcional)"
		/>
	</FormSection>

	<FormSection title="Detalhes" description="Informações adicionais do caso" columns="1">
		<SimpleTextArea
			label="Descrição"
			name="descricao"
			form={casoForm}
			bind:value={$formData.descricao}
			placeholder="Descreva o caso..."
			rows={5}
		/>

		<SimpleTextArea
			label="Justificativa de Indeferimento"
			name="justif_indeferimento"
			form={casoForm}
			bind:value={$formData.justif_indeferimento}
			placeholder="Justificativa (se aplicável)..."
			rows={3}
		/>
	</FormSection>

	<div class="flex items-center justify-between border-t border-border pt-6">
		<Button type="button" variant="outline" href="/casos">Cancelar</Button>
		<div class="flex gap-3">
			{#if !isCreateMode}
				<Form.Button type="button" variant="outline">Visualizar</Form.Button>
			{/if}
			<Form.Button class="min-w-[140px]">
				{isCreateMode ? 'Criar Caso' : 'Salvar Alterações'}
			</Form.Button>
		</div>
	</div>
</form>
