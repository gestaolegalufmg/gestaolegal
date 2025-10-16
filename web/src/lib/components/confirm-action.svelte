<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { Button } from '$lib/components/ui/button';
	import type { Snippet } from 'svelte';
	import { buttonVariants, type ButtonSize, type ButtonVariant } from './ui/button';

	let {
		title = 'Você tem certeza??',
		description = 'Por favor, confirme que deseja realizar esta ação.',
		confirmText = 'Confirmar',
		cancelText = 'Cancelar',
		onConfirm,
		triggerText,
		buttonVariant = 'destructive',
		buttonSize = 'sm',
		trigger,
		triggerClass
	}: {
		title?: string;
		description?: string;
		confirmText?: string;
		cancelText?: string;
		triggerText?: string;
		onConfirm: () => void | Promise<void>;
		buttonVariant?: ButtonVariant;
		buttonSize?: ButtonSize;
		trigger?: Snippet;
		triggerClass?: string;
	} = $props();

	let open = $state(false);

	async function handleConfirm() {
		await onConfirm();
		open = false;
	}
</script>

<AlertDialog.Root bind:open>
	<AlertDialog.Trigger
		class={triggerClass || buttonVariants({ variant: buttonVariant, size: buttonSize })}
	>
		{#if trigger}
			{@render trigger()}
		{:else}
			{triggerText}
		{/if}
	</AlertDialog.Trigger>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{title}</AlertDialog.Title>
			<AlertDialog.Description>
				{description}
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel>{cancelText}</AlertDialog.Cancel>
			<Button variant={buttonVariant} size={buttonSize} onclick={handleConfirm}>
				{confirmText}
			</Button>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
