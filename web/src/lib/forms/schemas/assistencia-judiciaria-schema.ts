import { z } from 'zod/v4';

const baseAssistenciaJudiciariaFormSchema = z.object({
	nome: z
		.string()
		.nonempty('Nome é obrigatório')
		.max(150, 'Nome deve ter no máximo 150 caracteres'),

	regiao: z.enum(
		[
			'norte',
			'sul',
			'leste',
			'oeste',
			'noroeste',
			'centro_sul',
			'nordeste',
			'pampulha',
			'barreiro',
			'venda_nova',
			'contagem',
			'betim'
		],
		{ error: 'Selecione a região' }
	),

	areas_atendidas: z
		.array(z.string())
		.min(1, 'Selecione ao menos uma área atendida'),

	telefone: z
		.string()
		.nonempty('Telefone é obrigatório')
		.max(18, 'Telefone deve ter no máximo 18 caracteres'),

	email: z.email('E-mail inválido').max(80, 'E-mail deve ter no máximo 80 caracteres'),

	logradouro: z.string().nonempty('Logradouro é obrigatório').max(100),
	numero: z.string().nonempty('Número é obrigatório').max(8),
	complemento: z.string().max(100).nullish(),
	bairro: z.string().nonempty('Bairro é obrigatório').max(100),
	cep: z.string().nonempty('CEP é obrigatório').max(9),
	cidade: z.string().nonempty('Cidade é obrigatória').max(100),
	estado: z.string().nonempty('Estado é obrigatório').max(100)
});

export const assistenciaJudiciariaCreateFormSchema = baseAssistenciaJudiciariaFormSchema;
export const assistenciaJudiciariaUpdateFormSchema = baseAssistenciaJudiciariaFormSchema;

export const assistenciaJudiciariaSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false),
	area: z.string().optional(),
	regiao: z.string().optional()
});

export type AssistenciaJudiciariaCreateFormSchema = typeof assistenciaJudiciariaCreateFormSchema;
export type AssistenciaJudiciariaCreateFormData = z.infer<
	typeof assistenciaJudiciariaCreateFormSchema
>;
export type AssistenciaJudiciariaUpdateFormSchema = typeof assistenciaJudiciariaUpdateFormSchema;
