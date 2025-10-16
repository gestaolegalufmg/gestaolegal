<script lang="ts">
	import Textarea from '../ui/textarea/textarea.svelte';

	let {
		id,
		label,
		value,
		placeholder,
		required = false,
		disabled = false,
		rows = 3,
		class: className = ''
	}: {
		id: string;
		label: string;
		value: any;
		placeholder?: string;
		required?: boolean;
		disabled?: boolean;
		rows?: number;
		class?: string;
	} = $props();
</script>

<div class={className}>
	<label for={id} class="text-sm font-medium">{label}</label>
	<Textarea {id} bind:value {placeholder} {required} {disabled} {rows} />
</div>
