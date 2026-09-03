/** Telas acessíveis sem estar autenticado. */
const ROTAS_PUBLICAS = ['/login', '/setup-admin', '/esqueci-a-senha', '/redefinir-senha'];

/** Se a rota dispensa sessão (o prefixo cobre /redefinir-senha/<token>). */
export function ehRotaPublica(pathname: string): boolean {
	return ROTAS_PUBLICAS.some((rota) => pathname === rota || pathname.startsWith(`${rota}/`));
}
