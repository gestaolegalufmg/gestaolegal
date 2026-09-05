// API response types
export type { ApiResponse, ApiError } from './api-response';
export { ApiException } from './api-response';

// Domain types
export type { User, UserOption } from './user';
export type { OrientacaoJuridica } from './orientacao-juridica';
export type {
	AssistenciaJudiciaria,
	ListAssistenciaJudiciaria,
	OrientacaoResumo
} from './assistencia-judiciaria';
export type { Lembrete } from './lembrete';
export type { Historico } from './historico';
export type { Roteiro } from './roteiro';
export type { Arquivo, ListArquivo } from './arquivo';
export type { Notificacao, FiltroArquivadas } from './notificacao';
export { destinoDaNotificacao, FILTROS_ARQUIVADAS } from './notificacao';
export { ARQUIVO_PAPEIS_EDITAM, ARQUIVO_PAPEIS_EXCLUEM } from './arquivo';
export type { Atendido, ListAtendido } from './atendido';
export type { Paginated, PaginationMeta } from './paginated';
export type { Endereco } from './endereco';
export type { Unidade } from './unidade';
export type { Caso, ListCaso } from './caso';
export type { Processo, ListProcesso, ProcessoCreateInput, ProcessoUpdateInput } from './processo';
export type { SearchResultGroup, SearchResults, SearchResponse, SearchResultItem } from './search';
export type { FilaItem, FilaHoje, SenhaPreview } from './fila-atendimento';
export { FilaPrioridade, FilaStatus } from './fila-atendimento';
export type {
	JanelaPlantao,
	DiaAberto,
	EscalaItem,
	MinhaMarcacao,
	PaginaPlantao,
	ConfiguracaoPlantao,
	StatusPresenca,
	EstadoPresenca,
	RegistroPresencaResultado,
	PresencaPendente,
	PlantaoPendente,
	Pendencias,
	ConfirmacaoItem,
	Confirmacao
} from './plantao';
export { CONFIRMACAO } from './plantao';
