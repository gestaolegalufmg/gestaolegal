export const SITUACAO_DEFERIMENTO = {
	AGUARDANDO_DEFERIMENTO: 'aguardando_deferimento',
	ATIVO: 'ativo',
	INDEFERIDO: 'indeferido',
	ARQUIVADO: 'arquivado',
	SOLUCIONADO: 'solucionado'
} as const;

export const SITUACAO_DEFERIMENTO_VALUES = Object.values(SITUACAO_DEFERIMENTO);

export type SituacaoDeferimento = (typeof SITUACAO_DEFERIMENTO)[keyof typeof SITUACAO_DEFERIMENTO];

export const SITUACAO_DEFERIMENTO_OPTIONS = [
	{ value: SITUACAO_DEFERIMENTO.AGUARDANDO_DEFERIMENTO, label: 'Aguardando Deferimento' },
	{ value: SITUACAO_DEFERIMENTO.ATIVO, label: 'Ativo' },
	{ value: SITUACAO_DEFERIMENTO.INDEFERIDO, label: 'Indeferido' },
	{ value: SITUACAO_DEFERIMENTO.ARQUIVADO, label: 'Arquivado' },
	{ value: SITUACAO_DEFERIMENTO.SOLUCIONADO, label: 'Solucionado' }
];

export const SITUACAO_DEFERIMENTO_BADGE_MAP = {
	[SITUACAO_DEFERIMENTO.AGUARDANDO_DEFERIMENTO]: {
		text: 'Aguardando Deferimento',
		variant: 'secondary' as const,
		class:
			'border-transparent bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
	},
	[SITUACAO_DEFERIMENTO.ATIVO]: {
		text: 'Ativo',
		variant: 'default' as const,
		class: 'border-transparent bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
	},
	[SITUACAO_DEFERIMENTO.INDEFERIDO]: {
		text: 'Indeferido',
		variant: 'secondary' as const,
		class: 'border-transparent bg-pink-700 text-pink-50 dark:bg-pink-800 dark:text-pink-100'
	},
	[SITUACAO_DEFERIMENTO.ARQUIVADO]: {
		text: 'Arquivado',
		variant: 'secondary' as const,
		class: 'border-transparent bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200'
	},
	[SITUACAO_DEFERIMENTO.SOLUCIONADO]: {
		text: 'Solucionado',
		variant: 'default' as const,
		class: 'border-transparent bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
	}
} as const;
