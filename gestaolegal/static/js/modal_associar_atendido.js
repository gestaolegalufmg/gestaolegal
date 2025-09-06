$(document).ready(function() {
    let currentOrientacaoId = null;
    let searchTimeout;
    
    // Listen for modal open events
    document.addEventListener('modal:open', function(event) {
        if (event.detail.modalId === 'modalAssociarAtendido') {
            currentOrientacaoId = window.currentOrientacaoId;
            carregarAtendidos('');
        }
    });
    
    $('#buscaAtendido').on('input', function() {
        clearTimeout(searchTimeout);
        const termo = $(this).val();
        
        searchTimeout = setTimeout(function() {
            carregarAtendidos(termo);
        }, 300);
    });
    
    function carregarAtendidos(termo) {
        if (!currentOrientacaoId) {
            return;
        }
        
        $('#loadingAtendidos').show();
        $('#tbodyAtendidos').empty();
        
        $.ajax({
            url: '/orientacao_juridica/buscar_atendidos_ajax',
            method: 'GET',
            data: {
                termo: termo,
                orientacao_id: currentOrientacaoId
            },
            success: function(data) {
                $('#tbodyAtendidos').html(data);
            },
            error: function() {
                $('#tbodyAtendidos').html('<tr><td colspan="3" class="text-center text-danger">Erro ao carregar atendidos</td></tr>');
            },
            complete: function() {
                $('#loadingAtendidos').hide();
            }
        });
    }
    
    $(document).on('click', '.btn-associar-atendido', function() {
        const atendidoId = $(this).data('atendido-id');
        const atendidoNome = $(this).data('atendido-nome');
        
        if (confirm(`Deseja associar o atendido "${atendidoNome}" à orientação jurídica?`)) {
            const url = `/orientacao_juridica/associa_orientacao_juridica/${currentOrientacaoId}/${atendidoId}`;
            
            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrf_token: $('input[name="csrf_token"]').val()
                },
                success: function(response) {
                    if (response.success) {
                        ModalManager.close('modalAssociarAtendido');
                        location.reload();
                    } else {
                        alert('Erro ao associar atendido: ' + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    alert('Erro ao associar atendido');
                }
            });
        }
    });
}); 