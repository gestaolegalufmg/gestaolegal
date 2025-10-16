import type { Endereco } from './endereco';

export interface ListAtendido {
	id: number;
	nome: string;
	cpf: string;
	telefone: string;
	celular: string;
	email: string;
	data_nascimento: string;
	status: boolean;
	is_assistido: boolean;
	endereco: Endereco;
}

export interface Atendido {
	id: number;
	nome: string;
	cpf?: string;
	cnpj?: string;
	email?: string;
	telefone?: string;
	celular?: string;
	data_nascimento?: string;
	estado_civil?: string;
	logradouro?: string;
	numero?: string;
	complemento?: string;
	bairro?: string;
	cep?: string;
	cidade?: string;
	estado?: string;
	como_conheceu?: string;
	indicacao_orgao?: string;
	procurou_outro_local?: string;
	procurou_qual_local?: string;
	obs?: string;
	pj_constituida?: string;
	repres_legal?: boolean;
	status?: number;
	created_at?: string;
	updated_at?: string;
}
