import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import { normalizarSituacaoDeferimento } from '$lib/constants/situacao-deferimento';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { Caso, UserOption } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const [caso, usersData] = await Promise.all([
			api.get<Caso>(`caso/${params.id}`, {}, fetch),
			api.get<{ items: UserOption[] }>('user/opcoes', {}, fetch)
		]);

		const casoData = {
			id_usuario_responsavel: caso.id_usuario_responsavel,
			area_direito: caso.area_direito,
			sub_area: caso.sub_area,
			id_orientador: caso.id_orientador,
			id_estagiario: caso.id_estagiario,
			id_colaborador: caso.id_colaborador,
			// Casos antigos gravaram "deferido"; sem normalizar, o select fica
			// fora das opções e o formulário acusa "invalid input".
			situacao_deferimento: normalizarSituacaoDeferimento(caso.situacao_deferimento),
			justif_indeferimento: caso.justif_indeferimento,
			descricao: caso.descricao,
			ids_clientes: caso.clientes?.map((cliente: { id: number }) => cliente.id) ?? []
		};

		const form = await superValidate(casoData, zod4(casoCreateFormSchema));
		const usuarios = usersData.items ?? [];
		const casoAssistidos = caso.clientes ?? [];

		return { form, usuarios, assistidos: casoAssistidos, caso };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
