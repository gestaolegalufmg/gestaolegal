export type Historico = {
	id: number;
	data: string;
	acao: string | null;
	descricao: string | null;
	usuario?: { id: number; nome: string } | null;
};
