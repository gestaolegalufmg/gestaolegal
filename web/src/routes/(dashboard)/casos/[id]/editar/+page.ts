import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { Caso, Paginated, User } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const [caso, usersData] = await Promise.all([
			api.get<Caso>(`caso/${params.id}`, {}, fetch),
			api.get<Paginated<User>>('user?per_page=1000', {}, fetch)
		]);

		const casoData = {
			id_usuario_responsavel: caso.id_usuario_responsavel,
			area_direito: caso.area_direito,
			sub_area: caso.sub_area,
			id_orientador: caso.id_orientador,
			id_estagiario: caso.id_estagiario,
			id_colaborador: caso.id_colaborador,
			situacao_deferimento: caso.situacao_deferimento,
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
