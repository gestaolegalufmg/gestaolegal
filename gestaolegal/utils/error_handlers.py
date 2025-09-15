import logging

from flask import flash, redirect, render_template, request

logger = logging.getLogger(__name__)


def error_404(error):
    return render_template("principal/erros/404.html"), 404


def error_403(error):
    return render_template("principal/erros/403.html"), 403


def error_413(error):
    flash("Arquivo muito grande. O tamanho máximo permitido é de 10MB.")
    return redirect(request.url, code=302)


def error_500(error):
    return render_template("principal/erros/500.html"), 500


def error_csrf(error):
    """Handle CSRF token errors"""
    flash(
        "Token de segurança inválido ou expirado. Por favor, tente novamente.",
        "warning",
    )
    return redirect(request.url or "/"), 400


def value_error(error):
    logger.error(f"Value error: {error}")
    flash(error.args[0], "error")
    return redirect(request.url or "/"), 400
