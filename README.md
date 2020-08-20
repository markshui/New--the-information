# New-the-infomation



### 一、项目介绍

一款新闻展示的Web项目，主要为用户提供最新的金融资讯、数据

基于Flask框架实现，以**前后端不分离**的形式实现具体逻辑



### 二、技术实现

- 基于 Python 3.0 + Flask 框架实现
- 数据存储使用 Redis + MySQL 实现
- 第三方扩展：
  - 七牛云：文件存储平台
  - 云通信：短信验证码平台
- 布署：基于ubuntu 16.04系统，使用 Gunicorn + Nginx 进行布署



### 三、功能模块

- 新闻模块
  - 首页新闻列表
  - 新闻详情
- 用户模块
  - 登录注册/个人信息修改
  - 新闻收藏/发布
- 后台管理



### 四、项目包介绍

```python
alembic==1.4.0
blinker==1.4
certifi==2019.11.28
chardet==3.0.4
Click==7.0
Flask==1.1.1
Flask-Mail==0.9.1
Flask-Migrate==2.5.2
Flask-MySQLdb==0.2.0
Flask-Script==2.0.6
Flask-Session==0.3.1
Flask-SQLAlchemy==2.4.1
Flask-WTF==0.14.3
idna==2.9
itsdangerous==1.1.0
Jinja2==2.10.3
jsonify==0.5
ledis==0.0.1
Mako==1.1.1
MarkupSafe==1.1.1
mysqlclient==1.4.6
Pillow==6.2.2
PyMySQL==0.9.3
python-dateutil==2.8.1
python-editor==1.0.4
qiniu==7.2.8
redis==3.4.1
requests==2.23.0
six==1.14.0
SQLAlchemy==1.3.13
urllib3==1.25.8
Werkzeug==0.16.0
WTForms==2.2.1
```



### 五、项目布局

```
├─.idea
│  └─inspectionProfiles
├─info
│  ├─libs
│  │  ├─yuntongxun
│  │  │  └─__pycache__
│  │  └─__pycache__
│  ├─modules
│  │  ├─admin
│  │  │  └─__pycache__
│  │  ├─index
│  │  │  └─__pycache__
│  │  ├─news
│  │  │  └─__pycache__
│  │  ├─passport
│  │  │  └─__pycache__
│  │  ├─profile
│  │  │  └─__pycache__
│  │  └─__pycache__
│  ├─static
│  │  ├─admin
│  │  │  ├─css
│  │  │  ├─html
│  │  │  ├─images
│  │  │  ├─js
│  │  │  └─tinymce
│  │  │      └─js
│  │  │          └─tinymce
│  │  │              ├─langs
│  │  │              ├─plugins
│  │  │              │  ├─advlist
│  │  │              │  ├─anchor
│  │  │              │  ├─autolink
│  │  │              │  ├─autoresize
│  │  │              │  ├─autosave
│  │  │              │  ├─bbcode
│  │  │              │  ├─charmap
│  │  │              │  ├─code
│  │  │              │  ├─codesample
│  │  │              │  │  └─css
│  │  │              │  ├─colorpicker
│  │  │              │  ├─contextmenu
│  │  │              │  ├─directionality
│  │  │              │  ├─emoticons
│  │  │              │  │  └─img
│  │  │              │  ├─fullpage
│  │  │              │  ├─fullscreen
│  │  │              │  ├─help
│  │  │              │  │  └─img
│  │  │              │  ├─hr
│  │  │              │  ├─image
│  │  │              │  ├─imagetools
│  │  │              │  ├─imageupload
│  │  │              │  │  ├─css
│  │  │              │  │  ├─img
│  │  │              │  │  └─uncompressed
│  │  │              │  │      └─css
│  │  │              │  ├─importcss
│  │  │              │  ├─insertdatetime
│  │  │              │  ├─legacyoutput
│  │  │              │  ├─link
│  │  │              │  ├─lists
│  │  │              │  ├─media
│  │  │              │  ├─nonbreaking
│  │  │              │  ├─noneditable
│  │  │              │  ├─pagebreak
│  │  │              │  ├─paste
│  │  │              │  ├─preview
│  │  │              │  ├─print
│  │  │              │  ├─save
│  │  │              │  ├─searchreplace
│  │  │              │  ├─spellchecker
│  │  │              │  ├─tabfocus
│  │  │              │  ├─table
│  │  │              │  ├─template
│  │  │              │  ├─textcolor
│  │  │              │  ├─textpattern
│  │  │              │  ├─toc
│  │  │              │  ├─visualblocks
│  │  │              │  │  └─css
│  │  │              │  ├─visualchars
│  │  │              │  └─wordcount
│  │  │              ├─skins
│  │  │              │  └─lightgray
│  │  │              │      ├─fonts
│  │  │              │      └─img
│  │  │              └─themes
│  │  │                  ├─inlite
│  │  │                  ├─mobile
│  │  │                  └─modern
│  │  └─news
│  │      ├─css
│  │      ├─html
│  │      ├─images
│  │      ├─js
│  │      └─tinymce
│  │          └─js
│  │              └─tinymce
│  │                  ├─langs
│  │                  ├─plugins
│  │                  │  ├─advlist
│  │                  │  ├─anchor
│  │                  │  ├─autolink
│  │                  │  ├─autoresize
│  │                  │  ├─autosave
│  │                  │  ├─bbcode
│  │                  │  ├─charmap
│  │                  │  ├─code
│  │                  │  ├─codesample
│  │                  │  │  └─css
│  │                  │  ├─colorpicker
│  │                  │  ├─contextmenu
│  │                  │  ├─directionality
│  │                  │  ├─emoticons
│  │                  │  │  └─img
│  │                  │  ├─fullpage
│  │                  │  ├─fullscreen
│  │                  │  ├─help
│  │                  │  │  └─img
│  │                  │  ├─hr
│  │                  │  ├─image
│  │                  │  ├─imagetools
│  │                  │  ├─imageupload
│  │                  │  │  ├─css
│  │                  │  │  ├─img
│  │                  │  │  └─uncompressed
│  │                  │  │      └─css
│  │                  │  ├─importcss
│  │                  │  ├─insertdatetime
│  │                  │  ├─legacyoutput
│  │                  │  ├─link
│  │                  │  ├─lists
│  │                  │  ├─media
│  │                  │  ├─nonbreaking
│  │                  │  ├─noneditable
│  │                  │  ├─pagebreak
│  │                  │  ├─paste
│  │                  │  ├─preview
│  │                  │  ├─print
│  │                  │  ├─save
│  │                  │  ├─searchreplace
│  │                  │  ├─spellchecker
│  │                  │  ├─tabfocus
│  │                  │  ├─table
│  │                  │  ├─template
│  │                  │  ├─textcolor
│  │                  │  ├─textpattern
│  │                  │  ├─toc
│  │                  │  ├─visualblocks
│  │                  │  │  └─css
│  │                  │  ├─visualchars
│  │                  │  └─wordcount
│  │                  ├─skins
│  │                  │  └─lightgray
│  │                  │      ├─fonts
│  │                  │      └─img
│  │                  └─themes
│  │                      ├─inlite
│  │                      ├─mobile
│  │                      └─modern
│  ├─templates
│  │  ├─admin
│  │  └─news
│  ├─utils
│  │  ├─captcha
│  │  │  ├─fonts
│  │  │  └─__pycache__
│  │  └─__pycache__
│  └─__pycache__
├─logs
├─migrations
│  ├─versions
│  │  └─__pycache__
│  └─__pycache__
└─__pycache__

```

### 六、数据库之创建表关系


