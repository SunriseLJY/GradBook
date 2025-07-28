# GradBook 使用说明

### If you're an english reader, please translate this manual by your own, I'm sorry for this.

### 如果你想要下载本项目，请仔细阅读以下内容：

- 如果你将本项目用于个人学习，可以直接使用，但不得部署在服务器或以任何形式以自己的名义向他人传播项目代码。  
- 如果你将本项目用于个人项目，你可以部署在服务器或向他人传播，但是必须在页脚添加 “powered by GradBook” 字样和一个指向本项目的 Github 地址的超链接。  
- 如果你将此项目用于商业用途，请通过邮箱联系我，获得我明确同意后方可在我允许的范围内使用。

## 介绍
### 这是一个毕业纪念册网站, 你可以在上面记录你的班级中的几乎所有具有纪念意义的信息。包括：

- 图片
- 视频
- 同学档案，包括姓名、生日、联系方式。
- 老师档案，包括姓名、生日、任教科目、任教时间、联系方式。

当然，你也可以在下载本项目后自行更改。

## 使用说明
本项目采用 Python 的 Flask 第三方库实现后台逻辑，前端采用 HTML与CSS 实现，数据库采用 SQLite3 实现。

首先，需要在您的计算机上安装以下语言环境/第三方库：

- ### Python 3  
  访问 [Python 官方网站](https://www.python.org/) 下载最新版本的 Python3。

  接下来，运行项目目录下的 main.py 文件。

  运行后，访问 `http://127.0.0.1:5000/` 即可访问本项目。

- ### Flask
  输入命令 `pip install flask` 安装 Flask 第三方库。  
  如果您觉得下载速度慢或pip提示网络错误，可以使用以下命令：
  ```
  pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
