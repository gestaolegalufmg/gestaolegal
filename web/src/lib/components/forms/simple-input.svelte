<script lang="ts" module>
	import type { FormPath } from 'sveltekit-superforms';
</script>

<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import { Input } from '$lib/components/ui/input';
	import type { FieldProps } from 'formsnap';
	import type { FullAutoFill, HTMLInputTypeAttribute } from 'svelte/elements';

	let {
		form,
		name,
		label,
		value = $bindable(),
		pattern,
		placeholder,
		type,
		autocomplete,
		disabled,
		files = $bindable(undefined)
	}: FieldProps<T, U> & {
		type?: HTMLInputTypeAttribute;
		pattern?: string;
		value: any;
		name: string;
		label: string;
		placeholder?: string;
		autocomplete?: FullAutoFill;
		disabled?: boolean;
		files?: FileList;
	} = $props();
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			{#if type === 'file'}
				<Input
					bind:value
					bind:files
					type="file"
					{pattern}
					{placeholder}
					{autocomplete}
					{disabled}
					{...props}
				/>
			{:else}
				<Input bind:value {type} {pattern} {placeholder} {autocomplete} {disabled} {...props} />
			{/if}
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
