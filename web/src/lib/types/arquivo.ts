/** Arquivo geral da organização (módulo "Arquivos"). */
export type Arquivo = {
	id: number;
	titulo: string;
	descricao: string | null;
	/** Nome original do arquivo enviado. */
	nome: string;
	caminho: string | null;
	data_criacao: string | null;
	id_criado_por: number | null;
};

/** Item da listagem, com o nome de quem cadastrou. */
export type ListArquivo = Arquivo & { criado_por: string | null };

/** Papéis que cadastram e editam arquivos (mesma regra do backend). */
export const ARQUIVO_PAPEIS_EDITAM = ['admin', 'prof', 'colab_proj', 'colab_ext'];
/** Papéis que excluem arquivos. */
export const ARQUIVO_PAPEIS_EXCLUEM = ['admin', 'prof', 'colab_proj'];
