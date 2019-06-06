from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app

app = create_app("develop")
# 6.集成flask_script
manager = Manager(app)
# 7.集成flask_migrate， 在flask中对数据库进行迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)



@app.route('/')
def index():
    return 'ok'


if __name__ == '__main__':
    manager.run()
