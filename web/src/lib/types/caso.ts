import type { User } from './user';
import type { Atendido } from './atendido';
import type { Processo } from './processo';

export interface Caso {
	id: number;
	id_usuario_responsavel: number;
	usuario_responsavel: User;
	area_direito: string;
	sub_area: string | null;
	clientes: Atendido[];
	id_orientador: number | null;
	orientador: User | null;
	id_estagiario: number | null;
	estagiario: User | null;
	id_colaborador: number | null;
	colaborador: User | null;
	data_criacao: string;
	id_criado_por: number;
	criado_por: User;
	data_modificacao: string | null;
	id_modificado_por: number | null;
	modificado_por: User | null;
	situacao_deferimento: string;
	justif_indeferimento: string | null;
	status: boolean;
	descricao: string | null;
	numero_ultimo_processo: number | null;
	processos?: Processo[];
	arquivos?: ArquivoCaso[];
}

export interface ListCaso {
	id: number;
	area_direito: string;
	sub_area: string | null;
	situacao_deferimento: string;
	status: boolean;
	descricao: string | null;
	data_criacao: string;
	usuario_responsavel: User;
	clientes: Atendido[];
}

export interface ArquivoCaso {
	id: number;
	link_arquivo: string;
}
