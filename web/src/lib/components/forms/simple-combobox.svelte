<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import { Combobox } from 'bits-ui';
	import * as Form from '$lib/components/ui/form';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';
	import { ChevronDown, X } from '@lucide/svelte';

	let {
		form,
		name,
		label,
		value = $bindable(''),
		options,
		placeholder = 'Digite para buscar...',
		selectedLabel,
		optional = false
	}: FieldProps<T, U> & {
		label: string;
		value: string;
		options: { value: string; label: string }[];
		placeholder?: string;
		selectedLabel?: string;
		optional?: boolean;
	} = $props();
	let search = $state('');
	let open = $state(false);
	const labelAtual = $derived(
		value ? (options.find((option) => option.value === value)?.label ?? selectedLabel ?? '') : ''
	);
	const normalizar = (texto: string) =>
		texto
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '')
			.toLocaleLowerCase();
	const filtered = $derived(
		options.filter((option) => normalizar(option.label).includes(normalizar(search)))
	);
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label}</Form.Label>
			<Combobox.Root
				type="single"
				bind:value
				bind:open
				{name}
				items={options}
				inputValue={open ? search : labelAtual}
				allowDeselect={false}
				onOpenChange={(opened) => {
					if (!opened) search = '';
				}}
			>
				<div class="flex w-full items-center gap-1">
					<Combobox.Input
						{...props}
						name={undefined}
						{placeholder}
						clearOnDeselect
						class="h-9 w-full min-w-0 rounded-md border border-input bg-background px-3 text-sm focus-visible:ring-2 focus-visible:ring-ring"
						oninput={(event) => {
							search = event.currentTarget.value;
							open = true;
						}}
					/>
					<Combobox.Trigger
						type="button"
						class="shrink-0 rounded-md p-2 hover:bg-muted"
						aria-label={`Abrir opções de ${label}`}
					>
						<ChevronDown class="size-4" />
					</Combobox.Trigger>
					{#if optional && value}
						<button
							type="button"
							class="shrink-0 rounded-md p-2 hover:bg-muted"
							aria-label={`Limpar ${label}`}
							onclick={() => {
								value = '';
								search = '';
							}}><X class="size-4" /></button
						>
					{/if}
				</div>
				<Combobox.Portal>
					<Combobox.Content
						sideOffset={4}
						class="z-50 max-h-72 w-(--bits-combobox-anchor-width) min-w-60 overflow-y-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md"
					>
						{#each filtered as option (option.value)}
							<Combobox.Item
								value={option.value}
								label={option.label}
								class="cursor-pointer rounded-sm px-3 py-2 text-sm data-[highlighted]:bg-accent data-[selected]:font-semibold"
								>{option.label}</Combobox.Item
							>
						{:else}
							<p class="px-3 py-2 text-sm text-muted-foreground">Nenhum usuário encontrado.</p>
						{/each}
					</Combobox.Content>
				</Combobox.Portal>
			</Combobox.Root>
			{#if value && !options.some((option) => option.value === value)}
				<p class="text-sm text-muted-foreground">
					Vínculo atual preservado: {labelAtual}. Escolha outro usuário para substituí-lo.
				</p>
			{/if}
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
