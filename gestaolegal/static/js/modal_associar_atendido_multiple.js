$(document).ready(function() {
    let searchTimeout;
    let selectedAtendidos = [];
    
    $('#modalAssociarAtendidoMultiple').on('show.bs.modal', function (event) {
        carregarAtendidos('');
    });
    
    $('#buscaAtendidoMultiple').on('input', function() {
        clearTimeout(searchTimeout);
        const termo = $(this).val();
        
        searchTimeout = setTimeout(function() {
            carregarAtendidos(termo);
        }, 300);
    });
    
    function carregarAtendidos(termo) {
        $('#loadingAtendidosMultiple').show();
        $('#tbodyAtendidosMultiple').empty();
        
        $.ajax({
            url: '/orientacao_juridica/buscar_atendidos_ajax',
            method: 'GET',
            data: {
                termo: termo,
                orientacao_id: 0,
                template: 'multiple'
            },
            success: function(data) {
                $('#tbodyAtendidosMultiple').html(data);
                updateSelectedCount();
            },
            error: function(xhr, status, error) {
                $('#tbodyAtendidosMultiple').html('<tr><td colspan="4" class="text-center text-danger">Erro ao carregar atendidos</td></tr>');
            },
            complete: function() {
                $('#loadingAtendidosMultiple').hide();
            }
        });
    }
    
    $(document).on('change', '#tbodyAtendidosMultiple input[type="checkbox"]', function() {
        updateSelectedCount();
    });
    
    $(document).on('change', '#checkallMultiple', function() {
        const isChecked = $(this).is(':checked');
        $('#tbodyAtendidosMultiple input[type="checkbox"]').prop('checked', isChecked);
        updateSelectedCount();
    });
    
    function updateSelectedCount() {
        const checkedCount = $('#tbodyAtendidosMultiple input[type="checkbox"]:checked').length;
        const totalCount = $('#tbodyAtendidosMultiple input[type="checkbox"]').length;
        
        if (checkedCount === 0) {
            $('#checkallMultiple').prop('indeterminate', false).prop('checked', false);
        } else if (checkedCount === totalCount) {
            $('#checkallMultiple').prop('indeterminate', false).prop('checked', true);
        } else {
            $('#checkallMultiple').prop('indeterminate', true);
        }
        
        const button = $('#associarSelecionados');
        if (checkedCount > 0) {
            button.prop('disabled', false).text(`Associar Selecionados (${checkedCount})`);
        } else {
            button.prop('disabled', true).text('Associar Selecionados');
        }
    }
    
    $(document).on('click', '#associarSelecionados', function() {
        const checkedBoxes = $('#tbodyAtendidosMultiple input[type="checkbox"]:checked');
        selectedAtendidos = [];
        
        checkedBoxes.each(function() {
            const row = $(this).closest('tr');
            const atendidoId = $(this).data('atendido-id');
            const atendidoNome = row.find('td:eq(1)').text().trim();
            const atendidoCpf = row.find('td:eq(2)').text().trim();
            const atendidoCelular = row.find('td:eq(3)').text().trim();
            
            selectedAtendidos.push({
                id: atendidoId,
                nome: atendidoNome,
                cpf: atendidoCpf,
                celular: atendidoCelular
            });
        });
        
        if (selectedAtendidos.length > 0) {
            updateFormWithSelectedAtendidos();
            $('#modalAssociarAtendidoMultiple').modal('hide');
        }
    });
    
    function updateFormWithSelectedAtendidos() {
        $('#lista-atendidos').remove();
        
        const container = $('#atendidos > div > p');
        container.after(`
            <div id="lista-atendidos">
                <table class="table table-striped">
                    <tbody></tbody>
                </table>
            </div>
        `);
        
        const tableBody = $('#lista-atendidos .table tbody');
        selectedAtendidos.forEach(atendido => {
            tableBody.append(`
                <tr>
                    <td>${atendido.nome}</td>
                    <td>${atendido.cpf}</td>
                    <td>${atendido.celular}</td>
                    <td>
                        <a href="/atendido/perfil_assistido/${atendido.id}" target="_blank" class="btn btn-sm btn-info">visualizar</a>
                    </td>
                </tr>
            `);
        });
        
        const atendidosData = { id: selectedAtendidos.map(a => a.id) };
        $('#form').prepend(`
            <input id="listaAtendidos" type="hidden" name="listaAtendidos" value='${JSON.stringify(atendidosData)}' />
        `);
    }
    
    $('#modalAssociarAtendidoMultiple').on('hidden.bs.modal', function () {
        $('#buscaAtendidoMultiple').val('');
        $('#tbodyAtendidosMultiple').empty();
        $('#checkallMultiple').prop('checked', false).prop('indeterminate', false);
        $('#associarSelecionados').prop('disabled', true).text('Associar Selecionados');
    });
}); 