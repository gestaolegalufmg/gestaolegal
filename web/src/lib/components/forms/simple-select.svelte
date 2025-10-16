<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import * as Select from '$lib/components/ui/select';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';

	let {
		form,
		label,
		name,
		value = $bindable(),
		placeholder,
		type = 'single',
		options
	}: FieldProps<T, U> & {
		label?: string;
		value: any;
		placeholder?: string;
		type?: 'single' | 'multiple';
		options: readonly { value: string; label: string }[];
	} = $props();

	placeholder = placeholder ?? `Digite o ${name}`;

	let selectedOptionLabel = $derived(options.find((option) => option.value === value)?.label);
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			<Select.Root bind:value {...props} {type}>
				<Select.Trigger class="w-full data-[placeholder]:text-foreground" {...props}>
					{selectedOptionLabel
						? selectedOptionLabel
						: (label ?? name.charAt(0).toUpperCase() + name.slice(1))}
				</Select.Trigger>
				<Select.Content>
					{#each options as option}
						<Select.Item value={option.value}>{option.label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
