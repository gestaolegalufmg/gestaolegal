<script lang="ts">
	import type { PageProps } from './$types';
	import * as Card from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { AREA_DIREITO_OPTIONS } from '$lib/constants';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { invalidateAll } from '$app/navigation';

	let { data }: PageProps = $props();

	// One editable link value per área do direito, seeded from the saved roteiros.
	let links = $state<Record<string, string>>({});
	let savingArea = $state<string | null>(null);

	$effect(() => {
		const initial: Record<string, string> = {};
		for (const opt of AREA_DIREITO_OPTIONS) {
			const existing = data.roteiros.find((r) => r.area_direito === opt.value);
			initial[opt.value] = existing?.link ?? '';
		}
		links = initial;
	});

	async function save(area: string) {
		savingArea = area;
		try {
			await api.put('roteiro', { area_direito: area, link: links[area] || null });
			toast.success('Roteiro atualizado');
			await invalidateAll();
		} catch {
			toast.error('Erro ao salvar roteiro');
		} finally {
			savingArea = null;
		}
	}
</script>

<div class="max-w-4xl space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Links de Roteiro</h1>
		<p class="mt-2 text-muted-foreground">
			Cadastre o link do roteiro (documento guia) para cada área do direito.
		</p>
	</div>

	<Card.Root>
		<Card.Content class="space-y-4 pt-6">
			{#each AREA_DIREITO_OPTIONS as area}
				<div class="flex items-end gap-3">
					<div class="flex-1 space-y-1">
						<Label for={`link-${area.value}`}>{area.label}</Label>
						<Input
							id={`link-${area.value}`}
							type="url"
							placeholder="https://exemplo.com.br/roteiro"
							bind:value={links[area.value]}
						/>
					</div>
					<Button onclick={() => save(area.value)} disabled={savingArea === area.value}>
						{savingArea === area.value ? 'Salvando...' : 'Salvar'}
					</Button>
				</div>
			{/each}
		</Card.Content>
	</Card.Root>
</div>
