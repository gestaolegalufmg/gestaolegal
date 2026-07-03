export const FilaPrioridade = {
	NORMAL: 0,
	PRIORIDADE: 1,
	SUPER_PRIORIDADE: 2
} as const;

export const FilaStatus = {
	NA_FILA: 0,
	CHAMADO: 1,
	CANCELADO: 2
} as const;

export interface FilaItem {
	id: number;
	id_atendido: number | null;
	nome: string | null;
	senha: string;
	prioridade: number;
	psicologia: number;
	status: number;
	data_criacao: string | null;
	data_saida: string | null;
}

export interface FilaHoje {
	data: string;
	fila: FilaItem[];
	atendidos_cancelados: FilaItem[];
}

export interface SenhaPreview {
	senha: string;
}
