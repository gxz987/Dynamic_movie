import logging
from flask import current_app
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db


# 通过传入不同配置创造出不同配置下的app实例，python设计模式：工厂模式
app = create_app("develop")

# 6.集成flask_script
manager = Manager(app)
# 7.集成flask_migrate， 在flask中对数据库进行迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)



if __name__ == '__main__':
    manager.run()
