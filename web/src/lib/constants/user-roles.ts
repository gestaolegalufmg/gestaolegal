export const USER_ROLES = {
	ADMIN: 'admin',
	ORIENT: 'orient',
	COLAB_PROJ: 'colab_proj',
	ESTAG_DIREITO: 'estag_direito',
	COLAB_EXT: 'colab_ext',
	PROF: 'prof'
} as const;

export const USER_ROLE_VALUES = Object.values(USER_ROLES);

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

export const USER_ROLE_OPTIONS = [
	{ value: USER_ROLES.ADMIN, label: 'Administrador' },
	{ value: USER_ROLES.ORIENT, label: 'Orientador' },
	{ value: USER_ROLES.COLAB_PROJ, label: 'Colaborador de projeto' },
	{ value: USER_ROLES.ESTAG_DIREITO, label: 'Estagiário de Direito' },
	{ value: USER_ROLES.COLAB_EXT, label: 'Colaborador externo' },
	{ value: USER_ROLES.PROF, label: 'Professor' }
] as const;

export const USER_ROLE_BADGE_MAP = {
	[USER_ROLES.ADMIN]: {
		text: 'Administrador',
		variant: 'secondary' as const,
		class: 'bg-primary text-primary-foreground border-primary'
	},
	[USER_ROLES.ORIENT]: {
		text: 'Orientador',
		variant: 'secondary' as const,
		class: 'bg-chart-1 text-primary-foreground border-chart-1'
	},
	[USER_ROLES.COLAB_PROJ]: {
		text: 'Colaborador de projeto',
		variant: 'secondary' as const,
		class: 'bg-chart-2 text-primary-foreground border-chart-2'
	},
	[USER_ROLES.ESTAG_DIREITO]: {
		text: 'Estagiário de Direito',
		variant: 'secondary' as const,
		class: 'bg-chart-3 text-primary-foreground border-chart-3'
	},
	[USER_ROLES.COLAB_EXT]: {
		text: 'Colaborador externo',
		variant: 'secondary' as const,
		class: 'bg-chart-4 text-primary-foreground border-chart-4'
	},
	[USER_ROLES.PROF]: {
		text: 'Professor',
		variant: 'secondary' as const,
		class: 'bg-chart-5 text-primary-foreground border-chart-5'
	}
} as const;

export function getUserRoleLabel(roleValue: string): string {
	const role = USER_ROLE_OPTIONS.find((r) => r.value === roleValue);
	return role?.label || roleValue;
}
