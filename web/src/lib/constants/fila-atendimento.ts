import { FilaPrioridade } from '$lib/types/fila-atendimento';

export interface PrioridadeOption {
	value: number;
	label: string;
	descricao: string;
}

export const PRIORIDADE_OPTIONS: PrioridadeOption[] = [
	{
		value: FilaPrioridade.NORMAL,
		label: 'Normal',
		descricao: 'Público em geral'
	},
	{
		value: FilaPrioridade.PRIORIDADE,
		label: 'Prioridade',
		descricao:
			'Idosos até 80 anos; pessoas com deficiência; gestantes; lactantes; pessoas com crianças de colo e obesos'
	},
	{
		value: FilaPrioridade.SUPER_PRIORIDADE,
		label: 'Super Prioridade',
		descricao: 'Idosos acima de 80 anos.'
	}
];

const PRIORIDADE_LABELS: Record<number, string> = {
	[FilaPrioridade.NORMAL]: 'Normal',
	[FilaPrioridade.PRIORIDADE]: 'Prioridade',
	[FilaPrioridade.SUPER_PRIORIDADE]: 'Super Prioridade'
};

export function getPrioridadeLabel(prioridade: number): string {
	return PRIORIDADE_LABELS[prioridade] ?? 'Normal';
}

/** Classe de fundo da linha da fila conforme o grau de prioridade. */
export function getPrioridadeRowClass(prioridade: number): string {
	switch (prioridade) {
		case FilaPrioridade.SUPER_PRIORIDADE:
			return 'bg-orange-100 hover:bg-orange-200/70 dark:bg-orange-950/40 dark:hover:bg-orange-950/60';
		case FilaPrioridade.PRIORIDADE:
			return 'bg-blue-100 hover:bg-blue-200/70 dark:bg-blue-950/40 dark:hover:bg-blue-950/60';
		default:
			return 'hover:bg-muted/50';
	}
}
