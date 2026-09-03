import { apiFetch } from '$lib/api-client';
import { ApiException } from '$lib/types';

/** Baixa um arquivo autenticado da API e dispara o download no navegador. */
export async function baixarArquivoDaApi(endpoint: string, nomeSugerido: string): Promise<void> {
	const response = await apiFetch(endpoint);
	if (!response.ok) {
		let mensagem = 'Erro ao baixar arquivo';
		try {
			mensagem = (await response.json())?.error?.message ?? mensagem;
		} catch {
			/* resposta sem corpo JSON */
		}
		throw new ApiException(mensagem, undefined, undefined, response.status);
	}
	const blob = await response.blob();
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = nomeSugerido || 'arquivo';
	document.body.appendChild(a);
	a.click();
	a.remove();
	window.URL.revokeObjectURL(url);
}
