<script lang="ts">
	import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import {
		assistenciaJudiciariaCreateFormSchema,
		type AssistenciaJudiciariaCreateFormSchema
	} from './schemas/assistencia-judiciaria-schema';
	import { SimpleInput, SimpleSelect, MaskedInput } from '$lib/components/forms';
	import MultipleSelect from '$lib/components/forms/multiple-select.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import type { AssistenciaJudiciaria } from '$lib/types';
	import { AREA_DIREITO_OPTIONS, REGION_OPTIONS } from '$lib/constants';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import { goto } from '$app/navigation';

	let {
		data,
		isCreateMode = false,
		assistenciaId,
		onError
	}: {
		data: SuperValidated<Infer<AssistenciaJudiciariaCreateFormSchema>>;
		isCreateMode?: boolean;
		assistenciaId?: number;
		onError?: (error: any) => void;
	} = $props();

	const form = superForm(data, {
		SPA: true,
		dataType: 'json',
		validators: zod4Client(assistenciaJudiciariaCreateFormSchema),
		resetForm: false,
		onUpdate: async ({ form, result }) => {
			try {
				if (result.type === 'failure') {
					toast.error('Por favor resolva os erros de preenchimento');
					return;
				}

				const response = isCreateMode
					? await api.post<AssistenciaJudiciaria>('assistencia_judiciaria', form.data)
					: await api.put<AssistenciaJudiciaria>(
							`assistencia_judiciaria/${assistenciaId}`,
							form.data
						);

				toast.success(
					isCreateMode
						? 'Assistência judiciária criada com sucesso!'
						: 'Assistência judiciária atualizada com sucesso!'
				);

				const redirectTo = isCreateMode
					? '/plantao/assistencias-judiciarias'
					: `/plantao/assistencias-judiciarias/${response.id}`;

				await goto(redirectTo);
			} catch (error) {
				console.error('Assistencia judiciaria form error:', error);
				toast.error('Erro ao salvar assistência judiciária. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance class="space-y-6">
	<Card.Root>
		<Card.Header>
			<Card.Title>Informações da Assistência Judiciária</Card.Title>
			<Card.Description>Dados do órgão ou entidade de assistência judiciária</Card.Description>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<div class="md:col-span-2">
				<SimpleInput
					label="Nome"
					name="nome"
					{form}
					bind:value={$formData.nome}
					placeholder="Nome da assistência judiciária"
				/>
			</div>

			<SimpleSelect
				label="Região"
				name="regiao"
				{form}
				bind:value={$formData.regiao}
				options={REGION_OPTIONS}
				placeholder="Selecione a região"
			/>

			<MultipleSelect
				label="Áreas Atendidas"
				name="areas_atendidas"
				{form}
				bind:value={$formData.areas_atendidas}
				options={AREA_DIREITO_OPTIONS}
				placeholder="Selecione as áreas atendidas"
			/>

			<SimpleInput
				label="Telefone"
				name="telefone"
				{form}
				bind:value={$formData.telefone}
				placeholder="(31) 3333-3333"
			/>

			<SimpleInput
				label="E-mail"
				name="email"
				type="email"
				{form}
				bind:value={$formData.email}
				placeholder="contato@exemplo.com.br"
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Endereço</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<div class="md:col-span-2">
				<SimpleInput
					label="Logradouro"
					name="logradouro"
					{form}
					bind:value={$formData.logradouro}
					placeholder="Rua, avenida..."
				/>
			</div>
			<SimpleInput label="Número" name="numero" {form} bind:value={$formData.numero} />
			<SimpleInput
				label="Complemento"
				name="complemento"
				{form}
				bind:value={$formData.complemento}
				placeholder="Sala, andar... (opcional)"
			/>
			<SimpleInput label="Bairro" name="bairro" {form} bind:value={$formData.bairro} />
			<MaskedInput
				label="CEP"
				name="cep"
				maskType="cep"
				{form}
				bind:value={$formData.cep}
				placeholder="00000-000"
			/>
			<SimpleInput label="Cidade" name="cidade" {form} bind:value={$formData.cidade} />
			<SimpleInput label="Estado" name="estado" {form} bind:value={$formData.estado} />
		</Card.Content>
	</Card.Root>

	<div class="flex justify-end gap-4">
		<Button type="button" variant="outline" href="/plantao/assistencias-judiciarias">
			Cancelar
		</Button>
		<Button type="submit">
			{isCreateMode ? 'Criar Assistência Judiciária' : 'Salvar Alterações'}
		</Button>
	</div>
</form>
