// Regressão do seletor no front local; todas as chamadas de API são simuladas.
// PLAYWRIGHT_MODULE=/caminho/node_modules/playwright node tests/browser/selector.cjs
// GL_BASE_URL (padrão http://localhost:5002), CHROME_PATH opcionais.
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.GL_BASE_URL || 'http://localhost:5002';
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
  try {
    const ctx = await browser.newContext();
    await ctx.addCookies([{ name: 'auth_token', value: 'fixture-sem-acesso-real', url: base }]);
    await ctx.addInitScript(() => localStorage.setItem('unidade_ativa', '1'));
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const requests = [];
    const people = Array.from({ length: 65 }, (_, i) => ({ id: i + 1, nome: `Assistido ${String(i + 1).padStart(3, '0')}`, cpf: '', email: '', is_assistido: true }));
    const test = { id: 100, nome: 'TESTE SELETOR NOVO', cpf: '123.456.789-00', email: '', is_assistido: true };
    let fail = false;
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      assert.equal(route.request().method(), 'GET', 'Teste não deve gravar dados');
      let data = { items: [], total: 0, total_pages: 0 };
      if (url.pathname === '/api/user/me') data = { id: 1, nome: 'Operador sintético', urole: 'admin', status: true, unidades: [{ id: 1, nome: 'Belo Horizonte', sigla: 'BH', ativa: true }] };
      else if (url.pathname === '/api/user/opcoes') data = { items: [{ id: 1, nome: 'Operador sintético', urole: 'admin' }] };
      else if (url.pathname.includes('/atendido')) {
        const params = url.searchParams;
        assert.equal(params.get('tipo_busca'), 'assistidos');
        requests.push({ search: params.get('search'), page: params.get('page') });
        if (fail) return route.fulfill({ status: 500, json: { success: false, error: { message: 'Falha simulada' } } });
        const term = params.get('search');
        if (term === 'lenta') await new Promise(resolve => setTimeout(resolve, 1200));
        const filtered = term === 'TESTE' ? [test] : term ? [{ ...test, nome: term }] : people;
        const number = Number(params.get('page'));
        data = { items: filtered.slice((number - 1) * 50, number * 50), total: filtered.length, total_pages: Math.ceil(filtered.length / 50) };
      }
      await route.fulfill({ json: { success: true, data } });
    });
    await page.goto(base + '/casos/cadastrar-novo-caso');
    await page.getByRole('button', { name: 'Adicionar Assistidos' }).click();
    const dialog = page.getByRole('dialog');
    const ready = () => dialog.getByRole('button', { name: 'Confirmar Seleção' }).waitFor().then(async () => {
      await page.waitForFunction(() => { const b = [...document.querySelectorAll('[role="dialog"] button')].find(b => b.textContent.includes('Confirmar Seleção')); return b && !b.disabled; });
    });
    await ready();
    assert.equal(await dialog.getByRole('checkbox').count(), 50);
    await dialog.getByRole('checkbox').first().check();
    await dialog.getByRole('button', { name: 'Próxima' }).click();
    await page.waitForFunction(() => document.querySelector('[role="dialog"]')?.textContent.includes('Página 2 de 2'));
    assert.equal(await dialog.getByRole('checkbox').count(), 15);
    await dialog.getByRole('checkbox').first().check();
    await dialog.getByPlaceholder('Buscar por nome ou CPF (com ou sem pontuação)').fill('TESTE');
    await dialog.getByText('TESTE SELETOR NOVO', { exact: true }).waitFor();
    assert.equal(requests.at(-1).page, '1');
    await dialog.getByRole('checkbox').check();
    await dialog.getByRole('button', { name: 'Confirmar Seleção' }).click();
    await page.getByText('3 assistido(s) selecionado(s):').waitFor();
    await page.getByRole('button', { name: 'Adicionar Assistidos' }).click();
    await ready();
    assert.equal(await dialog.getByRole('checkbox').first().isChecked(), true);
    // Cancelar uma desmarcação não perde seleções já confirmadas.
    await dialog.getByRole('checkbox').first().uncheck();
    await dialog.getByRole('button', { name: 'Cancelar', exact: true }).click();
    await page.getByRole('button', { name: 'Adicionar Assistidos' }).click();
    await ready();
    assert.equal(await dialog.getByRole('checkbox').first().isChecked(), true);
    const search = dialog.getByPlaceholder('Buscar por nome ou CPF (com ou sem pontuação)');
    await search.fill('lenta');
    await page.waitForTimeout(450);
    await search.fill('rápida');
    await dialog.getByText('rápida', { exact: true }).waitFor();
    await page.waitForTimeout(1300);
    assert.equal(await dialog.getByText('lenta', { exact: true }).count(), 0);
    fail = true;
    await search.fill('erro');
    await dialog.getByRole('alert').waitFor();
    fail = false;
    await dialog.getByRole('button', { name: 'Tentar novamente' }).click();
    await dialog.getByText('erro', { exact: true }).waitFor();
    assert.equal(await dialog.getByRole('alert').count(), 0);
    assert.deepEqual(errors, []);
    console.log('OK: URL, busca, paginação, seleção entre páginas, reabertura, cancelar, concorrência e recuperação de erro.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
