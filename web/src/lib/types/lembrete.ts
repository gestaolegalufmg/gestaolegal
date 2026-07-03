export type Lembrete = {
	id: number;
	num_lembrete: number | null;
	id_caso: number;
	data_criacao: string;
	data_lembrete: string;
	descricao: string;
	status: boolean;
	criador?: { id: number; nome: string } | null;
	usuario?: { id: number; nome: string } | null;
};
