<script lang="ts">
	import UserForm from '$lib/forms/user-form.svelte';
	import type { PageProps } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: PageProps = $props();
	const { me } = data;
	const isAdmin = $derived(me.urole === 'admin');

	function onUpdate() {
		toast.success('Usuário criado com sucesso');
	}

	function onError(error: any) {
		toast.error('Erro ao criar usuário');
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-4xl py-1">
		{#if isAdmin}
			<div class="mb-8">
				<div class="flex items-center justify-between">
					<div>
						<h1 class="text-3xl font-bold tracking-tight text-foreground">Novo Usuário</h1>
						<p class="mt-2 text-muted-foreground">Cadastre um novo usuário no sistema</p>
					</div>
					<Button variant="outline" href="/usuarios">Voltar</Button>
				</div>
			</div>
			<UserForm data={data.form} isCreateMode={true} {onError} />
		{:else}
			<p class="text-muted-foreground">Você não tem permissão para criar usuários.</p>
		{/if}
	</div>
</div>
