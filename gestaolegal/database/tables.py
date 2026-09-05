from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)

metadata = MetaData()

# Unidade padrão (Belo Horizonte), a mesma que a migration atribui aos
# registros herdados. Serve a quem precisa nomear a unidade inicial — o vínculo
# do primeiro usuário e a migration —, NÃO como default de coluna: `coluna_unidade`
# teve o `default=UNIDADE_PADRAO_ID` removido na Fase A, depois que os services
# passaram a gravar a unidade ativa. Sem ele, INSERT sem unidade estoura o NOT NULL
# na hora, em vez de gravar calado em Belo Horizonte um registro de Nova Lima.
UNIDADE_PADRAO_ID = 1


def coluna_unidade() -> Column:
    return Column(
        "unidade_id",
        Integer,
        ForeignKey("unidades.id"),
        nullable=False,
        index=True,
    )

enderecos = Table(
    "enderecos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("logradouro", String(100), nullable=False),
    Column("numero", String(8), nullable=False),
    Column("complemento", String(100), nullable=True),
    Column("bairro", String(100), nullable=False),
    Column("cep", String(9), nullable=False),
    Column("cidade", String(100), nullable=False),
    Column("estado", String(100), nullable=False),
)

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(80), nullable=False, unique=True),
    Column("senha", String(60), nullable=False),
    Column("urole", String(50), nullable=False),
    Column("nome", String(60), nullable=False),
    Column("sexo", String(60), nullable=False),
    Column("rg", String(18), nullable=False),
    Column("cpf", String(14), nullable=False),
    Column("profissao", String(45), nullable=False),
    Column("estado_civil", String(45), nullable=False),
    Column("nascimento", Date, nullable=False),
    Column("telefone", String(18), nullable=True),
    Column("celular", String(18), nullable=False),
    Column("oab", String(30), nullable=True),
    Column("obs", Text, nullable=True),
    Column("data_entrada", Date, nullable=False),
    Column("data_saida", Date, nullable=True),
    Column("criado", DateTime, nullable=False),
    Column("modificado", DateTime, nullable=True),
    Column("criadopor", Integer, nullable=False),
    Column("matricula", String(45), nullable=True),
    Column("modificadopor", Integer, nullable=True),
    Column("bolsista", Boolean, nullable=False),
    Column("tipo_bolsa", String(50), nullable=True),
    Column("horario_atendimento", String(30), nullable=True),
    Column("suplente", String(30), nullable=True),
    Column("ferias", String(150), nullable=True),
    Column("status", Boolean, nullable=False),
    Column("cert_atuacao_DAJ", String(3), nullable=False),
    Column("inicio_bolsa", DateTime, nullable=True),
    Column("fim_bolsa", DateTime, nullable=True),
    Column("endereco_id", Integer, ForeignKey("enderecos.id"), nullable=True),
    Column("chave_recuperacao", Boolean, nullable=True, default=False),
)

atendidos = Table(
    "atendidos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String(80), nullable=False),
    Column("data_nascimento", Date, nullable=False),
    Column("cpf", String(14), nullable=False),
    Column("cnpj", String(18), nullable=True),
    Column("endereco_id", Integer, ForeignKey("enderecos.id"), nullable=True),
    Column("telefone", String(18), nullable=True),
    Column("celular", String(18), nullable=False),
    Column("email", String(80), nullable=False),
    Column("estado_civil", String(80), nullable=False),
    Column("como_conheceu", String(80), nullable=False),
    Column("indicacao_orgao", String(80), nullable=True),
    Column("procurou_outro_local", String(80), nullable=False),
    Column("procurou_qual_local", String(80), nullable=True),
    Column("obs", Text, nullable=True),
    Column("pj_constituida", String(80), nullable=False),
    Column("repres_legal", Boolean, nullable=True),
    Column("nome_repres_legal", String(80), nullable=True),
    Column("cpf_repres_legal", String(14), nullable=True),
    Column("contato_repres_legal", String(18), nullable=True),
    Column("rg_repres_legal", String(50), nullable=True),
    Column("nascimento_repres_legal", Date, nullable=True),
    Column("pretende_constituir_pj", String(80), nullable=True),
    Column("status", Integer, nullable=False),
    coluna_unidade(),
)

