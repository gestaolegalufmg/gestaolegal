import {
	AREA_DIREITO,
	AREA_DIREITO_VALUES,
	SUB_AREA_DIREITO_ADMINISTRATIVO_VALUES,
	SUB_AREA_DIREITO_CIVEL_VALUES,
	type SubAreaDireitoAdministrativo,
	type SubAreaDireitoCivel
} from '$lib/constants/area_direito';
import { SITUACAO_DEFERIMENTO_VALUES } from '$lib/constants/situacao-deferimento';
import { z } from 'zod/v4';

export const casoCreateFormSchema = z
	.object({
		id_usuario_responsavel: z.number().min(1, 'Usuário responsável é obrigatório'),
		area_direito: z.enum(AREA_DIREITO_VALUES),
		sub_area: z.string().nullish(),
		id_orientador: z.number().optional().nullable(),
		id_estagiario: z.number().optional().nullable(),
		id_colaborador: z.number().optional().nullable(),
		situacao_deferimento: z.enum(SITUACAO_DEFERIMENTO_VALUES),
		justif_indeferimento: z.string().optional().nullable(),
		descricao: z.string().optional().nullable(),
		ids_clientes: z.array(z.number()).default([])
	})
	.refine(
		(data) => {
			if (data.area_direito === AREA_DIREITO.ADMINISTRATIVO && data.sub_area) {
				return SUB_AREA_DIREITO_ADMINISTRATIVO_VALUES.includes(
					data.sub_area as SubAreaDireitoAdministrativo
				);
			}
			if (data.area_direito === AREA_DIREITO.CIVEL && data.sub_area) {
				return SUB_AREA_DIREITO_CIVEL_VALUES.includes(data.sub_area as SubAreaDireitoCivel);
			}

			return true;
		},
		{
			path: ['sub_area'],
			message: 'Sub-área é obrigatória'
		}
	)
	.refine(
		(data) => {
			if (data.situacao_deferimento === 'indeferido') {
				return data.justif_indeferimento && data.justif_indeferimento.trim().length > 0;
			}
			return true;
		},
		{
			path: ['justif_indeferimento'],
			message: 'Justificativa de indeferimento é obrigatória quando o caso é indeferido'
		}
	);

export const casoUpdateFormSchema = casoCreateFormSchema.partial();

export const casoSearchSchema = z.object({
	search: z.string().optional(),
	show_inactive: z.boolean().optional().default(false),
	situacao_deferimento: z.string().optional()
});

export type CasoCreateFormSchema = typeof casoCreateFormSchema;
export type CasoUpdateFormSchema = typeof casoUpdateFormSchema;
export type CasoSearchFormSchema = typeof casoSearchSchema;
