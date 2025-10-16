import { z } from 'zod/v4';

export const processoCreateFormSchema = z.object({
	especie: z.string().min(1, 'Espécie é obrigatória'),
	numero: z.number().optional().nullable(),
	identificacao: z.string().optional().nullable(),
	vara: z.string().optional().nullable(),
	link: z.url().optional().nullable().or(z.literal('')),
	probabilidade: z.string().optional().nullable(),
	posicao_assistido: z.string().optional().nullable(),
	valor_causa_inicial: z.number().optional().nullable(),
	valor_causa_atual: z.number().optional().nullable(),
	data_distribuicao: z.string().optional().nullable(),
	data_transito_em_julgado: z.string().optional().nullable(),
	obs: z.string().optional().nullable(),
	status: z.boolean().default(true)
});

export const processoSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false)
});

export type ProcessoCreateFormSchema = typeof processoCreateFormSchema;
export type ProcessoSearchFormSchema = typeof processoSearchSchema;
