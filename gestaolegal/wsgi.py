from gestaolegal import app
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
	csrf.init_app(app)
