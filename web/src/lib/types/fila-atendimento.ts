export interface FilaItem {
	id: number;
	senha: string;
	posicao: number | null;
	tipo: string | null;
	prioridade: number;
	/** 0 = aguardando, 1 = em atendimento, 2 = concluído */
	status: number;
	status_label: string;
	data_criacao: string;
	id_atendido: number;
	atendido_nome: string;
	atendido_cpf: string;
}

export const TIPOS_FILA = [
	'Atendimento Jurídico',
	'Assistência Judiciária',
	'Orientação Jurídica',
	'Atendimento Psicológico'
] as const;
