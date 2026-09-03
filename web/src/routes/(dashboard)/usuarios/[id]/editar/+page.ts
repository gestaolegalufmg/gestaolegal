import { userUpdateFormSchema } from '$lib/forms/schemas/user-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import type { User } from '$lib/types/user';
import { flattenObject } from '$lib/utils/object';
import { toISODateInput } from '$lib/utils/date';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';

// The API serializes dates as GMT strings; the form's date pickers need ISO
// "YYYY-MM-DD" or the update request fails backend validation.
function normalizeUserDates(source: Record<string, unknown>): Record<string, unknown> {
	const dateFields = ['nascimento', 'data_entrada', 'data_saida', 'inicio_bolsa', 'fim_bolsa'];
	const result = { ...source };
	for (const field of dateFields) {
		if (field in result) {
			result[field] = toISODateInput(result[field] as string | null | undefined);
		}
	}
	return result;
}

export const load: PageLoad = async ({ params, fetch, parent }) => {
	if (params.id === 'eu') {
		const { me } = await parent();
		return {
			form: await superValidate(
				normalizeUserDates(me as unknown as Record<string, unknown>),
				zod4(userUpdateFormSchema)
			),
			user: me
		};
	}

	try {
		const user = await api.get<User>(`user/${params.id}`, {}, fetch);
		const form = await superValidate(
			normalizeUserDates(flattenObject(user)),
			zod4(userUpdateFormSchema)
		);

		return { form, user };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
