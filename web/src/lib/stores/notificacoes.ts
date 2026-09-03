import { writable } from 'svelte/store';

/** Contador de notificações não lidas do usuário logado (sino do cabeçalho). */
export const naoLidas = writable(0);
