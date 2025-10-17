import z from 'zod/v4';

export const setupAdminSchema = z.object({
	email: z.email({ message: 'Email inválido' }),
	password: z
		.string({ message: 'Senha é obrigatória' })
		.min(8, { message: 'Senha deve ter no mínimo 8 caracteres' }),
	setup_token: z.string({ message: 'Token de configuração é obrigatório' }).min(1, {
		message: 'Token de configuração é obrigatório'
	})
});

export type SetupAdminSchema = typeof setupAdminSchema;
export type SetupAdminData = z.infer<typeof setupAdminSchema>;
