# Atendido/Assistido Templates

This directory contains all templates related to atendidos (clients) and assistidos (assisted clients) that have been centralized from various locations in the project.

## Structure

### Main Templates
- `atendidos_assistidos.html` - Main listing page for atendidos and assistidos
- `busca_atendidos.html` - Search results for atendidos
- `busca_atendidos_assistidos.html` - Search results for both atendidos and assistidos
- `cadastro_novo_atendido.html` - Form for creating new atendidos
- `editar_atendido.html` - Form for editing atendidos
- `editar_assistido.html` - Form for editing assistidos
- `atendido_form.html` - Reusable form component for atendidos
- `assistido_form.html` - Reusable form component for assistidos
- `perfil_assistidos.html` - Profile view for assistidos
- `tornar_assistido.html` - Form for converting atendidos to assistidos
- `lista_atendidos.html` - List view for atendidos
- `listar_assistidos.html` - List view for assistidos

### Search and Association Templates
- `busca_atendidos_oj.html` - Search atendidos for orientação jurídica
- `atendidos_lista_ajax.html` - AJAX list for atendidos
- `atendidos_lista_ajax_multiple.html` - AJAX list for multiple atendido selection
- `busca_associa_orientacao_juridica.html` - Search for associating atendidos with orientação jurídica

### Components
- `components/modal_associar_atendido.html` - Modal for associating atendidos
- `components/modal_associar_atendido_multiple.html` - Modal for associating multiple atendidos

## Migration Notes

These templates were previously scattered across:
- `gestaolegal/plantao/templates/`
- `gestaolegal/orientacao_juridica/templates/`

**All duplicate templates have been removed from their original locations.**

All template references have been updated to use the new centralized paths:
- Old: `{% include 'busca_atendidos.html' %}`
- New: `{% include 'atendido/busca_atendidos.html' %}`

## Usage

When including these templates in other files, use the full path:
```html
{% include 'atendido/busca_atendidos.html' %}
{% include 'atendido/components/modal_associar_atendido.html' %}
```

## Related Controllers

The main controller for these templates is `atendido_controller.py`, which has been updated to use the new template paths.
