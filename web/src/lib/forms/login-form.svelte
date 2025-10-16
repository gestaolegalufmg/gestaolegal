<script lang="ts">
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import { Button } from '$lib/components/ui/button';
	import type { SuperForm } from 'sveltekit-superforms';
	import type { LoginData } from './schemas/login-schema';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';

	let { form }: { form: SuperForm<LoginData> } = $props();

	const { form: formData, enhance, delayed } = form;
</script>

<form method="POST" action="?/login" use:enhance class="space-y-8">
	<SimpleInput
		{form}
		name="email"
		label="Email"
		bind:value={$formData.email}
		autocomplete="email"
	/>
	<SimpleInput
		{form}
		name="password"
		type="password"
		label="Senha"
		bind:value={$formData.password}
		autocomplete="current-password"
	/>
	<Button type="submit" class="h-12 w-full">
		{#if $delayed}
			<div class="flex items-center gap-2">
				<span>Carregando...</span>
				<LoaderCircle class="h-4 w-4 animate-spin" />
			</div>
		{:else}
			Entrar
		{/if}
	</Button>
</form>
