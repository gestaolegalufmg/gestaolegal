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
		variant: 'secondary' as const
	},
	[SITUACAO_DEFERIMENTO.ATIVO]: {
		text: 'Ativo',
		variant: 'default' as const
	},
	[SITUACAO_DEFERIMENTO.INDEFERIDO]: {
		text: 'Indeferido',
		variant: 'secondary' as const
	},
	[SITUACAO_DEFERIMENTO.ARQUIVADO]: {
		text: 'Arquivado',
		variant: 'secondary' as const
	},
	[SITUACAO_DEFERIMENTO.SOLUCIONADO]: {
		text: 'Solucionado',
		variant: 'default' as const
	}
} as const;
