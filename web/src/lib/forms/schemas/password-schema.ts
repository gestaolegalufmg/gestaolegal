import { z } from 'zod';

export const passwordChangeSchema = z
	.object({
		currentPassword: z.string().optional(),
		newPassword: z.string().min(8, 'Nova senha deve ter pelo menos 8 caracteres'),
		confirmPassword: z.string().min(1, 'Confirmação de senha é obrigatória')
	})
	.refine((data) => data.newPassword === data.confirmPassword, {
		message: 'As senhas não coincidem',
		path: ['confirmPassword']
	});

export type PasswordChangeSchema = typeof passwordChangeSchema;
