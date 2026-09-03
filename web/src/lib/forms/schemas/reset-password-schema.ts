import z from 'zod/v4';

export const resetPasswordSchema = z
	.object({
		password: z
			.string({ message: 'Senha é obrigatória' })
			.min(8, { message: 'Senha deve ter no mínimo 8 caracteres' }),
		confirmPassword: z.string({ message: 'Confirmação de senha é obrigatória' })
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: 'As senhas não coincidem',
		path: ['confirmPassword']
	});

export type ResetPasswordSchema = typeof resetPasswordSchema;
export type ResetPasswordData = z.infer<typeof resetPasswordSchema>;
