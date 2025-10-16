<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { Button } from '$lib/components/ui/button';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Label } from '$lib/components/ui/label';
	import type { Snippet } from 'svelte';
	import { buttonVariants, type ButtonSize, type ButtonVariant } from './ui/button';

	let {
		title = 'Indeferir Caso',
		description = 'Por favor, informe a justificativa para o indeferimento deste caso.',
		confirmText = 'Indeferir',
		cancelText = 'Cancelar',
		onConfirm,
		triggerText,
		buttonVariant = 'destructive',
		buttonSize = 'sm',
		trigger,
		triggerClass,
		open = $bindable(false)
	}: {
		title?: string;
		description?: string;
		confirmText?: string;
		cancelText?: string;
		triggerText?: string;
		onConfirm: (justificativa: string) => void | Promise<void>;
		buttonVariant?: ButtonVariant;
		buttonSize?: ButtonSize;
		trigger?: Snippet;
		triggerClass?: string;
		open?: boolean;
	} = $props();

	let justificativa = $state('');

	async function handleConfirm() {
		await onConfirm(justificativa);
		open = false;
		justificativa = '';
	}

	function handleCancel() {
		justificativa = '';
		open = false;
	}
</script>

<AlertDialog.Root bind:open>
	{#if trigger || triggerText}
		<AlertDialog.Trigger
			class={triggerClass || buttonVariants({ variant: buttonVariant, size: buttonSize })}
		>
			{#if trigger}
				{@render trigger()}
			{:else}
				{triggerText}
			{/if}
		</AlertDialog.Trigger>
	{/if}
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{title}</AlertDialog.Title>
			<AlertDialog.Description>
				{description}
			</AlertDialog.Description>
		</AlertDialog.Header>
		<div class="py-4">
			<Label for="justificativa">Justificativa</Label>
			<Textarea
				id="justificativa"
				bind:value={justificativa}
				placeholder="Digite a justificativa para o indeferimento..."
				class="mt-2"
				rows={4}
			/>
		</div>
		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={handleCancel}>{cancelText}</AlertDialog.Cancel>
			<Button variant={buttonVariant} size={buttonSize} onclick={handleConfirm}>
				{confirmText}
			</Button>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
