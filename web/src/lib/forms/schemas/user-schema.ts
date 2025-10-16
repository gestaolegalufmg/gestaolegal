import { z } from 'zod/v4';
import {
	USER_ROLE_VALUES,
	GENDER_VALUES,
	MARITAL_STATUS_VALUES,
	YES_NO_VALUES
} from '$lib/constants';
import { validateCPF } from '$lib/utils/cpf-validator';

const baseUserFormSchema = z
	.object({
		nome: z
			.string()
			.min(2, 'Nome deve ter pelo menos 2 caracteres')
			.max(100, 'Nome deve ter no máximo 100 caracteres'),

		email: z.email('Email inválido'),

		urole: z.enum(USER_ROLE_VALUES, {
			error: 'Selecione uma função'
		}),

		status: z.boolean().default(true),

		rg: z.string().min(1, 'RG é obrigatório').max(18, 'RG deve ter no máximo 18 caracteres'),

		cpf: z
			.string()
			.nonempty('CPF é obrigatório')
			.refine(
				(cpf) => {
					if (!cpf) return true;
					return validateCPF(cpf);
				},
				{
					message: 'CPF inválido'
				}
			),

		oab: z.string().max(30, 'OAB deve ter no máximo 30 caracteres').nullish(),

		sexo: z.enum(GENDER_VALUES, {
			error: 'Selecione o sexo'
		}),

		estado_civil: z.enum(MARITAL_STATUS_VALUES, {
			error: 'Selecione o estado civil'
		}),

		nascimento: z.string().nonempty(),

		profissao: z
			.string()
			.min(1, 'Profissão é obrigatória')
			.max(100, 'Profissão deve ter no máximo 100 caracteres'),

		telefone: z.string().nullish(),

		celular: z.string().min(1, 'Telefone celular é obrigatório'),

		logradouro: z
			.string()
			.max(200, 'Logradouro deve ter no máximo 200 caracteres')
			.nonempty('Logradouro é obrigatório'),

		numero: z
			.string()
			.min(1, 'Número é obrigatório')
			.max(20, 'Número deve ter no máximo 20 caracteres'),

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

		data_entrada: z.string().nonempty(),
		data_saida: z.string().nullish(),

		bolsista: z
			.boolean({
				error: 'Selecione se é bolsista'
			})
			.default(false),

		matricula: z.string().max(50, 'Matrícula deve ter no máximo 50 caracteres').nullish(),

		horario_atendimento: z
			.string()
			.max(200, 'Dia e horário deve ter no máximo 200 caracteres')
			.nullish(),

		suplente: z.string().max(100, 'Suplente deve ter no máximo 100 caracteres').nullish(),

		ferias: z.string().max(100, 'Férias deve ter no máximo 100 caracteres').nullish(),

		cert_atuacao_DAJ: z.enum(YES_NO_VALUES, {
			error: 'Selecione se possui certificado de atuação DAJ'
		}),

		obs: z.string().max(1000, 'Observações devem ter no máximo 1000 caracteres').nullish(),

		tipo_bolsa: z.string().max(50, 'Tipo de bolsa deve ter no máximo 50 caracteres').nullish(),

		inicio_bolsa: z.string().nullish(),

		fim_bolsa: z.string().nullish()
	})
	.refine(
		(data) => {
			return data.bolsista ? data.tipo_bolsa && data.inicio_bolsa && data.fim_bolsa : true;
		},
		{
			message: 'Preencha os campos referentes à bolsa',
			path: ['tipo_bolsa', 'inicio_bolsa', 'fim_bolsa']
		}
	);

const passwordSchema = z
	.string()
	.min(8, { message: 'A senha deve ter pelo menos 8 caracteres' })
	.max(20, { message: 'A senha deve ter no máximo 20 caracteres' })
	.refine((password) => /[A-Z]/.test(password), {
		message: 'A senha deve ter pelo menos uma letra maiúscula'
	})
	.refine((password) => /[a-z]/.test(password), {
		message: 'A senha deve ter pelo menos uma letra minúscula'
	})
	.refine((password) => /[0-9]/.test(password), {
		message: 'A senha deve ter pelo menos um número'
	})
	.refine((password) => /[!@#$%^&*]/.test(password), {
		message: 'A senha deve ter pelo menos um símbolo especial'
	});

export const userCreateFormSchema = baseUserFormSchema;
export const userUpdateFormSchema = baseUserFormSchema;

export const userSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false),
	funcao: z.string().optional()
});

export type UserCreateFormSchema = typeof userCreateFormSchema;
export type UserCreateFormData = z.infer<typeof userCreateFormSchema>;

export type UserUpdateFormSchema = typeof userUpdateFormSchema;
export type UserUpdateFormData = z.infer<typeof userUpdateFormSchema>;

export type UserSearchFormSchema = typeof userSearchSchema;
