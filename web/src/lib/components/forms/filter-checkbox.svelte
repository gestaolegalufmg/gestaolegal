<script lang="ts" generics="T extends Record<string, unknown>, U extends FormPath<T>">
	import * as Form from '$lib/components/ui/form';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import type { FieldProps } from 'formsnap';
	import type { FormPath } from 'sveltekit-superforms';
	import { cn } from '$lib/utils';

	let {
		form,
		label,
		name,
		value,
		checked = $bindable(false),
		onchange,
		class: className,
		...restProps
	}: FieldProps<T, U> & {
		label: string;
		value: string;
		checked?: boolean;
		onchange?: (checked: boolean) => void;
		class?: string;
	} = $props();
</script>

<Form.Field {form} {name} class="flex items-center">
	<Form.Control>
		{#snippet children({ props })}
			<div class="flex h-fit flex-row-reverse items-center gap-2">
				<Form.Label
					class={cn(
						'flex min-w-fit cursor-pointer items-center gap-2 text-sm select-none',
						className
					)}
				>
					{label}
				</Form.Label>
				<Checkbox
					{...props}
					{value}
					bind:checked
					onCheckedChange={onchange}
					{...restProps}
					class="scale-125"
				/>
			</div>
		{/snippet}
	</Form.Control>
</Form.Field>
