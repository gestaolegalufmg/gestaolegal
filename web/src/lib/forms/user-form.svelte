<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Button } from '$lib/components/ui/button';
	import {
		FormSection,
		SimpleInput,
		MaskedInput,
		SimpleSelect,
		SimpleTextArea,
		SimpleDatePicker
	} from '$lib/components/forms';
	import { userCreateFormSchema, type UserCreateFormSchema } from './schemas/user-schema';
	import { booleanProxy, superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import {
		USER_ROLE_OPTIONS,
		GENDER_OPTIONS,
		MARITAL_STATUS_OPTIONS,
		YES_NO_OPTIONS,
		BOOLEAN_OPTIONS,
		SCHOLARSHIP_TYPE_OPTIONS
	} from '$lib/constants';
	import { fetchCepData } from '$lib/utils/cep';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import { goto } from '$app/navigation';

	let {
		data,
		onUpdate,
		onError,
		isCreateMode = false,
		userId
	}: {
		data: SuperValidated<Infer<UserCreateFormSchema>>;
		isCreateMode?: boolean;
		userId?: number;
		onUpdate?: (data: SuperValidated<Infer<UserCreateFormSchema>>) => void;
		onError?: (error: any) => void;
	} = $props();

	const userForm = superForm(data, {
		SPA: true,
		validators: zod4Client(userCreateFormSchema),
		resetForm: false,
		taintedMessage: 'Tem certeza que deseja sair? Você perderá qualquer alteração não salva.',
		onSubmit: async ({ formData }) => {
			const data = Object.fromEntries(formData);

			try {
				const response = isCreateMode
					? await api.post('user', data)
					: await api.put(`user/${userId}`, data);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar usuário');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(
					isCreateMode ? 'Usuário criado com sucesso!' : 'Usuário atualizado com sucesso!'
				);
				onUpdate?.(responseData);

				// Redirect to user details page
				goto(`/usuarios/${responseData.id}`);
			} catch (error) {
				console.error('User form error:', error);
				toast.error('Erro ao salvar usuário. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const proxy = booleanProxy(userForm, 'bolsista');

	const { form: formData, enhance } = userForm;

	let isLoadingCep = $state(false);
	let addressFieldsDisabled = $state(true);
	let lastCepLookup = $state('');

	$effect(() => {
		const cep = $formData.cep;
		if (!cep) {
			addressFieldsDisabled = true;
			return;
		}

		const cleanCep = cep.replace(/\D/g, '');

		if (cleanCep.length === 8 && cleanCep !== lastCepLookup) {
			handleCepLookup(cleanCep);
		}
	});

	async function handleCepLookup(cleanCep: string) {
		if (isLoadingCep) return;

		lastCepLookup = cleanCep;
		isLoadingCep = true;
		addressFieldsDisabled = true;

		const result = await fetchCepData(cleanCep);

		isLoadingCep = false;

		if (result.success && result.data) {
			$formData.logradouro = result.data.logradouro;
			$formData.bairro = result.data.bairro;
			$formData.cidade = result.data.cidade;
			$formData.estado = result.data.estado;

			// Keep fields disabled when successfully filled
			addressFieldsDisabled = true;
			toast.success('Endereço preenchido automaticamente!');
		} else {
			// Enable fields for manual editing on error
			addressFieldsDisabled = false;
			toast.error(result.error || 'Erro ao buscar CEP. Preencha manualmente.');
		}
	}
</script>

<form method="POST" use:enhance class="space-y-8">
	<FormSection
		title="Dados de Acesso ao Sistema"
		description="Informações essenciais para acesso ao sistema"
		columns="2"
	>
		<SimpleInput
			label="Nome Completo"
			name="nome"
			form={userForm}
			bind:value={$formData.nome}
			placeholder="Digite o nome completo"
			autocomplete="name"
		/>
		<SimpleInput
			label="Email"
			name="email"
			form={userForm}
			bind:value={$formData.email}
			placeholder="Digite o email"
			autocomplete="email"
		/>
		<SimpleSelect
			label="Função"
			name="urole"
			form={userForm}
			bind:value={$formData.urole}
			options={USER_ROLE_OPTIONS}
			placeholder="Selecione a função"
		/>
	</FormSection>

	<FormSection title="Dados Pessoais" description="Informações pessoais e de contato" columns="3">
		<SimpleInput
			label="RG"
			name="rg"
			form={userForm}
			bind:value={$formData.rg}
			placeholder="Digite o RG"
		/>
		<MaskedInput
			label="CPF"
			name="cpf"
			form={userForm}
			bind:value={$formData.cpf}
			placeholder="000.000.000-00"
			maskType="cpf"
		/>
		<SimpleInput
			label="OAB"
			name="oab"
			form={userForm}
			bind:value={$formData.oab}
			placeholder="Digite a OAB"
		/>
		<SimpleSelect
			label="Sexo"
			name="sexo"
			form={userForm}
			bind:value={$formData.sexo}
			options={GENDER_OPTIONS}
			placeholder="Selecione o sexo"
		/>
		<SimpleSelect
			label="Estado Civil"
			name="estado_civil"
			form={userForm}
			bind:value={$formData.estado_civil}
			options={MARITAL_STATUS_OPTIONS}
			placeholder="Selecione o estado civil"
		/>
		<SimpleDatePicker
			label="Data de Nascimento"
			name="nascimento"
			form={userForm}
			placeholder="Selecione a data"
			bind:value={$formData.nascimento}
		/>
		<SimpleInput
			label="Profissão"
			name="profissao"
			form={userForm}
			bind:value={$formData.profissao}
			placeholder="Digite a profissão"
		/>
		<MaskedInput
			label="Telefone Fixo"
			name="telefone"
			type="tel"
			autocomplete="tel"
			form={userForm}
			bind:value={$formData.telefone}
			placeholder="(00) 0000-0000"
			maskType="phone"
		/>
		<MaskedInput
			label="Telefone Celular"
			name="celular"
			type="tel"
			autocomplete="tel"
			form={userForm}
			bind:value={$formData.celular}
			placeholder="(00) 00000-0000"
			maskType="cellphone"
		/>
	</FormSection>

	<FormSection title="Endereço" description="Informações de localização" columns="1">
		<div class="flex flex-wrap gap-4">
			<div class="w-24">
				<MaskedInput
					label="CEP"
					name="cep"
					form={userForm}
					bind:value={$formData.cep}
					placeholder="00000-000"
					maskType="cep"
				/>
			</div>
			<div class="w-64">
				<SimpleInput
					label="Logradouro"
					name="logradouro"
					form={userForm}
					bind:value={$formData.logradouro}
					placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
					disabled={addressFieldsDisabled || isLoadingCep}
				/>
			</div>
			<div class="w-24">
				<SimpleInput
					label="Número"
					name="numero"
					form={userForm}
					bind:value={$formData.numero}
					placeholder="Nº"
				/>
			</div>
		</div>
		<div class="flex flex-wrap gap-4">
			<div class="w-56">
				<SimpleInput
					label="Complemento"
					name="complemento"
					form={userForm}
					bind:value={$formData.complemento}
					placeholder="Digite o complemento"
				/>
			</div>
			<div class="w-48">
				<SimpleInput
					label="Bairro"
					name="bairro"
					form={userForm}
					bind:value={$formData.bairro}
					placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
					disabled={addressFieldsDisabled || isLoadingCep}
				/>
			</div>
			<div class="w-36">
				<SimpleInput
					label="Cidade"
					name="cidade"
					form={userForm}
					bind:value={$formData.cidade}
					placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
					disabled={addressFieldsDisabled || isLoadingCep}
				/>
			</div>
			<div class="min-w-fit">
				<SimpleInput
					label="Estado"
					name="estado"
					form={userForm}
					bind:value={$formData.estado}
					placeholder={isLoadingCep ? 'Buscando...' : 'UF'}
					disabled={addressFieldsDisabled || isLoadingCep}
				/>
			</div>
		</div>
	</FormSection>

	<FormSection
		title="Informações Acadêmicas e Profissionais"
		description="Dados relacionados ao trabalho e estudos"
		columns="3"
	>
		<SimpleDatePicker
			label="Data de Entrada"
			name="data_entrada"
			form={userForm}
			placeholder="Selecione a data"
			bind:value={$formData.data_entrada}
		/>
		<SimpleDatePicker
			label="Data de Saída"
			name="data_saida"
			form={userForm}
			placeholder="Selecione a data"
			bind:value={$formData.data_saida}
		/>
		<SimpleInput
			label="Matrícula"
			name="matricula"
			form={userForm}
			bind:value={$formData.matricula}
			placeholder="Digite a matrícula"
		/>
		<SimpleInput
			label="Horário de Atendimento"
			name="horario_atendimento"
			form={userForm}
			bind:value={$formData.horario_atendimento}
			placeholder="Digite o horário de atendimento"
		/>
		<SimpleInput
			label="Suplente"
			name="suplente"
			form={userForm}
			bind:value={$formData.suplente}
			placeholder="Digite o suplente"
		/>
		<SimpleInput
			label="Férias"
			name="ferias"
			form={userForm}
			bind:value={$formData.ferias}
			placeholder="Digite as férias"
		/>

		<SimpleSelect
			label="É bolsista?"
			name="bolsista"
			form={userForm}
			bind:value={$proxy}
			options={BOOLEAN_OPTIONS}
			placeholder="Selecione se é bolsista"
		/>
	</FormSection>

	{#if $formData.bolsista}
		<FormSection title="Informações da Bolsa" description="Informações da bolsa" columns="3">
			<SimpleSelect
				label="Tipo de Bolsa"
				name="tipo_bolsa"
				form={userForm}
				bind:value={$formData.tipo_bolsa}
				options={SCHOLARSHIP_TYPE_OPTIONS}
				placeholder="Selecione o tipo de bolsa"
			/>
			<SimpleDatePicker
				label="Data de Início da Bolsa"
				name="inicio_bolsa"
				form={userForm}
				placeholder="Selecione a data"
				bind:value={$formData.inicio_bolsa}
			/>
			<SimpleDatePicker
				label="Data de Fim da Bolsa"
				name="fim_bolsa"
				form={userForm}
				placeholder="Selecione a data"
				bind:value={$formData.fim_bolsa}
			/>
		</FormSection>
	{/if}
	<FormSection
		title="Certificado de Atuação DAJ"
		description="Informações sobre certificação e observações"
		columns="1"
	>
		<SimpleSelect
			label="Usuário faz jus ao certificado de atuação na DAJ?"
			name="cert_atuacao_DAJ"
			form={userForm}
			bind:value={$formData.cert_atuacao_DAJ}
			options={YES_NO_OPTIONS}
			placeholder="Selecione se faz jus ao certificado"
		/>
		<SimpleTextArea
			label="Observações e Fichas"
			name="obs"
			form={userForm}
			bind:value={$formData.obs}
			placeholder="Digite observações relevantes sobre o usuário..."
			rows={4}
		/>
	</FormSection>

	<div class="flex items-center justify-between border-t border-border pt-6">
		<Button type="button" variant="outline" href="/usuarios">Cancelar</Button>
		<div class="flex gap-3">
			{#if !isCreateMode}
				<Form.Button type="button" variant="outline">Visualizar</Form.Button>
			{/if}
			<Form.Button class="min-w-[140px]">
				{isCreateMode ? 'Criar Usuário' : 'Salvar Alterações'}
			</Form.Button>
		</div>
	</div>
</form>
