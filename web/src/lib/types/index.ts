// API response types
export type { ApiResponse, ApiError } from './api-response';
export { ApiException } from './api-response';

// Domain types
export type { User } from './user';
export type { OrientacaoJuridica } from './orientacao-juridica';
export type { Atendido, ListAtendido } from './atendido';
export type { Paginated, PaginationMeta } from './paginated';
export type { Endereco } from './endereco';
export type { Caso, ListCaso } from './caso';
export type { Processo, ListProcesso, ProcessoCreateInput, ProcessoUpdateInput } from './processo';
export type { SearchResultGroup, SearchResults, SearchResponse, SearchResultItem } from './search';
