<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Button } from '$lib/components/ui/button';
	import { FormSection, SimpleInput, SimpleSelect, SimpleTextArea } from '$lib/components/forms';
	import { processoCreateFormSchema } from './schemas/processo-schema';
	import { intProxy, superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { get } from 'svelte/store';

	let {
		data,
		onUpdate,
		onError,
		isCreateMode = true,
		casoId,
		processoId
	}: {
		data: SuperValidated<Infer<typeof processoCreateFormSchema>>;
		isCreateMode?: boolean;
		casoId?: number;
		processoId?: number;
		onUpdate?: (data: any) => void;
		onError?: (error: any) => void;
	} = $props();

	const processoForm = superForm(data, {
		SPA: true,
		validators: zod4Client(processoCreateFormSchema),
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
					? await api.post(`caso/${casoId}/processos`, payload)
					: await api.put(`caso/${casoId}/processos/${processoId}`, payload);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar processo');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(
					isCreateMode ? 'Processo criado com sucesso!' : 'Processo atualizado com sucesso!'
				);

				// Use custom onUpdate callback if provided
				if (onUpdate) {
					onUpdate(responseData);
				} else {
					goto(`/casos/${casoId}/processos/${responseData.id}`);
				}
			} catch (error) {
				console.error('Processo form error:', error);
				toast.error('Erro ao salvar processo. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = processoForm;

	const especieOptions = [
		{ value: 'Ação', label: 'Ação' },
		{ value: 'Recurso', label: 'Recurso' },
		{ value: 'Mandado de Segurança', label: 'Mandado de Segurança' },
		{ value: 'Habeas Corpus', label: 'Habeas Corpus' },
		{ value: 'Execução', label: 'Execução' },
		{ value: 'Embargos', label: 'Embargos' },
		{ value: 'Apelação', label: 'Apelação' },
		{ value: 'Agravo', label: 'Agravo' },
		{ value: 'Outros', label: 'Outros' }
	];

	const probabilidadeOptions = [
		{ value: 'Alta', label: 'Alta' },
		{ value: 'Média', label: 'Média' },
		{ value: 'Baixa', label: 'Baixa' }
	];

	const posicaoAssistidoOptions = [
		{ value: 'Autor', label: 'Autor' },
		{ value: 'Réu', label: 'Réu' },
		{ value: 'Interessado', label: 'Interessado' },
		{ value: 'Terceiro', label: 'Terceiro' }
	];

	const numeroProxy = intProxy(formData, 'numero');
	const valorCausaInicialProxy = intProxy(formData, 'valor_causa_inicial');
	const valorCausaAtualProxy = intProxy(formData, 'valor_causa_atual');
</script>

<form method="POST" use:enhance class="space-y-8">
	<FormSection
		title="Dados do Processo"
		description="Informações principais sobre o processo"
		columns="2"
	>
		<SimpleSelect
			label="Espécie"
			name="especie"
			form={processoForm}
			bind:value={$formData.especie}
			options={especieOptions}
			placeholder="Selecione a espécie"
		/>

		<SimpleInput
			label="Número"
			name="numero"
			form={processoForm}
			bind:value={$numeroProxy}
			placeholder="Número do processo"
			type="number"
		/>

		<SimpleInput
			label="Vara"
			name="vara"
			form={processoForm}
			bind:value={$formData.vara}
			placeholder="Vara responsável"
		/>

		<SimpleInput
			label="Link"
			name="link"
			form={processoForm}
			bind:value={$formData.link}
			placeholder="Link para o processo (opcional)"
		/>

		<SimpleSelect
			label="Probabilidade de Sucesso"
			name="probabilidade"
			form={processoForm}
			bind:value={$formData.probabilidade}
			options={probabilidadeOptions}
			placeholder="Selecione a probabilidade"
		/>

		<SimpleSelect
			label="Posição do Assistido"
			name="posicao_assistido"
			form={processoForm}
			bind:value={$formData.posicao_assistido}
			options={posicaoAssistidoOptions}
			placeholder="Selecione a posição"
		/>
	</FormSection>

	<FormSection title="Valores" description="Valores relacionados ao processo" columns="2">
		<SimpleInput
			label="Valor da Causa Inicial"
			name="valor_causa_inicial"
			form={processoForm}
			bind:value={$valorCausaInicialProxy}
			placeholder="Valor inicial (opcional)"
			type="number"
		/>

		<SimpleInput
			label="Valor da Causa Atual"
			name="valor_causa_atual"
			form={processoForm}
			bind:value={$valorCausaAtualProxy}
			placeholder="Valor atual (opcional)"
			type="number"
		/>
	</FormSection>

	<FormSection title="Datas" description="Datas importantes do processo" columns="2">
		<SimpleInput
			label="Data de Distribuição"
			name="data_distribuicao"
			form={processoForm}
			bind:value={$formData.data_distribuicao}
			placeholder="Data de distribuição"
			type="date"
		/>

		<SimpleInput
			label="Data de Trânsito em Julgado"
			name="data_transito_em_julgado"
			form={processoForm}
			bind:value={$formData.data_transito_em_julgado}
			placeholder="Data de trânsito em julgado"
			type="date"
		/>
	</FormSection>

	<FormSection title="Detalhes" description="Informações adicionais do processo" columns="1">
		<SimpleTextArea
			label="Identificação"
			name="identificacao"
			form={processoForm}
			bind:value={$formData.identificacao}
			placeholder="Identificação do processo..."
			rows={3}
		/>

		<SimpleTextArea
			label="Observações"
			name="obs"
			form={processoForm}
			bind:value={$formData.obs}
			placeholder="Observações adicionais..."
			rows={4}
		/>
	</FormSection>

	<div class="flex items-center justify-between border-t border-border pt-6">
		<Button type="button" variant="outline">Cancelar</Button>
		<div class="flex gap-3">
			<Form.Button class="min-w-[140px]">
				{isCreateMode ? 'Criar Processo' : 'Salvar Alterações'}
			</Form.Button>
		</div>
	</div>
</form>
