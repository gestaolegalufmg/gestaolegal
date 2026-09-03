import z from 'zod/v4';

export const forgotPasswordSchema = z.object({
	email: z.email({ message: 'Email inválido' })
});

export type ForgotPasswordSchema = typeof forgotPasswordSchema;
export type ForgotPasswordData = z.infer<typeof forgotPasswordSchema>;
