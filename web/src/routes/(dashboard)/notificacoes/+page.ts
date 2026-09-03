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

/** Visões da lista: ativas (padrão), só arquivadas ou todas. */
export const FILTROS_ARQUIVADAS = ['nao', 'sim', 'todas'] as const;
export type FiltroArquivadas = (typeof FILTROS_ARQUIVADAS)[number];

export const load = async ({ depends, url, fetch }) => {
	depends('app:notificacoes');
	const pedido = url.searchParams.get('arquivadas');
	const arquivadas: FiltroArquivadas = FILTROS_ARQUIVADAS.includes(pedido as FiltroArquivadas)
		? (pedido as FiltroArquivadas)
		: 'nao';
	try {
		const notificacoes = await api.get<PaginaNotificacoes>(
			`notificacao/?${url.searchParams.toString()}`,
			{},
			fetch
		);
		return { notificacoes, arquivadas };
	} catch (err) {
		if (err instanceof ApiException) error(err.statusCode || 500, err.message);
		throw err;
	}
};
