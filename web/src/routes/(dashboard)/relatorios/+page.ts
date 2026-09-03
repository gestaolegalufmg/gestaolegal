import { error } from '@sveltejs/kit';

// Mesmos papéis aceitos pelo backend em /api/relatorio (ALLOWED_ROLES).
const PAPEIS_PERMITIDOS = ['admin', 'orient', 'colab_ext'];

export const load = async ({ parent }) => {
	const { me } = await parent();
	if (!PAPEIS_PERMITIDOS.includes(me.urole)) {
		error(403, 'Você não tem permissão para acessar os relatórios. Contate o administrador.');
	}
	return {};
};