assistidos = Table(
    "assistidos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_atendido", Integer, ForeignKey("atendidos.id"), nullable=True),
    Column("sexo", String(1), nullable=False),
    Column("profissao", String(80), nullable=False),
    Column("raca", String(20), nullable=False),
    Column("rg", String(50), nullable=False),
    Column("grau_instrucao", String(100), nullable=False),
    Column("salario", Numeric(10, 2), nullable=False),
    Column("beneficio", String(30), nullable=False),
    Column("qual_beneficio", String(30), nullable=True),
    Column("contribui_inss", String(20), nullable=False),
    Column("qtd_pessoas_moradia", Integer, nullable=False),
    Column("renda_familiar", Numeric(10, 2), nullable=False),
    Column("participacao_renda", String(100), nullable=False),
    Column("tipo_moradia", String(100), nullable=False),
    Column("possui_outros_imoveis", Boolean, nullable=False),
    Column("quantos_imoveis", Integer, nullable=True),
    Column("possui_veiculos", Boolean, nullable=False),
    Column("possui_veiculos_obs", String(100), nullable=True),
    Column("quantos_veiculos", Integer, nullable=True),
    Column("ano_veiculo", String(5), nullable=True),
    Column("doenca_grave_familia", String(20), nullable=False),
    Column("pessoa_doente", String(50), nullable=True),
    Column("pessoa_doente_obs", String(100), nullable=True),
    Column("gastos_medicacao", Numeric(10, 2), nullable=True),
    Column("obs", String(1000), nullable=True),
)

orientacao_juridica = Table(
    "orientacao_juridica",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("area_direito", String(50), nullable=False),
    Column("sub_area", String(50), nullable=True),
    Column("descricao", Text, nullable=False),
    Column("data_criacao", DateTime, nullable=True),
    Column("status", Integer, nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=True),
    coluna_unidade(),
)

atendido_xOrientacaoJuridica = Table(
    "atendido_xOrientacaoJuridica",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "id_orientacaoJuridica",
        Integer,
        ForeignKey("orientacao_juridica.id"),
        nullable=True,
    ),
    Column("id_atendido", Integer, ForeignKey("atendidos.id"), nullable=True),
)

casos = Table(
    "casos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "id_usuario_responsavel", Integer, ForeignKey("usuarios.id"), nullable=False
    ),
    Column("area_direito", String(50), nullable=False),
    Column("sub_area", String(50), nullable=True),
    Column("id_orientador", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("id_estagiario", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("id_colaborador", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("data_criacao", DateTime, nullable=False),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("data_modificacao", DateTime, nullable=True),
    Column("id_modificado_por", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("situacao_deferimento", String(50), nullable=False),
    Column("justif_indeferimento", String(280), nullable=True),
    Column("status", Boolean, nullable=False),
    Column("descricao", Text, nullable=True),
    Column("numero_ultimo_processo", Integer, nullable=True),
    coluna_unidade(),
)

casos_atendidos = Table(
    "casos_atendidos",
    metadata,
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=True),
    Column("id_atendido", Integer, ForeignKey("atendidos.id"), nullable=True),
)

processos = Table(
    "processos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("especie", String(25), nullable=False),
    Column("numero", BigInteger, nullable=True, unique=True),
    Column("identificacao", Text, nullable=True),
    Column("vara", String(200), nullable=True),
    Column("link", String(1000), nullable=True),
    Column("probabilidade", String(25), nullable=True),
    Column("posicao_assistido", String(25), nullable=True),
    Column("valor_causa_inicial", Integer, nullable=True),
    Column("valor_causa_atual", Integer, nullable=True),
    Column("data_distribuicao", Date, nullable=True),
    Column("data_transito_em_julgado", Date, nullable=True),
    Column("obs", Text, nullable=True),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("status", Boolean, nullable=False),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False),
)

eventos = Table(
    "eventos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("num_evento", Integer, nullable=True),
    Column("tipo", String(50), nullable=False),
    Column("descricao", Text, nullable=True),
    Column("arquivo", String(100), nullable=True),
    Column("data_evento", Date, nullable=False),
    Column("data_criacao", DateTime, nullable=False),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_usuario_responsavel", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("status", Boolean, nullable=False),
    coluna_unidade(),
)

arquivos_caso = Table(
    "arquivosCaso",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("link_arquivo", String(300), nullable=True),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=True),
)

arquivos = Table(
    "arquivos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("titulo", String(150), nullable=False),
    Column("descricao", Text, nullable=True),
    Column("nome", Text, nullable=False),
    # Colunas abaixo são nulas em registros herdados da v2.
    Column("caminho", String(300), nullable=True),
    Column("data_criacao", DateTime, nullable=True),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=True),
)

notificacao = Table(
    "notificacao",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_executor_acao", Integer, ForeignKey("usuarios.id"), nullable=True),
    # Nulo = aviso geral (abertura do plantão), visto por orientadores e estagiários.
    Column("id_usu_notificar", Integer, ForeignKey("usuarios.id"), nullable=True),
    Column("acao", String(200), nullable=False),
    Column("data", Date, nullable=False),
    # Colunas abaixo não existiam na v2 (nulas em registros herdados).
    Column("tipo", String(30), nullable=True),  # caso | evento | lembrete | plantao
    Column("id_caso", Integer, nullable=True),
    Column("id_referencia", Integer, nullable=True),  # id do evento ou lembrete
    # Resumo do conteúdo do aviso (cliente do caso, descrição do lembrete etc.).
    Column("detalhe", String(300), nullable=True),
    Column("lida", Boolean, nullable=False, default=False),
    Column("data_criacao", DateTime, nullable=True),
    # Preenchida = notificação arquivada (some da lista padrão).
    Column("data_arquivamento", DateTime, nullable=True),
)

