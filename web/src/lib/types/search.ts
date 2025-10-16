import type { Atendido } from './atendido';
import type { Caso } from './caso';
import type { OrientacaoJuridica } from './orientacao-juridica';
import type { User } from './user';

export interface SearchResultGroup<T> {
	items: T[];
	total: number;
}

export interface SearchResults {
	atendidos: SearchResultGroup<Atendido>;
	casos: SearchResultGroup<Caso>;
	orientacoes_juridicas: SearchResultGroup<OrientacaoJuridica>;
	usuarios: SearchResultGroup<User>;
}

export interface SearchResponse {
	query: string;
	results: SearchResults;
}

export interface SearchResultItem {
	id: number;
	title: string;
	subtitle?: string;
	type: 'atendido' | 'caso' | 'orientacao_juridica' | 'usuario';
	url: string;
}
