import { z } from 'zod/v4';

export const eventoCreateFormSchema = z.object({
	tipo: z.string().min(1, 'Tipo é obrigatório'),
	descricao: z.string().optional().nullable(),
	arquivo: z.instanceof(File).optional().nullable(),
	data_evento: z.string().min(1, 'Data do evento é obrigatória'),
	id_usuario_responsavel: z.number().optional().nullable(),
	status: z.boolean().default(true)
});

export const eventoUpdateFormSchema = z.object({
	tipo: z.string().min(1, 'Tipo é obrigatório'),
	descricao: z.string().optional().nullable(),
	arquivo: z.instanceof(File).optional().nullable(),
	data_evento: z.string().min(1, 'Data do evento é obrigatória'),
	id_usuario_responsavel: z.number().optional().nullable(),
	status: z.boolean().default(true)
});

export type EventoCreateFormSchema = typeof eventoCreateFormSchema;
export type EventoUpdateFormSchema = typeof eventoUpdateFormSchema;
