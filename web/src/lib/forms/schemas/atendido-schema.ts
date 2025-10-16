import { z } from 'zod/v4';
import { validateCPF } from '$lib/utils/cpf-validator';

const baseAtendidoFormSchema = z
	.object({
		nome: z
			.string()
			.min(2, 'Nome deve ter pelo menos 2 caracteres')
			.max(80, 'Nome deve ter no máximo 80 caracteres'),

		data_nascimento: z.string().nonempty('Data de nascimento é obrigatória'),

		cpf: z
			.string()
			.nonempty('CPF é obrigatório')
			.refine((cpf) => validateCPF(cpf), {
				message: 'CPF inválido'
			}),

		cnpj: z
			.string()
			.max(18, 'CNPJ deve ter no máximo 18 caracteres')
			.regex(/^\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}$/, 'CNPJ inválido')
			.nullish(),

		telefone: z.string().max(18, 'Telefone deve ter no máximo 18 caracteres').nullish(),

		celular: z
			.string()
			.max(18, 'Celular deve ter no máximo 18 caracteres')
			.nonempty('Celular é obrigatório'),

		email: z.string().email('Email inválido').max(100, 'Email muito longo'),

		estado_civil: z.enum(['solteiro', 'casado', 'divorciado', 'separado', 'uniao', 'viuvo'], {
			error: 'Selecione o estado civil'
		}),

		logradouro: z
			.string()
			.max(100, 'Logradouro deve ter no máximo 100 caracteres')
			.nonempty('Logradouro é obrigatório'),

		numero: z.string().max(8, 'Número deve ter no máximo 8 caracteres').nonempty(),

		complemento: z.string().max(100, 'Complemento deve ter no máximo 100 caracteres').nullish(),

		bairro: z
			.string()
			.max(100, 'Bairro deve ter no máximo 100 caracteres')
			.nonempty('Bairro é obrigatório'),

		cep: z.string().nonempty('CEP é obrigatório'),

		cidade: z
			.string()
			.max(100, 'Cidade deve ter no máximo 100 caracteres')
			.nonempty('Cidade é obrigatória'),

		estado: z
			.string()
			.max(50, 'Estado deve ter no máximo 50 caracteres')
			.nonempty('Estado é obrigatório'),

		como_conheceu: z.enum(
			['assist', 'integ', 'orgaos_pub', 'meios_com', 'nucleos', 'conhec', 'outros'],
			{
				error: 'Selecione como conheceu o DAJ'
			}
		),

		indicacao_orgao: z.string().max(80, 'Muito longo').nullish(),

		procurou_outro_local: z.enum(['sim', 'nao'], {
			error: 'Selecione se procurou outro local'
		}),

		procurou_qual_local: z.string().max(80, 'Muito longo').nullish(),

		obs: z.string().max(1000, 'Observações muito longas').nullish(),

		pj_constituida: z.enum(['sim', 'nao'], {
			error: 'Selecione se a PJ está constituída'
		}),

		repres_legal: z.boolean().nullish(),

		nome_repres_legal: z.string().max(80, 'Nome muito longo').nullish(),

		cpf_repres_legal: z
			.string()
			.refine(
				(cpf) => {
					if (!cpf) return true;
					return validateCPF(cpf);
				},
				{
					message: 'CPF do representante legal inválido'
				}
			)
			.nullish(),

		contato_repres_legal: z.string().max(18, 'Contato muito longo').nullish(),

		rg_repres_legal: z.string().max(50, 'RG muito longo').nullish(),

		nascimento_repres_legal: z.string().nullish(),

		pretende_constituir_pj: z.string().max(80, 'Muito longo').nullish()
	})
	.refine(
		(data) => {
			if (data.como_conheceu === 'orgaos_pub') {
				return !!data.indicacao_orgao;
			}
			return true;
		},
		{
			message: 'Indicação do órgão é obrigatória quando conheceu por órgãos públicos',
			path: ['indicacao_orgao']
		}
	)
	.refine(
		(data) => {
			if (data.procurou_outro_local === 'sim') {
				return !!data.procurou_qual_local;
			}
			return true;
		},
		{
			message: 'Informe qual local procurou',
			path: ['procurou_qual_local']
		}
	)
	.refine(
		(data) => {
			if (data.pj_constituida === 'sim') {
				return !!data.cnpj;
			}
			return true;
		},
		{
			message: 'CNPJ é obrigatório quando PJ está constituída',
			path: ['cnpj']
		}
	)
	.refine(
		(data) => {
			if (data.pj_constituida === 'sim' && data.repres_legal === false) {
				return (
					!!data.nome_repres_legal &&
					!!data.cpf_repres_legal &&
					!!data.contato_repres_legal &&
					!!data.rg_repres_legal &&
					!!data.nascimento_repres_legal
				);
			}
			return true;
		},
		{
			message: 'Dados do representante legal são obrigatórios',
			path: ['nome_repres_legal']
		}
	);

export const atendidoCreateFormSchema = baseAtendidoFormSchema;
export const atendidoUpdateFormSchema = baseAtendidoFormSchema;

export const atendidoSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false),
	tipo_busca: z.string().optional()
});

export type AtendidoCreateFormSchema = typeof atendidoCreateFormSchema;
export type AtendidoCreateFormData = z.infer<typeof atendidoCreateFormSchema>;

export type AtendidoUpdateFormSchema = typeof atendidoUpdateFormSchema;
export type AtendidoUpdateFormData = z.infer<typeof atendidoUpdateFormSchema>;

export type AtendidoSearchFormSchema = typeof atendidoSearchSchema;
