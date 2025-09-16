document.addEventListener('DOMContentLoaded', function() {
    let currentCasoId = null;
    let searchTimeout;
    let selectedAssistidos = new Set();
    let selectedAssistidosInfo = new Map();
    let currentAssistidos = [];
    
    document.addEventListener('modal:open', function(event) {
        if (event.detail.modalId === 'modalGerenciarAssistidos') {
            currentCasoId = window.currentCasoId;
            if (currentCasoId) {
                carregarAssistidosAtuais();
                limparBusca();
                selectedAssistidos.clear();
                selectedAssistidosInfo.clear();
                updateAddButtonState();
            }
        }
    });
    
    document.getElementById('buscaAssistido').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const termo = this.value.trim();
        
        if (termo.length < 2) {
            esconderSugestoes();
            return;
        }
        
        searchTimeout = setTimeout(function() {
            buscarAssistidos(termo);
        }, 300);
    });
    
    document.getElementById('btnAdicionarAssistido').addEventListener('click', function() {
        adicionarAssistidosSelecionados();
    });
    
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('sugestao-item')) {
            const assistidoId = event.target.dataset.assistidoId;
            const assistidoNome = event.target.dataset.assistidoNome;
            toggleSelecaoAssistido(assistidoId, assistidoNome, event.target);
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.target.classList && event.target.classList.contains('sugestao-item')) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                const assistidoId = event.target.dataset.assistidoId;
                const assistidoNome = event.target.dataset.assistidoNome;
                toggleSelecaoAssistido(assistidoId, assistidoNome, event.target);
            }
        }
    });
    
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-excluir-assistido')) {
            const assistidoId = event.target.dataset.assistidoId;
            const assistidoNome = event.target.dataset.assistidoNome;
            
            if (confirm(`Deseja remover o assistido "${assistidoNome}" deste caso?`)) {
                removerAssistido(assistidoId);
            }
        }
    });
    
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.suggestions-container') && !event.target.closest('#buscaAssistido')) {
            esconderSugestoes();
        }
    });
    
    function carregarAssistidosAtuais() {
        if (!currentCasoId) return;
        
        document.getElementById('loadingAssistidos').style.display = 'block';
        
        fetch(`/api/casos/assistidos_caso_ajax/${currentCasoId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            const payload = data && data.data ? data.data : data;
            currentAssistidos = (payload && payload.assistidos) ? payload.assistidos : [];
            atualizarListaAssistidos();
        })
        .catch(error => {
            console.error('Erro ao carregar assistidos:', error);
            document.getElementById('listaAssistidosAtuais').innerHTML = 
                '<div class="text-center text-danger">Erro ao carregar assistidos</div>';
        })
        .finally(() => {
            document.getElementById('loadingAssistidos').style.display = 'none';
        });
    }
    
    function buscarAssistidos(termo) {
        if (!currentCasoId) {
            return;
        }
        
        const searchLoading = document.getElementById('searchLoading');
        searchLoading.style.display = 'block';
        
        const params = new URLSearchParams({
            termo: termo,
            caso_id: currentCasoId
        });
        
        fetch(`/casos/api/buscar_assistidos?${params}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            mostrarSugestoes(data.data);
        })
        .catch(error => {
            console.error('Erro ao buscar assistidos:', error);
            esconderSugestoes();
        })
        .finally(() => {
            searchLoading.style.display = 'none';
        });
    }
    
    function mostrarSugestoes(assistidos) {
        const container = document.getElementById('sugestoesAssistidos');
        console.log('assistidos:', assistidos);
        if (assistidos.length === 0) {
            container.innerHTML = '<div class="sugestao-item">Nenhum assistido encontrado</div>';
        } else {
            container.innerHTML = assistidos.map(assistido => `
                <div class="sugestao-item ${selectedAssistidos.has(String(assistido.id)) ? 'selected' : ''}" 
                     data-assistido-id="${assistido.id}" 
                     data-assistido-nome="${assistido.nome}"
                     tabindex="0"
                     role="button"
                     aria-pressed="${selectedAssistidos.has(String(assistido.id))}"
                     aria-label="Selecionar assistido ${assistido.nome}">
                    <div class="sugestao-item-header">
                        <strong>${assistido.nome}</strong>
                    </div>
                    <div class="sugestao-item-content">
                        <small>CPF: ${assistido.cpf || 'N/A'}</small>
                    </div>
                </div>
            `).join('');
        }
        
        container.classList.add('show');
    }
    
    function esconderSugestoes() {
        const container = document.getElementById('sugestoesAssistidos');
        container.classList.remove('show');
        container.innerHTML = '';
    }
    
    function toggleSelecaoAssistido(assistidoId, assistidoNome, element) {
        const idStr = String(assistidoId);
        if (selectedAssistidos.has(idStr)) {
            selectedAssistidos.delete(idStr);
            selectedAssistidosInfo.delete(idStr);
            if (element) {
                element.classList.remove('selected');
                element.setAttribute('aria-pressed', 'false');
            }
        } else {
            selectedAssistidos.add(idStr);
            selectedAssistidosInfo.set(idStr, assistidoNome);
            if (element) {
                element.classList.add('selected');
                element.setAttribute('aria-pressed', 'true');
            }
        }
        updateAddButtonState();
    }
    
    function adicionarAssistidosSelecionados() {
        if (!currentCasoId || selectedAssistidos.size === 0) return;
        const button = document.getElementById('btnAdicionarAssistido');
        button.disabled = true;
        const ids = Array.from(selectedAssistidos);
        const requests = ids
            .filter(id => !currentAssistidos.some(a => String(a.id) === String(id)))
            .map(id => fetch(`/casos/adicionar_assistido_caso/${currentCasoId}/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRFToken()
                },
                body: `csrf_token=${document.querySelector('input[name="csrf_token"]').value}`
            }).then(r => r.json()).then(data => ({ id, ok: data && data.success, data }))
            );
        Promise.all(requests)
            .then(results => {
                results.forEach(res => {
                    if (res.ok) {
                        const nome = selectedAssistidosInfo.get(String(res.id)) || '';
                        if (!currentAssistidos.some(a => String(a.id) === String(res.id))) {
                            currentAssistidos.push({ id: res.id, nome: nome });
                        }
                    }
                });
                atualizarListaAssistidos();
                selectedAssistidos.clear();
                selectedAssistidosInfo.clear();
                document.getElementById('sugestoesAssistidos').innerHTML = '';
                updateAddButtonState();
                limparBusca();
                if (typeof window.atualizarListaCasos === 'function') {
                    window.atualizarListaCasos();
                }
            })
            .catch(() => {})
            .finally(() => {
                button.disabled = false;
            });
    }
    
    function removerAssistido(assistidoId) {
        if (!currentCasoId || !assistidoId) return;
        
        fetch(`/casos/excluir_assistido_caso/${currentCasoId}/${assistidoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: `csrf_token=${document.querySelector('input[name="csrf_token"]').value}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentAssistidos = currentAssistidos.filter(a => a.id != assistidoId);
                atualizarListaAssistidos();
                
                if (typeof window.atualizarListaCasos === 'function') {
                    window.atualizarListaCasos();
                }
            } else {
                alert('Erro ao remover assistido: ' + (data.message || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro ao remover assistido:', error);
            alert('Erro ao remover assistido');
        });
    }
    
    function atualizarListaAssistidos() {
        const container = document.getElementById('listaAssistidosAtuais');
        const countElement = document.getElementById('assistidosCount');
        
        // Update count
        countElement.textContent = currentAssistidos.length;
        
        if (currentAssistidos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">👥</div>
                    <p>Nenhum assistido associado a este caso</p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <table class="assistidos-table">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th style="width: 100px;">Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${currentAssistidos.map(assistido => `
                            <tr>
                                <td class="assistido-nome">${assistido.nome}</td>
                                <td>
                                    <button class="btn-excluir-assistido" 
                                            data-assistido-id="${assistido.id}" 
                                            data-assistido-nome="${assistido.nome}"
                                            aria-label="Remover assistido ${assistido.nome}">
                                        Excluir
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    }
    
    function limparBusca() {
        document.getElementById('buscaAssistido').value = '';
        updateAddButtonState();
        esconderSugestoes();
    }
    
    function getCSRFToken() {
        const token = document.querySelector('input[name="csrf_token"]');
        return token ? token.value : '';
    }

    function updateAddButtonState() {
        document.getElementById('btnAdicionarAssistido').disabled = selectedAssistidos.size === 0;
    }
});
