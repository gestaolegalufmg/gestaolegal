class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO")
        if scheme:
            environ["wsgi.url_scheme"] = scheme

        host = environ.get("HTTP_X_FORWARDED_HOST")
        if host:
            environ["HTTP_HOST"] = host

        forwarded_for = environ.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            environ["REMOTE_ADDR"] = forwarded_for.split(",")[0].strip()

        return self.app(environ, start_response)
