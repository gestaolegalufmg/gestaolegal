<script lang="ts">
	import { cn } from '$lib/utils';
	import { DropdownMenu as DropdownMenuPrimitive } from 'bits-ui';

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: DropdownMenuPrimitive.TriggerProps = $props();
</script>

<DropdownMenuPrimitive.Trigger
	bind:ref
	class={cn('cursor-pointer', className)}
	data-slot="dropdown-menu-trigger"
	{...restProps}
/>
