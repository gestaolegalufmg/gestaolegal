import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';
import type { Atendido } from '$lib/types';
import type { Paginated } from '$lib/types/paginated';
import type { ListCaso } from '$lib/types/caso';
import type { OrientacaoJuridica } from '$lib/types/orientacao-juridica';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const atendido = await api.get<Atendido>(`atendido/${params.id}`, {}, fetch);

		// Casos e orientações vinculados a esta pessoa. Falhas aqui não devem
		// derrubar a página inteira — mostramos listas vazias como fallback.
		const [casos, orientacoes] = await Promise.all([
			api.get<Paginated<ListCaso>>(`atendido/${params.id}/casos`, {}, fetch).catch(() => null),
			api
				.get<Paginated<OrientacaoJuridica>>(`atendido/${params.id}/orientacoes`, {}, fetch)
				.catch(() => null)
		]);

		return {
			atendido,
			casos: casos?.items ?? [],
			orientacoes: orientacoes?.items ?? []
		};
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
