<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { atendidoCreateFormSchema } from './schemas/atendido-schema';
	import {
		SimpleInput,
		MaskedInput,
		SimpleSelect,
		SimpleTextArea,
		SimpleDatePicker
	} from '$lib/components/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { fetchCepData } from '$lib/utils/cep';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import { goto } from '$app/navigation';

	let {
		data,
		isCreateMode = false,
		atendidoId,
		onError,
		onUpdate,
		hideSubmitButton = false
	}: {
		data: any;
		isCreateMode?: boolean;
		atendidoId?: number;
		onError?: (error: any) => void;
		onUpdate?: (responseData: any) => void;
		hideSubmitButton?: boolean;
	} = $props();

	const form = superForm(data, {
		SPA: true,
		validators: zod4Client(atendidoCreateFormSchema),
		onSubmit: async ({ formData }) => {
			const data = Object.fromEntries(formData);

			try {
				const response = isCreateMode
					? await api.post('atendido', data)
					: await api.put(`atendido/${atendidoId}`, data);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar atendido');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(
					isCreateMode ? 'Atendido criado com sucesso!' : 'Atendido atualizado com sucesso!'
				);

				// Use custom onUpdate callback if provided, otherwise default redirect
				if (onUpdate) {
					onUpdate(responseData);
				} else {
					goto(`/plantao/atendidos-assistidos/${responseData.id}`);
				}
			} catch (error) {
				console.error('Atendido form error:', error);
				toast.error('Erro ao salvar atendido. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = form;

	let showRepresentanteLegal = $derived(
		$formData.pj_constituida === 'sim' && $formData.repres_legal === false
	);

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

		// Only trigger lookup when we have exactly 8 digits and it's different from last lookup
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

<form method="POST" use:enhance class="space-y-6">
	<Card.Root>
		<Card.Header>
			<Card.Title>Dados Pessoais</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<div class="md:col-span-2">
				<SimpleInput
					label="Nome Completo"
					name="nome"
					{form}
					bind:value={$formData.nome}
					placeholder="Digite o nome completo"
				/>
			</div>

			<SimpleDatePicker
				label="Data de Nascimento"
				name="data_nascimento"
				{form}
				bind:value={$formData.data_nascimento}
			/>

			<MaskedInput
				label="CPF"
				name="cpf"
				{form}
				bind:value={$formData.cpf}
				placeholder="000.000.000-00"
				maskType="cpf"
			/>

			<MaskedInput
				label="CNPJ (se aplicável)"
				name="cnpj"
				{form}
				bind:value={$formData.cnpj}
				placeholder="00.000.000/0000-00"
				maskType="cnpj"
			/>

			<SimpleSelect
				label="Estado Civil"
				name="estado_civil"
				{form}
				bind:value={$formData.estado_civil}
				options={[
					{ value: 'solteiro', label: 'Solteiro' },
					{ value: 'casado', label: 'Casado' },
					{ value: 'divorciado', label: 'Divorciado' },
					{ value: 'separado', label: 'Separado' },
					{ value: 'uniao', label: 'União estável' },
					{ value: 'viuvo', label: 'Viúvo' }
				]}
				placeholder="Selecione"
			/>

			<MaskedInput
				label="Telefone"
				name="telefone"
				type="tel"
				autocomplete="tel"
				{form}
				bind:value={$formData.telefone}
				placeholder="(00) 0000-0000"
				maskType="phone"
			/>

			<MaskedInput
				label="Celular"
				name="celular"
				type="tel"
				autocomplete="tel"
				{form}
				bind:value={$formData.celular}
				placeholder="(00) 00000-0000"
				maskType="cellphone"
			/>

			<SimpleInput
				label="Email"
				name="email"
				{form}
				bind:value={$formData.email}
				placeholder="email@exemplo.com"
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Endereço</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<MaskedInput
				label="CEP"
				name="cep"
				{form}
				bind:value={$formData.cep}
				placeholder="00000-000"
				maskType="cep"
			/>

			<div class="md:col-span-2">
				<SimpleInput
					label="Logradouro"
					name="logradouro"
					{form}
					bind:value={$formData.logradouro}
					placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
					disabled={addressFieldsDisabled || isLoadingCep}
				/>
			</div>

			<SimpleInput
				label="Número"
				name="numero"
				{form}
				bind:value={$formData.numero}
				placeholder="Nº"
			/>

			<SimpleInput
				label="Complemento"
				name="complemento"
				{form}
				bind:value={$formData.complemento}
				placeholder="Apto, Bloco, etc"
			/>

			<SimpleInput
				label="Bairro"
				name="bairro"
				{form}
				bind:value={$formData.bairro}
				placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
				disabled={addressFieldsDisabled || isLoadingCep}
			/>

			<SimpleInput
				label="Cidade"
				name="cidade"
				{form}
				bind:value={$formData.cidade}
				placeholder={isLoadingCep ? 'Buscando...' : 'Preencha o CEP'}
				disabled={addressFieldsDisabled || isLoadingCep}
			/>

			<SimpleInput
				label="Estado"
				name="estado"
				{form}
				bind:value={$formData.estado}
				placeholder={isLoadingCep ? 'Buscando...' : 'UF'}
				disabled={addressFieldsDisabled || isLoadingCep}
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Como Conheceu o DAJ</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<SimpleSelect
				label="Como conheceu"
				name="como_conheceu"
				{form}
				bind:value={$formData.como_conheceu}
				options={[
					{ value: 'assist', label: 'Assistidos/ex-assistidos' },
					{ value: 'integ', label: 'Integrantes/ex-integrantes da UFMG' },
					{ value: 'orgaos_pub', label: 'Órgãos públicos' },
					{ value: 'meios_com', label: 'Meios de comunicação' },
					{ value: 'nucleos', label: 'Núcleos de prática jurídica' },
					{ value: 'conhec', label: 'Amigos, familiares ou conhecidos' },
					{ value: 'outros', label: 'Outros' }
				]}
				placeholder="Selecione"
			/>

			{#if $formData.como_conheceu === 'orgaos_pub'}
				<SimpleInput
					label="Indicação do Órgão"
					name="indicacao_orgao"
					{form}
					bind:value={$formData.indicacao_orgao}
					placeholder="Qual órgão indicou?"
				/>
			{/if}

			<SimpleSelect
				label="Procurou outro local?"
				name="procurou_outro_local"
				{form}
				bind:value={$formData.procurou_outro_local}
				options={[
					{ value: 'sim', label: 'Sim' },
					{ value: 'nao', label: 'Não' }
				]}
				placeholder="Selecione"
			/>

			{#if $formData.procurou_outro_local === 'sim'}
				<SimpleInput
					label="Qual local procurou?"
					name="procurou_qual_local"
					{form}
					bind:value={$formData.procurou_qual_local}
					placeholder="Informe qual local"
				/>
			{/if}
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Informações de Pessoa Jurídica</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<SimpleSelect
				label="PJ Constituída?"
				name="pj_constituida"
				{form}
				bind:value={$formData.pj_constituida}
				options={[
					{ value: 'sim', label: 'Sim' },
					{ value: 'nao', label: 'Não' }
				]}
				placeholder="Selecione"
			/>

			{#if $formData.pj_constituida === 'sim'}
				<div class="flex items-center space-x-2">
					<input
						type="checkbox"
						id="repres_legal"
						bind:checked={$formData.repres_legal}
						class="h-4 w-4 rounded border-gray-300"
					/>
					<label
						for="repres_legal"
						class="text-sm leading-none font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
					>
						O atendido é o representante legal?
					</label>
				</div>

				{#if showRepresentanteLegal}
					<div class="grid gap-4 border-l-4 border-primary pl-4 md:grid-cols-2">
						<div class="md:col-span-2">
							<SimpleInput
								label="Nome do Representante Legal"
								name="nome_repres_legal"
								{form}
								bind:value={$formData.nome_repres_legal}
								placeholder="Nome completo"
							/>
						</div>

						<MaskedInput
							label="CPF do Representante"
							name="cpf_repres_legal"
							{form}
							bind:value={$formData.cpf_repres_legal}
							placeholder="000.000.000-00"
							maskType="cpf"
						/>

						<SimpleInput
							label="RG do Representante"
							name="rg_repres_legal"
							{form}
							bind:value={$formData.rg_repres_legal}
							placeholder="RG"
						/>

						<MaskedInput
							label="Contato do Representante"
							name="contato_repres_legal"
							type="tel"
							{form}
							bind:value={$formData.contato_repres_legal}
							placeholder="(00) 00000-0000"
							maskType="cellphone"
						/>

						<SimpleDatePicker
							label="Data de Nascimento do Representante"
							name="nascimento_repres_legal"
							{form}
							bind:value={$formData.nascimento_repres_legal}
						/>
					</div>
				{/if}
			{:else}
				<SimpleInput
					label="Pretende constituir PJ?"
					name="pretende_constituir_pj"
					{form}
					bind:value={$formData.pretende_constituir_pj}
					placeholder="Sim/Não/Talvez"
				/>
			{/if}
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Observações</Card.Title>
		</Card.Header>
		<Card.Content>
			<SimpleTextArea
				label="Observações"
				name="obs"
				{form}
				bind:value={$formData.obs}
				placeholder="Observações gerais sobre o atendido..."
			/>
		</Card.Content>
	</Card.Root>

	{#if !hideSubmitButton}
		<div class="flex justify-end gap-4">
			<Button type="button" variant="outline" href="/plantao/atendidos-assistidos">Cancelar</Button>
			<Button type="submit">
				{isCreateMode ? 'Criar Atendido' : 'Salvar Alterações'}
			</Button>
		</div>
	{/if}
</form>
