from flask import flash, redirect, render_template, request


def error_404(error):
    return render_template("erros/404.html"), 404


def error_403(error):
    return render_template("erros/403.html"), 403


def error_413(error):
    flash("Arquivo muito grande. O tamanho máximo permitido é de 10MB.")
    return redirect(request.url, code=302)


def error_500(error):
    return render_template("erros/500.html"), 500
