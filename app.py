from gestaolegaldaj import app
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import  text

csrf = CSRFProtect(app)

if __name__ == '__main__':
	app.run(debug=False)
	csrf.init_app(app)