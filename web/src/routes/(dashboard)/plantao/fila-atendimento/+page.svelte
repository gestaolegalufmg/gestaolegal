<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Fila de Atendimento</h1>
		<p class="text-muted-foreground">Gerencie a fila de pessoas aguardando atendimento</p>
	</div>

	<div class="grid gap-6">
		<div class="rounded-lg border bg-card p-6">
			<div class="mb-4 flex items-center justify-between">
				<h2 class="text-xl font-semibold">Fila Atual</h2>
				<div class="flex gap-2">
					<button
						class="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
					>
						Adicionar à Fila
					</button>
					<button
						class="rounded-md bg-secondary px-4 py-2 text-secondary-foreground hover:bg-secondary/90"
					>
						Chamar Próximo
					</button>
				</div>
			</div>

			<div class="space-y-3">
				<div class="rounded-lg border bg-green-50 p-4">
					<div class="flex items-center justify-between">
						<div>
							<h3 class="font-medium">#001 - João Silva</h3>
							<p class="text-sm text-muted-foreground">CPF: 123.456.789-00</p>
							<p class="text-sm text-muted-foreground">Tipo: Atendimento Jurídico</p>
						</div>
						<div class="text-right">
							<p class="text-sm font-medium">Em Atendimento</p>
							<p class="text-xs text-muted-foreground">Iniciado: 14:30</p>
						</div>
					</div>
				</div>

				<div class="rounded-lg border p-4">
					<div class="flex items-center justify-between">
						<div>
							<h3 class="font-medium">#002 - Maria Santos</h3>
							<p class="text-sm text-muted-foreground">CPF: 987.654.321-00</p>
							<p class="text-sm text-muted-foreground">Tipo: Assistência Judiciária</p>
						</div>
						<div class="text-right">
							<p class="text-sm font-medium">Aguardando</p>
							<p class="text-xs text-muted-foreground">Posição: 1</p>
						</div>
					</div>
				</div>

				<div class="rounded-lg border p-4">
					<div class="flex items-center justify-between">
						<div>
							<h3 class="font-medium">#003 - Pedro Costa</h3>
							<p class="text-sm text-muted-foreground">CPF: 456.789.123-00</p>
							<p class="text-sm text-muted-foreground">Tipo: Orientação Jurídica</p>
						</div>
						<div class="text-right">
							<p class="text-sm font-medium">Aguardando</p>
							<p class="text-xs text-muted-foreground">Posição: 2</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
