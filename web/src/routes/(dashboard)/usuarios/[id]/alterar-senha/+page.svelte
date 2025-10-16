<script lang="ts">
	import PasswordForm from '$lib/forms/password-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';

	let { data }: { data: PageData } = $props();

	const isAdmin = $derived(data.me?.urole === 'admin');
	const isOwnProfile = $derived(data.me?.id === data.user.id);

	function onError(error: any) {
		toast.error('Erro ao alterar senha');
	}
</script>

<div class="min-h-screen bg-background">
	<div class="mx-auto max-w-2xl py-6">
		<PasswordForm
			data={data.form}
			{isAdmin}
			{isOwnProfile}
			userName={data.user.nome}
			userEmail={data.user.email}
			userId={data.user.id}
			{onError}
		/>
	</div>
</div>
