<script lang="ts">
	/**
	 * Rodapé institucional: crédito ao LabP² e logos (brancos, sobre fundo
	 * escuro) do LabP², da Faculdade de Direito e da UFMG.
	 */
	let { class: className = '' }: { class?: string } = $props();
</script>

<footer class="bg-slate-900 text-slate-300 {className}">
	<div
		class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 gap-y-3 px-6 py-3"
	>
		<p class="text-xs">
			Desenvolvido por
			<a
				href="https://labp2.direito.ufmg.br/"
				target="_blank"
				rel="noopener noreferrer"
				class="font-semibold text-white underline-offset-2 hover:underline">LabP²</a
			>
			· Faculdade de Direito da UFMG
		</p>
		<div class="flex items-center gap-5 opacity-70 transition-opacity hover:opacity-100">
			<a
				href="https://labp2.direito.ufmg.br/"
				target="_blank"
				rel="noopener noreferrer"
				title="LabP²"
			>
				<img src="/logos/labp2-branco.png" alt="LabP²" class="h-9 w-auto" />
			</a>
			<a
				href="https://www.direito.ufmg.br/"
				target="_blank"
				rel="noopener noreferrer"
				title="Faculdade de Direito da UFMG"
			>
				<img src="/logos/fdufmg-branco.png" alt="Faculdade de Direito da UFMG" class="h-8 w-auto" />
			</a>
			<a href="https://ufmg.br/" target="_blank" rel="noopener noreferrer" title="UFMG">
				<img src="/logos/ufmg-branco.png" alt="UFMG" class="h-6 w-auto" />
			</a>
		</div>
	</div>
</footer>
