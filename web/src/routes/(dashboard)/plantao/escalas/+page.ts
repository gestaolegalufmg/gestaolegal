import { api } from '$lib/api-client';
import type { ResumoEscala } from '$lib/types';

export const load = async ({ fetch }) => ({
	escalas: await api.get<ResumoEscala[]>('plantao/escalas', {}, fetch)
});