assistencias_judiciarias = Table(
    "assistencias_judiciarias",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String(150), nullable=False),
    Column("regiao", String(80), nullable=False),
    Column("areas_atendidas", String(1000), nullable=False),
    Column("endereco_id", Integer, ForeignKey("enderecos.id"), nullable=True),
    Column("telefone", String(18), nullable=False),
    Column("email", String(80), nullable=False, unique=True),
    Column("status", Integer, nullable=False),
    coluna_unidade(),
)

assistenciasJudiciarias_xOrientacao_juridica = Table(
    "assistenciasJudiciarias_xOrientacao_juridica",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "id_orientacaoJuridica",
        Integer,
        ForeignKey("orientacao_juridica.id"),
        nullable=True,
    ),
    Column(
        "id_assistenciaJudiciaria",
        Integer,
        ForeignKey("assistencias_judiciarias.id"),
        nullable=True,
    ),
)

lembretes = Table(
    "lembretes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("num_lembrete", Integer, nullable=True),
    Column("id_do_criador", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("data_criacao", DateTime, nullable=False),
    Column("data_lembrete", DateTime, nullable=False),
    Column("descricao", Text, nullable=False),
    Column("status", Boolean, nullable=False),
    coluna_unidade(),
)

historicos = Table(
    "historicos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("data", DateTime, nullable=False),
    Column("acao", String(50), nullable=True),
    Column("descricao", String(500), nullable=True),
)

documentos_roteiro = Table(
    "documentos_roteiro",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("area_direito", String(50), nullable=False),
    Column("link", String(1000), nullable=True),
)

fila_atendimentos = Table(
    "fila_atendimentos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("psicologia", Integer, nullable=False),
    Column("prioridade", Integer, nullable=False),
    Column("data_criacao", DateTime, nullable=True),
    Column("senha", String(10), nullable=False),
    Column("status", Integer, nullable=False),
    Column("id_atendido", Integer, ForeignKey("atendidos.id"), nullable=True),
    Column("data_saida", DateTime, nullable=True),
    coluna_unidade(),
)

# Tabelas do plantão. Criadas pela migration baseline ed1b0a0a61a6 e declaradas
# aqui para ficarem visíveis à aplicação, ao metadata.create_all dos testes e ao
# autogenerate do Alembic. O schema espelha o baseline coluna a coluna.
dias_plantao = Table(
    "dias_plantao",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("data", Date, nullable=True),
    # False = dia removido da configuração (soft delete)
    Column("status", Boolean, nullable=False, default=True),
    coluna_unidade(),
)

plantao = Table(
    "plantao",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("data_abertura", DateTime, nullable=True),
    Column("data_fechamento", DateTime, nullable=True),
    coluna_unidade(),
)

dias_marcados_plantao = Table(
    "dias_marcados_plantao",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("data_marcada", Date, nullable=True),
    # aberto | confirmar | divergencia | ausencia
    Column("confirmacao", String(15), nullable=False, default="aberto"),
    # True = marcação ativa; False = apagada pelo usuário (soft delete)
    Column("status", Boolean, nullable=False, default=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=True),
    coluna_unidade(),
)

registro_entrada = Table(
    "registro_entrada",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("data_entrada", DateTime, nullable=False),
    # NOT NULL no schema legado: enquanto o registro está em curso grava-se o
    # provisório 23:59:59 do dia da entrada, sobrescrito na saída.
    Column("data_saida", DateTime, nullable=False),
    # True = em curso (entrada sem saída); False = fechado
    Column("status", Boolean, nullable=False, default=True),
    # aberto | confirmar | divergencia | ausencia
    Column("confirmacao", String(15), nullable=False, default="aberto"),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=True),
    coluna_unidade(),
)

unidades = Table(
    "unidades",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String(60), nullable=False, unique=True),
    Column("sigla", String(10), nullable=False, unique=True),
    # False = unidade desativada (some do seletor, mantém o histórico)
    Column("ativa", Boolean, nullable=False, default=True),
    Column("criado", DateTime, nullable=False),
)

usuarios_unidades = Table(
    "usuarios_unidades",
    metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("unidade_id", Integer, ForeignKey("unidades.id"), primary_key=True),
)

password_reset_tokens = Table(
    "password_reset_tokens",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), nullable=False),
    # Só o hash do token é guardado: o valor em claro existe apenas no e-mail.
    Column("token_hash", String(64), nullable=False, unique=True),
    Column("expira_em", DateTime, nullable=False),
    # Preenchida = token já consumido (uso único).
    Column("usado_em", DateTime, nullable=True),
    Column("criado_em", DateTime, nullable=False),
)
