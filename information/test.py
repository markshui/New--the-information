import datetime
import random
import time

from info import db
from info.models import User
from manager import app


def add_users():
    """批量添加测试用户"""

    users = []
    now = datetime.datetime.now()
    print(now)

    for num in range(0, 10000):
        try:
            user = User()
            user.nick_name = '%011d' % num
            user.mobile = '%011d' % num
            user.password = '000000'
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)

    with app.app_context():
        db.session.add_all(users)
        db.session.commit()

    print('批量添加用户成功！')


if __name__ == '__main__':
    # add_users()
    t1 = time.localtime()
    t2= datetime.datetime.now()
    # print(t1)
    # print(type(t1))
    # print(t2)
    # print(type(t2))

    # 获取当前的时间字符串
    today_day_str = '%d-%02d-%02d' % (t1.tm_year, t1.tm_mon, t1.tm_mday)
    print(today_day_str)
    # 将当前的时间字符串转化成时间对象
    today_day = datetime.datetime.strptime(today_day_str, '%Y-%m-%d')
    print(today_day)
    print(type(today_day))

    begin_date = today_day - datetime.timedelta(days=1)
    end_date = today_day - datetime.timedelta(days=1-1)
    print(begin_date)
    print(end_date)

