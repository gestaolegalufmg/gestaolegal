import type { User } from './user';

export interface Processo {
	id: number;
	especie: string;
	numero?: number;
	identificacao?: string;
	vara?: string;
	link?: string;
	probabilidade?: string;
	posicao_assistido?: string;
	valor_causa_inicial?: number;
	valor_causa_atual?: number;
	data_distribuicao?: string;
	data_transito_em_julgado?: string;
	obs?: string;
	id_caso: number;
	status: boolean;
	id_criado_por: number;
	criado_por?: User;
}

export interface ListProcesso {
	id: number;
	especie: string;
	numero?: number;
	identificacao?: string;
	vara?: string;
	probabilidade?: string;
	posicao_assistido?: string;
	valor_causa_inicial?: number;
	valor_causa_atual?: number;
	data_distribuicao?: string;
	data_transito_em_julgado?: string;
	status: boolean;
	criado_por?: User;
}

export interface ProcessoCreateInput {
	especie: string;
	numero?: number;
	identificacao?: string;
	vara?: string;
	link?: string;
	probabilidade?: string;
	posicao_assistido?: string;
	valor_causa_inicial?: number;
	valor_causa_atual?: number;
	data_distribuicao?: string;
	data_transito_em_julgado?: string;
	obs?: string;
	id_caso: number;
	status?: boolean;
}

export interface ProcessoUpdateInput {
	especie?: string;
	numero?: number;
	identificacao?: string;
	vara?: string;
	link?: string;
	probabilidade?: string;
	posicao_assistido?: string;
	valor_causa_inicial?: number;
	valor_causa_atual?: number;
	data_distribuicao?: string;
	data_transito_em_julgado?: string;
	obs?: string;
	id_caso?: number;
	status?: boolean;
}
