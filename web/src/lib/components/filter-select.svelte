<script lang="ts">
	import * as Select from '$lib/components/ui/select/index.js';

	let {
		value = $bindable(),
		options,
		placeholder,
		label,
		name,
		onchange
	}: {
		value: string;
		options: { value: string; label: string }[];
		placeholder: string;
		label: string;
		name?: string;
		onchange?: (value: string) => void;
	} = $props();

	const triggerContent = $derived(
		options.find((option) => option.value === value)?.label ?? placeholder
	);

	function handleChange(value: string) {
		if (onchange) {
			onchange(value);
		}
	}
</script>

<Select.Root type="single" {name} bind:value onValueChange={handleChange}>
	<Select.Trigger class="w-[180px]">
		{triggerContent}
	</Select.Trigger>
	<Select.Content>
		<Select.Group>
			<Select.Label>{label}</Select.Label>
			{#each options as option (option.value)}
				<Select.Item value={option.value} label={option.label} disabled={option.value === 'grapes'}>
					{option.label}
				</Select.Item>
			{/each}
		</Select.Group>
	</Select.Content>
</Select.Root>
