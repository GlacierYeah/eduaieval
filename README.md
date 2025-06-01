## eduaieval
基于大模型的学习效果智能评估系统

这是一个前后端分离的智能教育系统，支持教师上传课程资料，自动生成知识图谱和练习题，学生可以学习课程并完成练习题。

# 项目结构

- `flaskProject/`: Flask后端项目
  - `app.py`: 主应用程序
  - `evaluate.py`: 评估学生答案的模块
  - `knowledge_graph.py`: 知识图谱生成模块
  - `question_generate.py`: 问题生成模块
  - `static/uploads/`: 上传的文件存储目录
  - `templates/`: HTML模板目录

- `Vue_project/`: Vue前端项目
  - `src/`: 源代码目录
    - `views/`: 页面组件
    - `components/`: 可复用组件
    - `stores/`: Pinia状态管理
    - `assets/`: 静态资源
  - `public/`: 公共资源目录

# 功能特点

1. **用户角色**：支持教师和学生两种角色
2. **教师功能**：
   - 课程管理：创建、编辑和删除课程
   - 学生管理：将学生添加到课程
   - 数据统计：查看学生学习情况
3. **学生功能**：
   - 课程学习：浏览课程内容和知识图谱
   - 练习答题：回答系统生成的问题
   - 查看反馈：查看AI评估的答案反馈
4. **智能功能**：
   - 自动从文档提取知识点
   - 生成知识图谱
   - 基于知识点生成问题和参考答案
   - 智能评估学生答案

## 技术栈

- **前端**：Vue 3 + Vite + Pinia + Vue Router + Element Plus + ECharts
- **后端**：Flask + SQLAlchemy + MySQL
- **AI模型**：通过API调用大语言模型

## 安装和运行

### 前端

```bash
cd Vue_project
npm install
npm run dev
```

vite. config. js中的的路径修改为此时后端端口

### 后端

```bash
cd flaskProject
# 创建并激活虚拟环境
conda activate flask_env
# 安装依赖
pip install flask flask-cors flask-sqlalchemy pymysql openai dashscope python-docx PyPDF2
# 初始化数据库
flask init-db
# 运行应用
flask run
```

将ffmpeg的bin目录比如D:\proj\eduaieval\ffmpeg-7.1.1-essentials_build\bin加入环境变量

部署wav2lip

## 数据库配置

1. 创建MySQL数据库：`education_system`

2. 配置数据库连接（在`flaskProject/app.py`中）：

   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@localhost/education_system'
   ```

## 示例用户

- 教师：用户名 `teacher1` / 密码 `123456`
- 学生：用户名 `student1` / 密码 `123456`

## 注意事项

- 确保已安装必要的Python库
- 确保后端API密钥配置正确（dashscope等）
- 确保MySQL服务已启动
- 前端默认连接到`http://localhost:5000/api`
