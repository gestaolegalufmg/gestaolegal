import { z } from 'zod/v4';

const assistidoFieldsSchema = z
	.object({
		sexo: z.enum(['M', 'F', 'O'], {
			error: 'Selecione o sexo'
		}),

		profissao: z
			.string()
			.min(2, 'Profissão deve ter pelo menos 2 caracteres')
			.max(80, 'Profissão muito longa'),

		raca: z.enum(['indigena', 'preta', 'parda', 'amarela', 'branca', 'nao_declarado'], {
			error: 'Selecione a raça/cor'
		}),

		rg: z.string().min(1, 'RG é obrigatório').max(50, 'RG deve ter no máximo 50 caracteres'),

		grau_instrucao: z.enum(
			[
				'nao_frequentou',
				'infantil_inc',
				'infantil_comp',
				'fundamental1_inc',
				'fundamental1_comp',
				'fundamental2_inc',
				'fundamental2_comp',
				'medio_inc',
				'medio_comp',
				'tecnico_inc',
				'tecnico_comp',
				'superior_inc',
				'superior_comp',
				'nao_info'
			],
			{
				error: 'Selecione o grau de instrução'
			}
		),

		salario: z.number().min(0, 'Salário deve ser maior ou igual a 0'),

		beneficio: z.enum(
			[
				'ben_prestacao_continuada',
				'renda_basica',
				'bolsa_escola',
				'bolsa_moradia',
				'cesta_basica',
				'valegas',
				'nao',
				'outro',
				'nao_info'
			],
			{
				error: 'Selecione o benefício'
			}
		),

		qual_beneficio: z.string().max(30, 'Muito longo').nullish(),

		contribui_inss: z.enum(['sim', 'enq_trabalhava', 'nao', 'nao_info'], {
			error: 'Selecione se contribui com INSS'
		}),

		qtd_pessoas_moradia: z.number().min(1, 'Deve ter pelo menos 1 pessoa'),

		renda_familiar: z.number().min(0, 'Renda familiar deve ser maior ou igual a 0'),

		participacao_renda: z.enum(['principal', 'contribuinte', 'dependente'], {
			error: 'Selecione a participação na renda'
		}),

		tipo_moradia: z.enum(
			[
				'propria_quitada',
				'propria_financiada',
				'moradia_cedida',
				'ocupada_irregular',
				'em_construcao',
				'alugada',
				'parentes_amigos',
				'situacao_rua'
			],
			{
				error: 'Selecione o tipo de moradia'
			}
		),

		possui_outros_imoveis: z.boolean(),

		quantos_imoveis: z.number().min(0).nullish(),

		possui_veiculos: z.boolean(),

		possui_veiculos_obs: z.string().max(200, 'Observação muito longa').nullish(),

		quantos_veiculos: z.number().min(0).nullish(),

		ano_veiculo: z.string().max(20, 'Ano muito longo').nullish(),

		doenca_grave_familia: z.enum(['sim', 'nao'], {
			error: 'Selecione se há doença grave na família'
		}),

		pessoa_doente: z
			.enum(
				['propria_pessoa', 'companheira_companheiro', 'filhos', 'pais', 'avos', 'sogros', 'outros'],
				{
					error: 'Selecione quem é a pessoa doente'
				}
			)
			.nullish(),

		pessoa_doente_obs: z.string().max(200, 'Observação muito longa').nullish(),

		gastos_medicacao: z.number().min(0).nullish(),

		obs: z.string().max(1000, 'Observações muito longas').nullish()
	})
	.refine(
		(data) => {
			if (data.beneficio !== 'nao' && data.beneficio !== 'nao_info') {
				return !!data.qual_beneficio;
			}
			return true;
		},
		{
			message: 'Especifique qual benefício',
			path: ['qual_beneficio']
		}
	)
	.refine(
		(data) => {
			if (data.possui_outros_imoveis) {
				return data.quantos_imoveis !== null && data.quantos_imoveis !== undefined;
			}
			return true;
		},
		{
			message: 'Informe quantos imóveis possui',
			path: ['quantos_imoveis']
		}
	)
	.refine(
		(data) => {
			if (data.possui_veiculos) {
				return (
					!!data.possui_veiculos_obs &&
					data.quantos_veiculos !== null &&
					data.quantos_veiculos !== undefined &&
					!!data.ano_veiculo
				);
			}
			return true;
		},
		{
			message: 'Informe os dados dos veículos',
			path: ['possui_veiculos_obs']
		}
	)
	.refine(
		(data) => {
			if (data.doenca_grave_familia === 'sim') {
				return !!data.pessoa_doente && !!data.pessoa_doente_obs && data.gastos_medicacao !== null;
			}
			return true;
		},
		{
			message: 'Informe os dados da pessoa doente',
			path: ['pessoa_doente']
		}
	);

export const assistidoCreateFormSchema = assistidoFieldsSchema;
export const assistidoUpdateFormSchema = assistidoFieldsSchema;

export type AssistidoCreateFormSchema = typeof assistidoCreateFormSchema;
export type AssistidoCreateFormData = z.infer<typeof assistidoCreateFormSchema>;

export type AssistidoUpdateFormSchema = typeof assistidoUpdateFormSchema;
export type AssistidoUpdateFormData = z.infer<typeof assistidoUpdateFormSchema>;
