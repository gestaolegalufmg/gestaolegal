export type OrientacaoJuridica = {
	id: number;
	area_direito: string;
	sub_area?: string | null;
	descricao: string;
	data_criacao?: string | null;
	status: boolean;
	usuario?: {
		id: number;
		nome: string;
	} | null;
	atendidos?: Array<{
		id: number;
		nome: string;
	}>;
};

export type PaginatedOrientacoesJuridicas = {
	items: OrientacaoJuridica[];
	total: number;
	page: number;
	pages: number;
	per_page: number;
};
