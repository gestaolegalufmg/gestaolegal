/**
 * Nome que o usuário enviou, sem o prefixo de unicidade da referência privada.
 *
 * A referência gravada no banco é `<categoria>/<uuid4hex>_<nome>`; só o prefixo
 * de 32 hexadecimais mais o primeiro underscore é gerado, e o resto do nome
 * (underscores inclusive) é do usuário. Referências herdadas da 2.0, sem esse
 * prefixo, voltam inteiras.
 *
 * Espelha `nome_original` de `gestaolegal/services/private_file_storage.py`:
 * mudou lá, mude aqui.
 */
export function nomeOriginalArquivo(ref: string | null | undefined): string {
	if (!ref) return 'arquivo';
	const nome = ref.split('/').pop() ?? '';
	if (!nome) return 'arquivo';
	const separador = nome.indexOf('_');
	if (separador === 32 && /^[0-9a-f]{32}$/.test(nome.slice(0, 32))) {
		return nome.slice(33) || nome;
	}
	return nome;
}
