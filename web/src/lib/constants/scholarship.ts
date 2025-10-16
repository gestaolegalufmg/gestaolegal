export const SCHOLARSHIP_TYPE = {
	FUMP: 'fump',
	VALLE: 'vale',
	PROEX: 'proex',
	OUTRA: 'outra'
} as const;

export const SCHOLARSHIP_TYPE_VALUES = Object.values(SCHOLARSHIP_TYPE);

export type ScholarshipType = (typeof SCHOLARSHIP_TYPE)[keyof typeof SCHOLARSHIP_TYPE];

export const SCHOLARSHIP_TYPE_OPTIONS = [
	{ value: SCHOLARSHIP_TYPE.FUMP, label: 'FUMP' },
	{ value: SCHOLARSHIP_TYPE.VALLE, label: 'Valle Ferreira' },
	{ value: SCHOLARSHIP_TYPE.PROEX, label: 'Projeto de extensão' },
	{ value: SCHOLARSHIP_TYPE.OUTRA, label: 'Outra' }
];

export const YES_NO = {
	SIM: 'sim',
	NAO: 'nao'
} as const;

export const YES_NO_VALUES = Object.values(YES_NO);

export type YesNo = (typeof YES_NO)[keyof typeof YES_NO];

export const YES_NO_OPTIONS = [
	{ value: YES_NO.SIM, label: 'Sim' },
	{ value: YES_NO.NAO, label: 'Não' }
];

export const BOOLEAN_OPTIONS = [
	{ value: 'true', label: 'Sim' },
	{ value: '', label: 'Não' }
];
