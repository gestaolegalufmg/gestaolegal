import type { Endereco } from './endereco';

export type User = {
	id: number;
	email: string;
	senha: string;
	urole: string;
	nome: string;
	sexo: string;
	rg: string;
	cpf: string;
	profissao: string;
	estado_civil: string;
	nascimento: string;
	telefone: string | null;
	celular: string;
	oab: string | null;
	obs: string | null;
	data_entrada: string;
	data_saida: string | null;
	criado: string;
	modificado: string | null;
	criadopor: number;
	matricula: string | null;
	modificadopor: number | null;
	bolsista: boolean;
	tipo_bolsa: string | null;
	horario_atendimento: string | null;
	suplente: string | null;
	ferias: string | null;
	status: boolean;
	cert_atuacao_DAJ: string;
	inicio_bolsa: string | null;
	fim_bolsa: string | null;
	endereco_id: number | null;
	chave_recuperacao: boolean | null;

	endereco: Endereco;
};
