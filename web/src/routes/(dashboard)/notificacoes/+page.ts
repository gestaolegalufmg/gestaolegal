import { api } from '$lib/api-client';
import { ApiException, type Notificacao } from '$lib/types';

/** Formato paginado devolvido pela API (campos no nível raiz). */
type PaginaNotificacoes = {
	items: Notificacao[];
	total: number;
	page: number;
	per_page: number;
	total_pages: number;
};
import { error } from '@sveltejs/kit';

export const load = async ({ depends, url, fetch }) => {
	depends('app:notificacoes');
	try {
		const notificacoes = await api.get<PaginaNotificacoes>(
			`notificacao/?${url.searchParams.toString()}`,
			{},
			fetch
		);
		return { notificacoes };
	} catch (err) {
		if (err instanceof ApiException) error(err.statusCode || 500, err.message);
		throw err;
	}
};
