<script lang="ts">
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import type { Arquivo } from '$lib/types';
	import { mensagemDeErro } from '$lib/utils/erros';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';

	let { arquivo = null }: { arquivo?: Arquivo | null } = $props();

	const isEdit = $derived(!!arquivo);

	let titulo = $state(arquivo?.titulo ?? '');
	let descricao = $state(arquivo?.descricao ?? '');
	let file = $state<File | null>(null);
	let submitting = $state(false);

	const TITULO_MAX = 150;
	const DESCRICAO_MAX = 8000;
	const TAMANHO_MAX = 10 * 1024 * 1024;

	function onFileChange(e: Event) {
		file = (e.currentTarget as HTMLInputElement).files?.[0] ?? null;
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!titulo.trim()) return toast.error('Informe o título do arquivo');
		if (titulo.trim().length > TITULO_MAX)
			return toast.error(`O título deve ter no máximo ${TITULO_MAX} caracteres`);
		if (descricao.length > DESCRICAO_MAX)
			return toast.error(`A descrição deve ter no máximo ${DESCRICAO_MAX} caracteres`);
		if (!isEdit && !file) return toast.error('Você precisa adicionar um arquivo');
		if (file && file.size > TAMANHO_MAX)
			return toast.error('O arquivo excede o tamanho máximo de 10 MB');

		const fd = new FormData();
		fd.append('titulo', titulo.trim());
		fd.append('descricao', descricao);
		if (file) fd.append('arquivo', file);

		submitting = true;
		try {
			const salvo = isEdit
				? await api.put<Arquivo>(`arquivo/${arquivo!.id}`, fd, { headers: {} })
				: await api.post<Arquivo>('arquivo/', fd, { headers: {} });
			toast.success(isEdit ? 'Arquivo editado' : 'Arquivo adicionado');
			await goto(`/arquivos/${salvo.id}`);
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao salvar arquivo'));
		} finally {
			submitting = false;
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-6">
	<div class="space-y-2">
		<Label for="arquivo-titulo">Título *</Label>
		<Input
			id="arquivo-titulo"
			bind:value={titulo}
			maxlength={TITULO_MAX}
			placeholder="Ex.: Regimento interno"
		/>
	</div>

	<div class="space-y-2">
		<Label for="arquivo-descricao">Descrição</Label>
		<Textarea
			id="arquivo-descricao"
			bind:value={descricao}
			rows={5}
			maxlength={DESCRICAO_MAX}
			placeholder="Descreva o conteúdo do arquivo (opcional)"
		/>
	</div>

	<div class="space-y-2">
		<Label for="arquivo-file">{isEdit ? 'Substituir arquivo' : 'Arquivo *'}</Label>
		<Input id="arquivo-file" type="file" onchange={onFileChange} />
		<p class="text-sm text-muted-foreground">
			{#if isEdit && arquivo}
				Arquivo atual: <span class="font-medium">{arquivo.nome}</span>. Envie um novo apenas se
				quiser substituí-lo.
			{:else}
				Qualquer tipo de arquivo, até 10 MB.
			{/if}
		</p>
	</div>

	<div class="flex justify-end gap-2">
		<Button variant="outline" href={isEdit && arquivo ? `/arquivos/${arquivo.id}` : '/arquivos'}
			>Cancelar</Button
		>
		<Button type="submit" disabled={submitting}>
			{submitting ? 'Salvando...' : isEdit ? 'Salvar' : 'Cadastrar'}
		</Button>
	</div>
</form>
