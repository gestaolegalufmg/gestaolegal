<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { assistidoCreateFormSchema } from './schemas/assistido-schema';
	import { SimpleInput, SimpleSelect, SimpleTextArea } from '$lib/components/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	let {
		data,
		atendidoId,
		onError,
		onUpdate,
		isAssistido = false
	}: {
		data: any;
		atendidoId?: number;
		onError?: (error: any) => void;
		onUpdate?: (responseData: any) => void;
		isAssistido?: boolean;
	} = $props();

	const form = superForm(data, {
		SPA: true,
		validators: zod4Client(assistidoCreateFormSchema),
		onSubmit: async ({ formData }) => {
			const data = Object.fromEntries(formData);

			try {
				// When editing an assistido (isAssistido=true), we update via the assistido endpoint
				// Otherwise, we're creating a new assistido (tornar assistido)
				const response = isAssistido
					? await api.put(`atendido/${atendidoId}/assistido`, data)
					: await api.post(`atendido/${atendidoId}/tornar-assistido`, data);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar assistido');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(
					isAssistido
						? 'Assistido atualizado com sucesso!'
						: 'Atendido convertido em assistido com sucesso!'
				);

				// Use custom onUpdate callback if provided, otherwise default redirect
				if (onUpdate) {
					onUpdate(responseData);
				} else {
					goto('/plantao/atendidos-assistidos');
				}
			} catch (error) {
				console.error('Assistido form error:', error);
				toast.error('Erro ao salvar assistido. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = form;

	let showBeneficioDetails = $derived(
		$formData.beneficio && $formData.beneficio !== 'nao' && $formData.beneficio !== 'nao_info'
	);
	let showVeiculosDetails = $derived($formData.possui_veiculos);
	let showDoencaDetails = $derived($formData.doenca_grave_familia === 'sim');
	let showImoveisQuantidade = $derived($formData.possui_outros_imoveis);
</script>

<form method="POST" use:enhance class="space-y-6">
	<Card.Root>
		<Card.Header>
			<Card.Title>Dados Pessoais</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<SimpleSelect
				label="Sexo"
				name="sexo"
				{form}
				bind:value={$formData.sexo}
				options={[
					{ value: 'M', label: 'Masculino' },
					{ value: 'F', label: 'Feminino' },
					{ value: 'O', label: 'Outro' }
				]}
				placeholder="Selecione"
			/>

			<SimpleInput
				label="RG"
				name="rg"
				{form}
				bind:value={$formData.rg}
				placeholder="Digite o RG"
			/>

			<SimpleInput
				label="Profissão"
				name="profissao"
				{form}
				bind:value={$formData.profissao}
				placeholder="Digite a profissão"
			/>

			<SimpleSelect
				label="Raça/Cor"
				name="raca"
				{form}
				bind:value={$formData.raca}
				options={[
					{ value: 'indigena', label: 'Indígena' },
					{ value: 'preta', label: 'Preta' },
					{ value: 'parda', label: 'Parda' },
					{ value: 'amarela', label: 'Amarela' },
					{ value: 'branca', label: 'Branca' },
					{ value: 'nao_declarado', label: 'Prefere não declarar' }
				]}
				placeholder="Selecione"
			/>

			<SimpleSelect
				label="Grau de Instrução"
				name="grau_instrucao"
				{form}
				bind:value={$formData.grau_instrucao}
				options={[
					{ value: 'nao_frequentou', label: 'Não frequentou a escola' },
					{ value: 'infantil_inc', label: 'Educação infantil incompleta' },
					{ value: 'infantil_comp', label: 'Educação infantil completa' },
					{ value: 'fundamental1_inc', label: 'Fundamental 1° ao 5° ano incompleto' },
					{ value: 'fundamental1_comp', label: 'Fundamental 1° ao 5° ano completo' },
					{ value: 'fundamental2_inc', label: 'Fundamental 6° ao 9° ano incompleto' },
					{ value: 'fundamental2_comp', label: 'Fundamental 6° ao 9° ano completo' },
					{ value: 'medio_inc', label: 'Ensino médio incompleto' },
					{ value: 'medio_comp', label: 'Ensino médio completo' },
					{ value: 'tecnico_inc', label: 'Curso técnico incompleto' },
					{ value: 'tecnico_comp', label: 'Curso técnico completo' },
					{ value: 'superior_inc', label: 'Ensino superior incompleto' },
					{ value: 'superior_comp', label: 'Ensino superior completo' },
					{ value: 'nao_info', label: 'Não informou' }
				]}
				placeholder="Selecione"
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Informações Financeiras</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4 md:grid-cols-2">
			<SimpleInput
				label="Salário (R$)"
				name="salario"
				type="number"
				{form}
				bind:value={$formData.salario}
				placeholder="0.00"
			/>

			<SimpleInput
				label="Renda Familiar (R$)"
				name="renda_familiar"
				type="number"
				{form}
				bind:value={$formData.renda_familiar}
				placeholder="0.00"
			/>

			<SimpleSelect
				label="Benefício"
				name="beneficio"
				{form}
				bind:value={$formData.beneficio}
				options={[
					{ value: 'ben_prestacao_continuada', label: 'Benefício de prestação continuada' },
					{ value: 'renda_basica', label: 'Renda Básica' },
					{ value: 'bolsa_escola', label: 'Bolsa escola' },
					{ value: 'bolsa_moradia', label: 'Bolsa moradia' },
					{ value: 'cesta_basica', label: 'Cesta básica' },
					{ value: 'valegas', label: 'Vale Gás' },
					{ value: 'nao', label: 'Não' },
					{ value: 'outro', label: 'Outro' },
					{ value: 'nao_info', label: 'Não informou' }
				]}
				placeholder="Selecione"
			/>

			{#if showBeneficioDetails}
				<SimpleInput
					label="Qual benefício?"
					name="qual_beneficio"
					{form}
					bind:value={$formData.qual_beneficio}
					placeholder="Especifique"
				/>
			{/if}

			<SimpleSelect
				label="Contribui com INSS?"
				name="contribui_inss"
				{form}
				bind:value={$formData.contribui_inss}
				options={[
					{ value: 'sim', label: 'Sim' },
					{ value: 'enq_trabalhava', label: 'Enquanto trabalhava' },
					{ value: 'nao', label: 'Não' },
					{ value: 'nao_info', label: 'Não informou' }
				]}
				placeholder="Selecione"
			/>

			<SimpleSelect
				label="Participação na Renda"
				name="participacao_renda"
				{form}
				bind:value={$formData.participacao_renda}
				options={[
					{ value: 'principal', label: 'Principal responsável' },
					{ value: 'contribuinte', label: 'Contribuinte' },
					{ value: 'dependente', label: 'Dependente' }
				]}
				placeholder="Selecione"
			/>

			<SimpleInput
				label="Quantidade de Pessoas na Moradia"
				name="qtd_pessoas_moradia"
				type="number"
				{form}
				bind:value={$formData.qtd_pessoas_moradia}
				placeholder="1"
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Moradia e Patrimônio</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<SimpleSelect
				label="Tipo de Moradia"
				name="tipo_moradia"
				{form}
				bind:value={$formData.tipo_moradia}
				options={[
					{ value: 'propria_quitada', label: 'Própria quitada' },
					{ value: 'propria_financiada', label: 'Própria financiada' },
					{ value: 'moradia_cedida', label: 'Cedida' },
					{ value: 'ocupada_irregular', label: 'Ocupada/Irregular' },
					{ value: 'em_construcao', label: 'Em construção' },
					{ value: 'alugada', label: 'Alugada' },
					{ value: 'parentes_amigos', label: 'Casa de parentes ou amigos' },
					{ value: 'situacao_rua', label: 'Situação de rua' }
				]}
				placeholder="Selecione"
			/>

			<div class="flex items-center space-x-2">
				<input
					type="checkbox"
					id="possui_outros_imoveis"
					bind:checked={$formData.possui_outros_imoveis}
					class="h-4 w-4 rounded border-gray-300"
				/>
				<label
					for="possui_outros_imoveis"
					class="text-sm leading-none font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
				>
					Possui outros imóveis?
				</label>
			</div>

			{#if showImoveisQuantidade}
				<SimpleInput
					label="Quantos imóveis?"
					name="quantos_imoveis"
					type="number"
					{form}
					bind:value={$formData.quantos_imoveis}
					placeholder="0"
				/>
			{/if}

			<div class="flex items-center space-x-2">
				<input
					type="checkbox"
					id="possui_veiculos"
					bind:checked={$formData.possui_veiculos}
					class="h-4 w-4 rounded border-gray-300"
				/>
				<label
					for="possui_veiculos"
					class="text-sm leading-none font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
				>
					Possui veículos?
				</label>
			</div>

			{#if showVeiculosDetails}
				<div class="grid gap-4 border-l-4 border-primary pl-4 md:grid-cols-2">
					<SimpleInput
						label="Quantos veículos?"
						name="quantos_veiculos"
						type="number"
						{form}
						bind:value={$formData.quantos_veiculos}
						placeholder="0"
					/>

					<SimpleInput
						label="Ano do(s) veículo(s)"
						name="ano_veiculo"
						{form}
						bind:value={$formData.ano_veiculo}
						placeholder="Ex: 2020, 2018"
					/>

					<div class="md:col-span-2">
						<SimpleTextArea
							label="Observações sobre veículos"
							name="possui_veiculos_obs"
							{form}
							bind:value={$formData.possui_veiculos_obs}
							placeholder="Marca, modelo, estado, etc..."
						/>
					</div>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Saúde</Card.Title>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<SimpleSelect
				label="Há doença grave na família?"
				name="doenca_grave_familia"
				{form}
				bind:value={$formData.doenca_grave_familia}
				options={[
					{ value: 'sim', label: 'Sim' },
					{ value: 'nao', label: 'Não' }
				]}
				placeholder="Selecione"
			/>

			{#if showDoencaDetails}
				<div class="grid gap-4 border-l-4 border-destructive pl-4 md:grid-cols-2">
					<SimpleSelect
						label="Quem é a pessoa doente?"
						name="pessoa_doente"
						{form}
						bind:value={$formData.pessoa_doente}
						options={[
							{ value: 'propria_pessoa', label: 'Própria pessoa' },
							{ value: 'companheira_companheiro', label: 'Cônjuge ou Companheiro(a)' },
							{ value: 'filhos', label: 'Filhos' },
							{ value: 'pais', label: 'Pais' },
							{ value: 'avos', label: 'Avós' },
							{ value: 'sogros', label: 'Sogros' },
							{ value: 'outros', label: 'Outros' }
						]}
						placeholder="Selecione"
					/>

					<SimpleInput
						label="Gastos com Medicação (R$)"
						name="gastos_medicacao"
						type="number"
						{form}
						bind:value={$formData.gastos_medicacao}
						placeholder="0.00"
					/>

					<div class="md:col-span-2">
						<SimpleTextArea
							label="Observações sobre a doença"
							name="pessoa_doente_obs"
							{form}
							bind:value={$formData.pessoa_doente_obs}
							placeholder="Detalhes sobre a doença, tratamento, etc..."
						/>
					</div>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Observações Gerais</Card.Title>
		</Card.Header>
		<Card.Content>
			<SimpleTextArea
				label="Observações"
				name="obs"
				{form}
				bind:value={$formData.obs}
				placeholder="Observações gerais sobre o assistido..."
			/>
		</Card.Content>
	</Card.Root>

	{#if isAssistido}
		<input type="hidden" name="isAssistido" value="true" />
	{/if}

	<div class="flex justify-end gap-4">
		<Button type="button" variant="outline" href="/plantao/atendidos-assistidos">Cancelar</Button>
		<Button type="submit">Salvar {isAssistido ? 'Alterações' : 'Assistido'}</Button>
	</div>
</form>
