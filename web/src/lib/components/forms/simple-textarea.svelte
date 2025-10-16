<script lang="ts" module>
	import type { FormPath } from 'sveltekit-superforms';

	type T = Record<string, unknown>;
	type U = unknown;
</script>

<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import Textarea from '$lib/components/ui/textarea/textarea.svelte';
	import type { FieldProps } from 'formsnap';

	let {
		form,
		label,
		name,
		value = $bindable(),
		placeholder,
		rows = 3
	}: FieldProps<T, U> & {
		label?: string;
		value: any;
		placeholder?: string;
		rows?: number;
	} = $props();

	placeholder = placeholder ?? `Digite o ${name}`;
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			<Textarea bind:value {...props} {placeholder} {rows} />
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
