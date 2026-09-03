import { ApiException } from '$lib/types';

/**
 * Mensagem para exibir ao usuário a partir de um erro de chamada à API.
 * Erros de permissão (403) e demais erros tratados pelo backend já chegam em
 * português; para qualquer outra falha usa-se o texto padrão informado.
 */
export function mensagemDeErro(err: unknown, padrao: string): string {
	if (err instanceof ApiException && err.message) return err.message;
	return padrao;
}
