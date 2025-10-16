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
		options,
		maxDisplayItems = 3
	}: FieldProps<T, U> & {
		label?: string;
		value: string[];
		placeholder?: string;
		options: readonly { value: string; label: string }[];
		maxDisplayItems?: number;
	} = $props();

	placeholder = placeholder ?? `Selecione ${name}`;

	let selectedOptionsLabels = $derived(
		options.filter((option) => value?.includes(option.value)).map((option) => option.label)
	);

	let displayText = $derived.by(() => {
		if (!value || value.length === 0) {
			return placeholder;
		}

		if (selectedOptionsLabels.length === 0) {
			return placeholder;
		}

		if (selectedOptionsLabels.length <= maxDisplayItems) {
			return selectedOptionsLabels.join(', ');
		}

		const displayedLabels = selectedOptionsLabels.slice(0, maxDisplayItems);
		const remainingCount = selectedOptionsLabels.length - maxDisplayItems;
		return `${displayedLabels.join(', ')} +${remainingCount} mais`;
	});
</script>

<Form.Field {form} {name}>
	<Form.Control>
		{#snippet children({ props })}
			<Form.Label>{label ?? name.charAt(0).toUpperCase() + name.slice(1)}</Form.Label>
			<Select.Root bind:value type="multiple" {...props}>
				<Select.Trigger class="w-full" {...props}>
					<span class="truncate text-left">
						{displayText}
					</span>
				</Select.Trigger>
				<Select.Content>
					{#each options as option}
						<Select.Item value={option.value}>
							{#snippet children({ selected })}
								{option.label}
								{#if selected}
									<div class="ml-auto">
										<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
											<path
												fill-rule="evenodd"
												d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
												clip-rule="evenodd"
											/>
										</svg>
									</div>
								{/if}
							{/snippet}
						</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		{/snippet}
	</Form.Control>
	<Form.FieldErrors />
</Form.Field>
