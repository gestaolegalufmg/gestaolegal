/**
 * Tipos do plantão e do registro de presença.
 *
 * Datas puras (`data`, `data_marcada`, `dias`) chegam da API como "YYYY-MM-DD".
 * Já os timestamps (`data_abertura`, `data_entrada`, ...) vêm em RFC-1123 GMT,
 * como no resto da API — formate-os com `formatDateTime` de `$lib/utils/date`.
 */

export const CONFIRMACAO = {
	ABERTO: 'aberto',
	CONFIRMAR: 'confirmar',
	DIVERGENCIA: 'divergencia',
	AUSENCIA: 'ausencia'
} as const;

export type Confirmacao = (typeof CONFIRMACAO)[keyof typeof CONFIRMACAO];

export interface JanelaPlantao {
	data_abertura: string | null;
	data_fechamento: string | null;
	aberto: boolean;
}

export interface DiaAberto {
	data: string;
	tem_vaga: boolean;
	/** `null` = o papel de quem consulta não tem limite de vagas. */
	vagas_restantes: number | null;
}

export interface EscalaItem {
	data: string;
	id_usuario: number;
	nome: string;
	urole: string;
}

export interface MinhaMarcacao {
	id: number;
	data_marcada: string;
	confirmacao: Confirmacao;
}

export interface PaginaPlantao {
	plantao: JanelaPlantao;
	pode_marcar: boolean;
	limite_dias: number;
	/** Qual plantão a pessoa está prestes a marcar (1º, 2º...). */
	numero_plantao: number;
	dias_abertos: DiaAberto[];
	escala: EscalaItem[];
	meus_dias: MinhaMarcacao[];
}

export interface ConfiguracaoPlantao {
	data_abertura: string | null;
	data_fechamento: string | null;
	dias: string[];
}

export type StatusPresenca = 'entrada' | 'saida';

export interface EstadoPresenca {
	status_presenca: StatusPresenca;
	registro_aberto: { id: number; data_entrada: string } | null;
	data_hoje: string;
	hora_sugerida: string;
}

export interface RegistroPresencaResultado extends EstadoPresenca {
	acao: StatusPresenca;
}

export interface PresencaPendente {
	id: number;
	id_usuario: number;
	nome: string;
	urole: string;
	data_entrada: string;
	data_saida: string;
	confirmacao: Confirmacao;
}

export interface PlantaoPendente {
	id: number;
	id_usuario: number;
	nome: string;
	urole: string;
	data_marcada: string;
	confirmacao: Confirmacao;
}

export interface Pendencias {
	data: string;
	presencas: PresencaPendente[];
	plantoes: PlantaoPendente[];
}

export interface ConfirmacaoItem {
	id: number;
	confirmacao: Exclude<Confirmacao, 'aberto'>;
}
