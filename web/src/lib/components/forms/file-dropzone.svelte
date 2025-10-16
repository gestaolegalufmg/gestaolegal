<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';
	import { cn, type WithElementRef } from '$lib/utils.js';

	type Props = WithElementRef<HTMLInputAttributes>;

	let { ref = $bindable(null), value = $bindable(), class: className }: Props = $props();
</script>

<input bind:this={ref} class={cn(className)} bind:value type="file" />
