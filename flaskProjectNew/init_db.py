import os
import sys
import pymysql
from app import app, db, User, Course, Question, StudentAnswer

def init_database():
    """初始化数据库，创建表结构和测试数据"""
    print("开始初始化数据库...")
    
    # 确保上传目录存在
    for folder in ['course_files', 'course_images']:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"创建目录: {folder_path}")
    
    # 创建所有表
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        
        # 添加测试用户
        if not User.query.filter_by(username='teacher1').first():
            teacher = User(username='teacher1', password='123456', role='teacher')
            db.session.add(teacher)
            print("添加测试教师用户: teacher1/123456")
        
        if not User.query.filter_by(username='student1').first():
            student = User(username='student1', password='123456', role='student')
            db.session.add(student)
            print("添加测试学生用户: student1/123456")
        
        # 保存更改
        db.session.commit()
        print("数据库初始化完成!")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        sys.exit(1) 