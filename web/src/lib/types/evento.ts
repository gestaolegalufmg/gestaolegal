import type { User } from './user';

export interface Evento {
	id: number;
	id_caso: number;
	num_evento?: number;
	tipo: string;
	descricao?: string;
	arquivo?: string;
	data_evento: string;
	data_criacao: string;
	id_criado_por: number;
	criado_por?: User;
	id_usuario_responsavel?: number;
	usuario_responsavel?: User;
	status: boolean;
}

export interface ListEvento {
	id: number;
	num_evento?: number;
	tipo: string;
	data_evento: string;
	data_criacao: string;
	criado_por?: string;
	usuario_responsavel?: string;
	status: boolean;
}

export interface EventoCreateInput {
	id_caso: number;
	num_evento?: number;
	tipo: string;
	descricao?: string;
	arquivo?: string;
	data_evento: string;
	id_usuario_responsavel?: number;
	status?: boolean;
}

export interface EventoUpdateInput {
	id_caso?: number;
	num_evento?: number;
	tipo?: string;
	descricao?: string;
	arquivo?: string;
	data_evento?: string;
	id_usuario_responsavel?: number;
	status?: boolean;
}
