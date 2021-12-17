import time
from setup import app, db
from user.user import user_app
from apis.shortener import url_app, URL

app.register_blueprint(user_app)
app.register_blueprint(url_app)
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

