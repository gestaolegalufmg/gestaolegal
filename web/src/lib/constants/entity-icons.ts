import BriefcaseIcon from '@lucide/svelte/icons/briefcase';
import UsersIcon from '@lucide/svelte/icons/users';
import FileTextIcon from '@lucide/svelte/icons/file-text';
import Building2Icon from '@lucide/svelte/icons/building-2';
import type { Component } from 'svelte';

export type EntityType = 'atendido' | 'caso' | 'orientacao_juridica' | 'usuario';

export const ENTITY_ICONS: Record<EntityType, Component> = {
	atendido: UsersIcon,
	caso: BriefcaseIcon,
	orientacao_juridica: FileTextIcon,
	usuario: UsersIcon
};

export function getEntityIcon(type: string): Component {
	return ENTITY_ICONS[type as EntityType] || FileTextIcon;
}

export const ENTITY_LABELS: Record<EntityType, string> = {
	atendido: 'Atendido',
	caso: 'Caso',
	orientacao_juridica: 'Orientação Jurídica',
	usuario: 'Usuário'
};

export function getEntityLabel(type: string): string {
	return ENTITY_LABELS[type as EntityType] || '';
}
