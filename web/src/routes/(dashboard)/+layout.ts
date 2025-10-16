import { error, redirect } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { LayoutLoad } from './$types';
import { api } from '$lib/api-client';

export const load: LayoutLoad = async ({ url, fetch }) => {
	const response = await api.get('user/me', {}, fetch);

	if (response.status === 401) {
		const loginUrl = `/login?redirectTo=${encodeURIComponent(url.pathname + url.search)}`;
		redirect(302, loginUrl);
	}

	if (!response.ok) {
		error(response.status, 'Falha ao carregar dados do usuário');
	}

	let me: User;
	try {
		me = await response.json();
	} catch (e) {
		error(500, 'Erro ao processar dados do usuário');
	}

	return { me };
};
