import { superValidate } from 'sveltekit-superforms';
import { orientacaoJuridicaCreateFormSchema } from '$lib/forms/schemas/orientacao-juridica-schema';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load = async () => {
	const form = await superValidate(zod4(orientacaoJuridicaCreateFormSchema));
	return { form };
};
