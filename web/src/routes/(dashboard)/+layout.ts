import { error, redirect } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { LayoutLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';
import { sincronizarUnidades } from '$lib/stores/unidade';

export const load: LayoutLoad = async ({ url, fetch }) => {
	try {
		const me = await api.get<User>('user/me', {}, fetch);
		// A unidade guardada só vale enquanto o vínculo existir: se o admin tirou
		// o usuário dela, cai para a primeira da lista.
		sincronizarUnidades(me.unidades);
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
