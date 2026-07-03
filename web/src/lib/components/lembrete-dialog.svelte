<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Label } from '$lib/components/ui/label';
	import { Input } from '$lib/components/ui/input';
	import * as Select from '$lib/components/ui/select';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import type { Lembrete } from '$lib/types';
	import type { Paginated, User } from '$lib/types';

	let {
		casoId,
		lembrete = null,
		open = $bindable(false),
		onSuccess
	}: {
		casoId: number;
		lembrete?: Lembrete | null;
		open?: boolean;
		onSuccess?: () => void | Promise<void>;
	} = $props();

	const isEdit = $derived(!!lembrete);

	let descricao = $state('');
	let dataLembrete = $state('');
	let idUsuario = $state<string>('');
	let usuarios = $state<User[]>([]);
	let submitting = $state(false);

	function toDateInput(value: string | null | undefined): string {
		if (!value) return '';
		return new Date(value).toISOString().slice(0, 10);
	}

	async function loadUsuarios() {
		try {
			const data = await api.get<Paginated<User>>('user?per_page=100');
			usuarios = data.items;
		} catch {
			toast.error('Erro ao carregar usuários');
		}
	}

	$effect(() => {
		if (open) {
			loadUsuarios();
			descricao = lembrete?.descricao ?? '';
			dataLembrete = toDateInput(lembrete?.data_lembrete);
			idUsuario = lembrete?.usuario?.id ? String(lembrete.usuario.id) : '';
		}
	});

	const selectedUsuarioNome = $derived(
		usuarios.find((u) => String(u.id) === idUsuario)?.nome ?? 'Selecione o usuário'
	);

	async function handleSubmit() {
		if (!descricao || !dataLembrete || !idUsuario) {
			toast.error('Preencha todos os campos');
			return;
		}
		submitting = true;
		try {
			const payload = {
				id_usuario: Number(idUsuario),
				data_lembrete: `${dataLembrete}T00:00:00`,
				descricao
			};
			if (isEdit && lembrete) {
				await api.put(`caso/${casoId}/lembretes/${lembrete.id}`, payload);
				toast.success('Lembrete atualizado com sucesso!');
			} else {
				await api.post(`caso/${casoId}/lembretes`, payload);
				toast.success('Lembrete criado com sucesso!');
			}
			open = false;
			await onSuccess?.();
		} catch {
			toast.error('Erro ao salvar lembrete');
		} finally {
			submitting = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-w-lg">
		<Dialog.Header>
			<Dialog.Title>{isEdit ? 'Editar Lembrete' : 'Novo Lembrete'}</Dialog.Title>
			<Dialog.Description>
				Crie um lembrete/tarefa e atribua a um usuário responsável.
			</Dialog.Description>
		</Dialog.Header>

		<div class="space-y-4 py-2">
			<div class="space-y-2">
				<Label for="lembrete-descricao">Descrição da tarefa</Label>
				<Textarea
					id="lembrete-descricao"
					bind:value={descricao}
					placeholder="Descreva a tarefa..."
					rows={3}
				/>
			</div>

			<div class="space-y-2">
				<Label for="lembrete-data">Data de notificação</Label>
				<Input id="lembrete-data" type="date" bind:value={dataLembrete} />
			</div>

			<div class="space-y-2">
				<Label>Usuário responsável</Label>
				<Select.Root type="single" bind:value={idUsuario}>
					<Select.Trigger class="w-full">{selectedUsuarioNome}</Select.Trigger>
					<Select.Content>
						{#each usuarios as usuario}
							<Select.Item value={String(usuario.id)}>{usuario.nome}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)}>Cancelar</Button>
			<Button onclick={handleSubmit} disabled={submitting}>
				{submitting ? 'Salvando...' : isEdit ? 'Salvar' : 'Criar Lembrete'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
