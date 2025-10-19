import { error, redirect } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { LayoutLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

export const load: LayoutLoad = async ({ url, fetch }) => {
	try {
		const me = await api.get<User>('user/me', {}, fetch);
		return { me };
	} catch (err) {
		if (err instanceof ApiException) {
			if (err.statusCode === 401) {
				const loginUrl = `/login?redirectTo=${encodeURIComponent(url.pathname + url.search)}`;
				redirect(302, loginUrl);
			}
			error(err.statusCode || 500, err.message);
		}
		error(500, 'Erro ao processar dados do usuário');
	}
};
