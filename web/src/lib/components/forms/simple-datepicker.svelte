<script lang="ts" module>
	import type { FormPath } from 'sveltekit-superforms';

	type T = Record<string, unknown>;
	type U = unknown;
</script>

<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import DatePicker from '$lib/components/date-picker.svelte';
	import type { FieldProps } from 'formsnap';

	let {
		form,
		label,
		name,
		value = $bindable(),
		placeholder
	}: FieldProps<T, U> & {
		label?: string;
		value: any;
		placeholder?: string;
	} = $props();
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			<DatePicker
				{...props}
				label={label ?? name.charAt(0).toUpperCase() + name.slice(1)}
				bind:value
				{placeholder}
			/>
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
