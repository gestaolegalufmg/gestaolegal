export const REGION = {
	NORTE: 'norte',
	SUL: 'sul',
	LESTE: 'leste',
	OESTE: 'oeste',
	NOROESTE: 'noroeste',
	CENTRO_SUL: 'centro_sul',
	NORDESTE: 'nordeste',
	PAMPULHA: 'pampulha',
	BARREIRO: 'barreiro',
	VENDA_NOVA: 'venda_nova',
	CONTAGEM: 'contagem',
	BETIM: 'betim'
} as const;

export const REGION_VALUES = Object.values(REGION);

export type Region = (typeof REGION)[keyof typeof REGION];

export const REGION_OPTIONS = [
	{ value: REGION.NORTE, label: 'Norte' },
	{ value: REGION.SUL, label: 'Sul' },
	{ value: REGION.LESTE, label: 'Leste' },
	{ value: REGION.OESTE, label: 'Oeste' },
	{ value: REGION.NOROESTE, label: 'Noroeste' },
	{ value: REGION.CENTRO_SUL, label: 'Centro-Sul' },
	{ value: REGION.NORDESTE, label: 'Nordeste' },
	{ value: REGION.PAMPULHA, label: 'Pampulha' },
	{ value: REGION.BARREIRO, label: 'Barreiro' },
	{ value: REGION.VENDA_NOVA, label: 'Venda Nova' },
	{ value: REGION.CONTAGEM, label: 'Contagem' },
	{ value: REGION.BETIM, label: 'Betim' }
];

export const REGION_BADGE_MAP = {
	[REGION.NORTE]: { text: 'Norte', variant: 'secondary' },
	[REGION.SUL]: { text: 'Sul', variant: 'secondary' },
	[REGION.LESTE]: { text: 'Leste', variant: 'secondary' },
	[REGION.OESTE]: { text: 'Oeste', variant: 'secondary' },
	[REGION.NOROESTE]: { text: 'Noroeste', variant: 'secondary' },
	[REGION.CENTRO_SUL]: { text: 'Centro-Sul', variant: 'secondary' },
	[REGION.NORDESTE]: { text: 'Nordeste', variant: 'secondary' },
	[REGION.PAMPULHA]: { text: 'Pampulha', variant: 'secondary' },
	[REGION.BARREIRO]: { text: 'Barreiro', variant: 'secondary' },
	[REGION.VENDA_NOVA]: { text: 'Venda Nova', variant: 'secondary' },
	[REGION.CONTAGEM]: { text: 'Contagem', variant: 'secondary' },
	[REGION.BETIM]: { text: 'Betim', variant: 'secondary' }
} as const;
