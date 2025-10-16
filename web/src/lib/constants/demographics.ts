export const GENDER = {
	MASCULINO: 'M',
	FEMININO: 'F',
	OUTRO: 'outro'
} as const;

export const GENDER_VALUES = Object.values(GENDER);

export type Gender = (typeof GENDER)[keyof typeof GENDER];

export const GENDER_OPTIONS = [
	{ value: GENDER.MASCULINO, label: 'Masculino' },
	{ value: GENDER.FEMININO, label: 'Feminino' },
	{ value: GENDER.OUTRO, label: 'Outro' }
];

export function getGenderLabel(genderValue: string): string {
	const gender = GENDER_OPTIONS.find((g) => g.value === genderValue);
	return gender?.label || genderValue;
}

export const MARITAL_STATUS = {
	SOLTEIRO: 'solteiro',
	CASADO: 'casado',
	DIVORCIADO: 'divorciado',
	SEPARADO: 'separado',
	UNIAO: 'uniao',
	VIUVO: 'viuvo'
} as const;

export const MARITAL_STATUS_VALUES = Object.values(MARITAL_STATUS);

export type MaritalStatus = (typeof MARITAL_STATUS)[keyof typeof MARITAL_STATUS];

export const MARITAL_STATUS_OPTIONS = [
	{ value: MARITAL_STATUS.SOLTEIRO, label: 'Solteiro(a)' },
	{ value: MARITAL_STATUS.CASADO, label: 'Casado(a)' },
	{ value: MARITAL_STATUS.DIVORCIADO, label: 'Divorciado(a)' },
	{ value: MARITAL_STATUS.SEPARADO, label: 'Separado(a)' },
	{ value: MARITAL_STATUS.UNIAO, label: 'União estável' },
	{ value: MARITAL_STATUS.VIUVO, label: 'Viúvo(a)' }
];

export function getMaritalStatusLabel(maritalStatusValue: string): string {
	const maritalStatus = MARITAL_STATUS_OPTIONS.find((m) => m.value === maritalStatusValue);
	return maritalStatus?.label || maritalStatusValue;
}

export const BRAZILIAN_STATES = {
	AC: 'AC',
	AL: 'AL',
	AM: 'AM',
	AP: 'AP',
	BA: 'BA',
	CE: 'CE',
	DF: 'DF',
	ES: 'ES',
	GO: 'GO',
	MA: 'MA',
	MG: 'MG',
	MS: 'MS',
	MT: 'MT',
	PA: 'PA',
	PB: 'PB',
	PE: 'PE',
	PI: 'PI',
	PR: 'PR',
	RJ: 'RJ',
	RN: 'RN',
	RO: 'RO',
	RR: 'RR',
	RS: 'RS',
	SC: 'SC',
	SE: 'SE',
	SP: 'SP',
	TO: 'TO'
} as const;

export const BRAZILIAN_STATES_VALUES = Object.values(BRAZILIAN_STATES);

export type BrazilianState = (typeof BRAZILIAN_STATES)[keyof typeof BRAZILIAN_STATES];

export const BRAZILIAN_STATES_OPTIONS = [
	{ value: BRAZILIAN_STATES.AC, label: 'Acre' },
	{ value: BRAZILIAN_STATES.AL, label: 'Alagoas' },
	{ value: BRAZILIAN_STATES.AM, label: 'Amazonas' },
	{ value: BRAZILIAN_STATES.AP, label: 'Amapá' },
	{ value: BRAZILIAN_STATES.BA, label: 'Bahia' },
	{ value: BRAZILIAN_STATES.CE, label: 'Ceará' },
	{ value: BRAZILIAN_STATES.DF, label: 'Distrito Federal' },
	{ value: BRAZILIAN_STATES.ES, label: 'Espírito Santo' },
	{ value: BRAZILIAN_STATES.GO, label: 'Goiás' },
	{ value: BRAZILIAN_STATES.MA, label: 'Maranhão' },
	{ value: BRAZILIAN_STATES.MG, label: 'Minas Gerais' },
	{ value: BRAZILIAN_STATES.MS, label: 'Mato Grosso do Sul' },
	{ value: BRAZILIAN_STATES.MT, label: 'Mato Grosso' },
	{ value: BRAZILIAN_STATES.PA, label: 'Pará' },
	{ value: BRAZILIAN_STATES.PB, label: 'Paraíba' },
	{ value: BRAZILIAN_STATES.PE, label: 'Pernambuco' },
	{ value: BRAZILIAN_STATES.PI, label: 'Piauí' },
	{ value: BRAZILIAN_STATES.PR, label: 'Paraná' },
	{ value: BRAZILIAN_STATES.RJ, label: 'Rio de Janeiro' },
	{ value: BRAZILIAN_STATES.RN, label: 'Rio Grande do Norte' },
	{ value: BRAZILIAN_STATES.RO, label: 'Rondônia' },
	{ value: BRAZILIAN_STATES.RR, label: 'Roraima' },
	{ value: BRAZILIAN_STATES.RS, label: 'Rio Grande do Sul' },
	{ value: BRAZILIAN_STATES.SC, label: 'Santa Catarina' },
	{ value: BRAZILIAN_STATES.SE, label: 'Sergipe' },
	{ value: BRAZILIAN_STATES.SP, label: 'São Paulo' },
	{ value: BRAZILIAN_STATES.TO, label: 'Tocantins' }
];

export function getBrazilianStateLabel(stateValue: string): string {
	const state = BRAZILIAN_STATES_OPTIONS.find((s) => s.value === stateValue);
	return state?.label || stateValue;
}
