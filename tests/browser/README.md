# Regressão do seletor de assistidos

Com o frontend local rodando, execute o teste abaixo. Todas as chamadas de API
são interceptadas e respondidas com dados sintéticos; não é necessário login e
nenhum cadastro real é criado ou alterado.

```bash
npm install --prefix /tmp/gestaolegal-browser --no-save playwright
PLAYWRIGHT_MODULE=/tmp/gestaolegal-browser/node_modules/playwright \
  node tests/browser/selector.cjs
```

O endereço padrão é `http://localhost:5002`; sobrescreva com `GL_BASE_URL`.
O navegador padrão é `/usr/bin/google-chrome`; sobrescreva com `CHROME_PATH`.

Verifica URL com filtros, busca, paginação de mais de 50 registros, seleção
entre páginas, confirmação, cancelamento, reabertura, respostas fora de ordem
e recuperação após falha da API. Os testes de API em
`tests/api/test_atendido_api.py` verificam CPF com/sem máscara, isolamento por
unidade, fichas legadas duplicadas e criação de caso com um assistido novo.
