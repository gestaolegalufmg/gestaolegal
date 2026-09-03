import { superValidate } from 'sveltekit-superforms';
import { assistenciaJudiciariaCreateFormSchema } from '$lib/forms/schemas/assistencia-judiciaria-schema';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load = async () => {
	const form = await superValidate(zod4(assistenciaJudiciariaCreateFormSchema));
	return { form };
};
