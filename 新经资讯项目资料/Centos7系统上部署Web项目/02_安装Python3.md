

# 安装Python3解释器



1. 安装相应的编辑工具

   ```shell
   [xiaowu@xiaowu ~]$ su root
   [root@xiaowu ~]$ yum -y groupinstall "Development tools"
   [root@xiaowu ~]$ yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel 	sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
   [root@xiaowu ~]$ yum install -y libffi-devel zlib1g-dev
   [root@xiaowu ~]$ yum install zlib* -y
   ```

2. 下载安装包

   ```shell
   [root@xiaowu ~]$ cd /opt
   [root@xiaowu opt]$ wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
   ```

3. 解压

   ```shell
   [root@xiaowu opt]$ tar -xvJf  Python-3.7.0.tar.xz
   ```

4. 创建编译安装目录

   ```shell
   [root@xiaowu opt]$ mkdir /usr/local/python3 
   ```

5. 安装

   ```shell
   [root@xiaowu opt]$ cd Python-3.7.0
   [root@xiaowu Python-3.7.0]$ ./configure --prefix=/usr/local/python3
   [root@xiaowu Python-3.7.0]$ make && install
   ```

6. 创建软链接

   ```shell
   [root@xiaowu Python-3.7.0]$ ln -s /usr/local/python3/bin/python3 /usr/local/bin/python3
   [root@xiaowu Python-3.7.0]$ ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip3
   ```

7. 验证是否成功

   ```shell
   [root@xiaowu Python-3.7.0]$ python3 -V
   [root@xiaowu Python-3.7.0]$ pip3 -V
   ```

   