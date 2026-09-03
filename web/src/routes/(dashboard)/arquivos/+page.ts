import { api } from '$lib/api-client';
import { ApiException, type ListArquivo, type Paginated } from '$lib/types';
import { error } from '@sveltejs/kit';

export const load = async ({ depends, url, fetch }) => {
	depends('app:arquivos');
	try {
		const arquivos = await api.get<Paginated<ListArquivo>>(
			`arquivo/?${url.searchParams.toString()}`,
			{},
			fetch
		);
		return { arquivos };
	} catch (err) {
		if (err instanceof ApiException) error(err.statusCode || 500, err.message);
		throw err;
	}
};
