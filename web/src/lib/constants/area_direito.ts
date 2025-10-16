export const AREA_DIREITO = {
	AMBIENTAL: 'ambiental',
	ADMINISTRATIVO: 'administrativo',
	CIVEL: 'civel',
	EMPRESARIAL: 'empresarial',
	PENAL: 'penal',
	TRABALHISTA: 'trabalhista'
} as const;

export const SUB_AREA_DIREITO_ADMINISTRATIVO = {
	ADMINISTRATIVO: 'administrativo',
	PREVIDENCIARIO: 'previdenciario',
	TRIBUTARIO: 'tributario'
} as const;

export const SUB_AREA_DIREITO_CIVEL = {
	CONSUMIDOR: 'consumidor',
	CONTRATOS: 'contratos',
	RESPONSABILIDADE_CIVIL: 'resp_civil',
	REAIS: 'reais',
	FAMILIA: 'familia',
	SUCESSOES: 'sucessoes'
} as const;

export const AREA_DIREITO_VALUES = Object.values(AREA_DIREITO);
export const SUB_AREA_DIREITO_ADMINISTRATIVO_VALUES = Object.values(
	SUB_AREA_DIREITO_ADMINISTRATIVO
);
export const SUB_AREA_DIREITO_CIVEL_VALUES = Object.values(SUB_AREA_DIREITO_CIVEL);

export type AreaDireito = (typeof AREA_DIREITO)[keyof typeof AREA_DIREITO];
export type SubAreaDireitoAdministrativo =
	(typeof SUB_AREA_DIREITO_ADMINISTRATIVO)[keyof typeof SUB_AREA_DIREITO_ADMINISTRATIVO];
export type SubAreaDireitoCivel =
	(typeof SUB_AREA_DIREITO_CIVEL)[keyof typeof SUB_AREA_DIREITO_CIVEL];

export const AREA_DIREITO_OPTIONS = [
	{ value: AREA_DIREITO.AMBIENTAL, label: 'Ambiental' },
	{ value: AREA_DIREITO.ADMINISTRATIVO, label: 'Administrativo' },
	{ value: AREA_DIREITO.CIVEL, label: 'Civel' },
	{ value: AREA_DIREITO.EMPRESARIAL, label: 'Empresarial' },
	{ value: AREA_DIREITO.PENAL, label: 'Penal' },
	{ value: AREA_DIREITO.TRABALHISTA, label: 'Trabalhista' }
];

export const SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS = [
	{ value: SUB_AREA_DIREITO_ADMINISTRATIVO.ADMINISTRATIVO, label: 'Administrativo' },
	{ value: SUB_AREA_DIREITO_ADMINISTRATIVO.PREVIDENCIARIO, label: 'Previdenciario' },
	{ value: SUB_AREA_DIREITO_ADMINISTRATIVO.TRIBUTARIO, label: 'Tributário' }
];

export const SUB_AREA_DIREITO_CIVEL_OPTIONS = [
	{ value: SUB_AREA_DIREITO_CIVEL.CONSUMIDOR, label: 'Consumidor' },
	{ value: SUB_AREA_DIREITO_CIVEL.CONTRATOS, label: 'Contratos' },
	{ value: SUB_AREA_DIREITO_CIVEL.RESPONSABILIDADE_CIVIL, label: 'Responsabilidade Civil' },
	{ value: SUB_AREA_DIREITO_CIVEL.REAIS, label: 'Reais' },
	{ value: SUB_AREA_DIREITO_CIVEL.FAMILIA, label: 'Familia' },
	{ value: SUB_AREA_DIREITO_CIVEL.SUCESSOES, label: 'Sucessões' }
];

export const AREA_BADGE_MAP = {
	[AREA_DIREITO.ADMINISTRATIVO]: { text: 'Administrativo', variant: 'secondary' as const },
	[AREA_DIREITO.AMBIENTAL]: { text: 'Ambiental', variant: 'secondary' as const },
	[AREA_DIREITO.CIVEL]: { text: 'Cível', variant: 'secondary' as const },
	[AREA_DIREITO.EMPRESARIAL]: { text: 'Empresarial', variant: 'secondary' as const },
	[AREA_DIREITO.PENAL]: { text: 'Penal', variant: 'secondary' as const },
	[AREA_DIREITO.TRABALHISTA]: { text: 'Trabalhista', variant: 'secondary' as const }
} as const;

export const SUB_AREA_BADGE_MAP = {
	[SUB_AREA_DIREITO_ADMINISTRATIVO.PREVIDENCIARIO]: {
		text: 'Previdenciário',
		variant: 'secondary'
	},
	[SUB_AREA_DIREITO_ADMINISTRATIVO.TRIBUTARIO]: { text: 'Tributário', variant: 'secondary' },
	[SUB_AREA_DIREITO_CIVEL.CONSUMIDOR]: { text: 'Consumidor', variant: 'secondary' },
	[SUB_AREA_DIREITO_CIVEL.CONTRATOS]: { text: 'Contratos', variant: 'secondary' },
	[SUB_AREA_DIREITO_CIVEL.RESPONSABILIDADE_CIVIL]: {
		text: 'Responsabilidade Civil',
		variant: 'secondary'
	},
	[SUB_AREA_DIREITO_CIVEL.REAIS]: { text: 'Reais', variant: 'secondary' },
	[SUB_AREA_DIREITO_CIVEL.FAMILIA]: { text: 'Familia', variant: 'secondary' },
	[SUB_AREA_DIREITO_CIVEL.SUCESSOES]: { text: 'Sucessões', variant: 'secondary' }
} as const;
