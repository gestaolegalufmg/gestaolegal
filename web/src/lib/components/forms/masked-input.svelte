<script lang="ts" module>
	import type { FormPath } from 'sveltekit-superforms';
</script>

<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import { Input } from '$lib/components/ui/input';
	import type { FieldProps } from 'formsnap';
	import type { FullAutoFill, HTMLInputTypeAttribute } from 'svelte/elements';

	type MaskType = 'cpf' | 'phone' | 'cellphone' | 'cep' | 'cnpj';

	let {
		form,
		name,
		label,
		value = $bindable(),
		maskType,
		placeholder,
		type = 'text',
		autocomplete
	}: FieldProps<T, U> & {
		type?: HTMLInputTypeAttribute;
		value: any;
		name: string;
		label: string;
		maskType: MaskType;
		placeholder?: string;
		autocomplete?: FullAutoFill;
	} = $props();

	const maxLengths: Record<MaskType, number> = {
		cpf: 11,
		cnpj: 14,
		phone: 10,
		cellphone: 11,
		cep: 8
	};

	function applyMask(val: string, mask: MaskType): string {
		if (!val) return '';

		let numbers = val.replace(/\D/g, '');
		const maxLength = maxLengths[mask];

		if (numbers.length > maxLength) {
			numbers = numbers.substring(0, maxLength);
		}

		switch (mask) {
			case 'cpf':
				return numbers
					.replace(/(\d{3})(\d)/, '$1.$2')
					.replace(/(\d{3})(\d)/, '$1.$2')
					.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
			case 'cnpj':
				return numbers
					.replace(/(\d{2})(\d)/, '$1.$2')
					.replace(/(\d{3})(\d)/, '$1.$2')
					.replace(/(\d{3})(\d)/, '$1/$2')
					.replace(/(\d{4})(\d{1,2})$/, '$1-$2');
			case 'phone':
				return numbers.replace(/(\d{2})(\d)/, '($1) $2').replace(/(\d{4})(\d{1,4})$/, '$1-$2');
			case 'cellphone':
				return numbers.replace(/(\d{2})(\d)/, '($1) $2').replace(/(\d{5})(\d{1,4})$/, '$1-$2');
			case 'cep':
				return numbers.replace(/(\d{5})(\d{1,3})$/, '$1-$2');
		}

		return numbers;
	}

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		const cursorPosition = target.selectionStart || 0;
		const oldValue = value || '';

		const digitsBeforeCursor = oldValue.substring(0, cursorPosition).replace(/\D/g, '').length;

		const newValue = applyMask(target.value, maskType);

		if (newValue === oldValue) {
			return;
		}

		value = newValue;

		let newCursorPosition = 0;
		let digitCount = 0;

		for (let i = 0; i < newValue.length; i++) {
			if (/\d/.test(newValue[i])) {
				digitCount++;
				if (digitCount === digitsBeforeCursor) {
					newCursorPosition = i + 1;
					break;
				}
			}
		}

		if (digitCount < digitsBeforeCursor || digitsBeforeCursor === 0) {
			newCursorPosition = newValue.length;
		}

		setTimeout(() => {
			target.setSelectionRange(newCursorPosition, newCursorPosition);
		}, 0);
	}
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			<Input bind:value {type} {placeholder} {autocomplete} oninput={handleInput} {...props} />
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
