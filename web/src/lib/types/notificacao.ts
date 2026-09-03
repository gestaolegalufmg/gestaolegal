/** Notificação interna (módulo "Notificações"). */
export type Notificacao = {
	id: number;
	acao: string;
	data: string;
	data_criacao: string | null;
	id_executor_acao: number | null;
	/** Nulo = aviso geral (abertura do plantão). */
	id_usu_notificar: number | null;
	tipo: 'caso' | 'evento' | 'lembrete' | 'plantao' | null;
	id_caso: number | null;
	id_referencia: number | null;
	lida: boolean;
	/** Nome de quem executou a ação. */
	executor: string | null;
};

/** Página de destino da notificação, conforme o tipo. */
export function destinoDaNotificacao(n: Notificacao): string | null {
	switch (n.tipo) {
		case 'caso':
			return n.id_caso ? `/casos/${n.id_caso}` : null;
		case 'evento':
			return n.id_caso && n.id_referencia ? `/casos/${n.id_caso}/eventos/${n.id_referencia}` : null;
		case 'lembrete':
			return n.id_caso ? `/casos/${n.id_caso}` : null;
		case 'plantao':
			return '/plantao/escala';
		default:
			return null;
	}
}
