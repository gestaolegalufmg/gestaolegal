import type { Endereco } from './endereco';

export type OrientacaoResumo = {
	id: number;
	area_direito: string;
	sub_area?: string | null;
	descricao: string;
};

export type AssistenciaJudiciaria = {
	id: number;
	nome: string;
	regiao: string;
	areas_atendidas: string[];
	telefone: string;
	email: string;
	status: boolean;
	endereco: Endereco | null;
	orientacoes: OrientacaoResumo[];
};

export type ListAssistenciaJudiciaria = {
	id: number;
	nome: string;
	regiao: string;
	areas_atendidas: string[];
	telefone: string;
	email: string;
	status: boolean;
	cidade: string | null;
};
