"""
配置信息：
1、数据库配置
2、redis配置
3、session配置：主要是用来保存用户登录信息
4、csrf配置：当修改服务器资源时保护(post,put,delete,dispath)
5、日志文件：记录程序运行的过程
6、迁移配置
"""


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db


# 通过调用方法，返回app对象，app对象已经有相关的配置信息
from info.models import User

app = create_app('development')

# 添加扩展命令行
manager = Manager(app)

# 将app与db关联
Migrate(app, db)

# 将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    """创建管理员"""

    if not all([name, password]):
        print("参数不足")
        return

    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()


if __name__ == '__main__':
    manager.run()
