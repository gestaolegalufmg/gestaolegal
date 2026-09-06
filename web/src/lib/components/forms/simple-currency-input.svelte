<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';

	let {
		form,
		name,
		label,
		value = $bindable(null)
	}: FieldProps<T, U> & {
		label: string;
		value: number | null | undefined;
	} = $props();
	const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
	const formatar = (numero: number | null | undefined) =>
		numero == null ? '' : moeda.format(numero);
	function digitar(event: Event & { currentTarget: HTMLInputElement }) {
		const texto = event.currentTarget.value;
		const digitos = texto.replace(/\D/g, '');
		if (digitos.length <= 15) {
			value = digitos ? (Number(digitos) / 100) * (texto.includes('-') ? -1 : 1) : null;
		}
		event.currentTarget.value = formatar(value);
	}
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label}</Form.Label>
			<input
				{...props}
				name={undefined}
				type="text"
				inputmode="decimal"
				placeholder="R$ 0,00"
				value={formatar(value)}
				oninput={digitar}
				class="h-9 w-full min-w-0 rounded-md border border-input bg-background px-3 py-1 text-base shadow-xs focus-visible:ring-2 focus-visible:ring-ring md:text-sm"
			/>
			<input type="hidden" {name} value={value ?? ''} />
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
