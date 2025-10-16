import { z } from 'zod/v4';

const baseOrientacaoJuridicaFormSchema = z
	.object({
		area_direito: z.enum(
			['administrativo', 'ambiental', 'civel', 'empresarial', 'penal', 'trabalhista'],
			{
				error: 'Selecione a área do direito'
			}
		),

		sub_area: z.string().max(50, 'Sub-área deve ter no máximo 50 caracteres').nullish(),

		descricao: z
			.string()
			.min(10, 'Descrição deve ter pelo menos 10 caracteres')
			.max(5000, 'Descrição deve ter no máximo 5000 caracteres')
			.nonempty('Descrição é obrigatória'),

		atendidos_ids: z.array(z.number())
	})
	.refine(
		(data) => {
			if (data.area_direito === 'civel' || data.area_direito === 'administrativo') {
				return !!data.sub_area;
			}
			return true;
		},
		{
			message: 'Sub-área é obrigatória para áreas Cível e Administrativo',
			path: ['sub_area']
		}
	);

export const orientacaoJuridicaCreateFormSchema = baseOrientacaoJuridicaFormSchema;
export const orientacaoJuridicaUpdateFormSchema = baseOrientacaoJuridicaFormSchema;

export const orientacaoSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false),
	area: z.string().optional()
});

export type OrientacaoJuridicaCreateFormSchema = typeof orientacaoJuridicaCreateFormSchema;
export type OrientacaoJuridicaCreateFormData = z.infer<typeof orientacaoJuridicaCreateFormSchema>;

export type OrientacaoJuridicaUpdateFormSchema = typeof orientacaoJuridicaUpdateFormSchema;
export type OrientacaoJuridicaUpdateFormData = z.infer<typeof orientacaoJuridicaUpdateFormSchema>;

export type OrientacaoSearchFormSchema = typeof orientacaoSearchSchema;
