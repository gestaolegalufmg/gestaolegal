from gestaolegal import app
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

if __name__ == "__main__":
    app.run(debug=False)
    csrf.init_app(app)
