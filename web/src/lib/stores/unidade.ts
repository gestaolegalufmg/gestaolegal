import { get, writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { Unidade } from '$lib/types';

/** Chave do localStorage onde a unidade ativa sobrevive ao reload. */
const CHAVE = 'unidade_ativa';

function lerGuardada(): number | null {
	if (!browser) return null;

	const bruto = localStorage.getItem(CHAVE);
	if (!bruto) return null;

	const id = Number(bruto);
	return Number.isInteger(id) && id > 0 ? id : null;
}

/** Id da unidade ativa. Todo `apiFetch` manda esse valor em `X-Unidade-Id`. */
export const unidadeAtiva = writable<number | null>(lerGuardada());

/** Define (ou limpa) a unidade ativa, persistindo no localStorage. */
export function definirUnidadeAtiva(id: number | null): void {
	unidadeAtiva.set(id);

	if (!browser) return;

	if (id === null) {
		localStorage.removeItem(CHAVE);
	} else {
		localStorage.setItem(CHAVE, String(id));
	}
}

/** Id da unidade ativa fora de componente (usado pelo api-client). */
export function unidadeAtivaId(): number | null {
	return get(unidadeAtiva);
}

/**
 * Só as unidades ativas da lista. `user/me` devolve todo vínculo do usuário,
 * inclusive com unidade desativada; quem navega (seletor e store) só pode
 * oferecer as ativas, porque a API recusa `X-Unidade-Id` de unidade inativa.
 */
export function unidadesAtivas(unidades: Unidade[] | undefined | null): Unidade[] {
	return (unidades ?? []).filter((unidade) => unidade.ativa);
}

/**
 * Concilia a unidade guardada com as unidades ativas do usuário logado: mantém
 * a guardada quando ela ainda está entre elas, senão cai para a primeira ativa.
 * Devolve o id resultante (null quando o usuário não tem unidade ativa
 * nenhuma).
 */
export function sincronizarUnidades(unidades: Unidade[] | undefined | null): number | null {
	const disponiveis = unidadesAtivas(unidades);

	if (disponiveis.length === 0) {
		definirUnidadeAtiva(null);
		return null;
	}

	const guardada = get(unidadeAtiva);
	const valida = disponiveis.some((unidade) => unidade.id === guardada);
	const escolhida = valida ? guardada! : disponiveis[0].id;

	definirUnidadeAtiva(escolhida);
	return escolhida;
}
