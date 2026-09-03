import { api } from '$lib/api-client';

/** Contagem de notificações não lidas (badge do atalho). */
type NaoLidas = { total: number };

export const load = async ({ fetch }) => {
	try {
		const { total } = await api.get<NaoLidas>('notificacao/nao-lidas', {}, fetch);
		return { naoLidas: total };
	} catch {
		// A home não pode depender do contador: sem ele, só não mostra o número.
		return { naoLidas: 0 };
	}
};
