/**
 * Item de navegação que só aparece para alguns papéis. A autorização de
 * verdade é feita no backend; esconder o item é só UX.
 */
export type ItemComPapeis = {
	roles?: string[];
};

/** Se o papel do usuário enxerga o item (sem `roles` = todos enxergam). */
export function podeVer(item: ItemComPapeis, urole: string): boolean {
	return !item.roles || item.roles.includes(urole);
}
