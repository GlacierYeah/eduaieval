from flask import Flask, request, jsonify, session, render_template, Response, current_app,send_from_directory, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import json
import uuid
from werkzeug.utils import secure_filename
from knowledge_graph import read_file_content, knowledge_extract, generate_knowledge_graph
from question_generate import question_ask
from evaluate import evaluate_student_answer
import os
from flask import Flask, request, jsonify, render_template # 等等
from flask_sqlalchemy import SQLAlchemy
from video import text_to_talking_head
import os
import traceback
import posixpath

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:8080", "http://localhost:3000"], allow_headers=["Content-Type", "Authorization"], expose_headers=["Content-Type"], methods=["GET", "POST", "PUT", "DELETE"])

# 配置
app.config['SECRET_KEY'] = '2f4a6d8b0c2e4f6a8b0d2f4a6d8b0c2e4f6a8b0d2f4a6d8b0c2e4f6a8b0d2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/education_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大上传大小

# 添加静态文件的CORS处理
@app.after_request
def add_cors_headers(response):
    if request.path.startswith('/static/'):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Cache-Control', 'public, max-age=86400')
    return response

# 确保上传文件夹存在
for folder in ['course_files', 'course_images', 'digital_human']:
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# 复制数字人视频文件到静态文件夹
digital_human_video = os.path.join(app.root_path, 'static', 'uploads', 'digital_human', 'assistant.mp4')
if not os.path.exists(digital_human_video):
    source_video = os.path.join(app.root_path, '..', 'flaskProject', 'static', 'uploads', 'digital_human', 'assistant.mp4')
    if os.path.exists(source_video):
        import shutil
        shutil.copy2(source_video, digital_human_video)
        print(f"已复制数字人视频文件到: {digital_human_video}")
    else:
        print(f"警告: 数字人视频文件不存在: {source_video}")

db = SQLAlchemy(app)

# 模型定义
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'teacher' 或 'student'
    email = db.Column(db.String(120), nullable=True)  # 添加email字段

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,

        }

# 教师与课程的多对多关系表
teacher_course = db.Table('teacher_course',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

# 学生与课程的多对多关系表
student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    knowledge_graph = db.Column(db.Text)  # 存储知识图谱JSON
    
    # 关系
    teachers = db.relationship('User', secondary=teacher_course, 
                            backref=db.backref('teaching_courses', lazy='dynamic'))
    students = db.relationship('User', secondary=student_course, 
                             backref=db.backref('enrolled_courses', lazy='dynamic'))
    questions = db.relationship('Question', backref='course', lazy=True)
    
    def to_dict(self):
        # 获取系统中所有学生的数量
        student_count = User.query.filter_by(role='student').count()
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_path': self.image_path,
            'file_path': self.file_path,
            'teachers': [teacher.username for teacher in self.teachers],
            'students_count': student_count,  # 显示所有学生数量而不是课程注册学生数
            'questions_count': len(self.questions)
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    video_url = db.Column(db.String(255), nullable=True)  # 存储视频路径/URL，nullable=True允许初始时没有视频
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'reference_answer': self.reference_answer,
            'course_id': self.course_id,
            'video_url': self.video_url
        }

class StudentAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    student = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='student_answers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'score': self.score,
            'feedback': self.feedback,
            'student_id': self.student_id,
            'question_id': self.question_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 路由
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'success': True, 'message': 'API工作正常'})

@app.route('/api/digital-human/status', methods=['GET'])
def digital_human_status():
    """检查AI数字人服务状态"""
    # 这里可以添加实际的服务状态检查逻辑
    # 目前简单返回服务可用
    return jsonify({
        'success': True, 
        'available': True,
        'message': 'AI数字人服务正常',
        'features': ['答题评估', '视觉交互']
    })

@app.route('/api/digital-human/video', methods=['GET'])
def get_digital_human_video():
    """提供数字人视频"""
    try:
        # 视频文件路径
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'digital_human', 'assistant.mp4')
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            return jsonify({'success': False, 'message': '数字人视频不存在'}), 404
        
        # 创建视频流响应
        def generate():
            with open(video_path, 'rb') as video_file:
                chunk_size = 1024 * 1024  # 1MB 块大小
                while True:
                    chunk = video_file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        return Response(
            generate(),
            mimetype='video/mp4',
            headers={
                'Content-Disposition': 'inline; filename=assistant.mp4',
                'Cache-Control': 'public, max-age=86400'  # 缓存24小时
            }
        )
    except Exception as e:
        print(f"提供视频时出错: {str(e)}")
        return jsonify({'success': False, 'message': '获取数字人视频失败'}), 500

@app.route('/static/generated_videos/courses/<int:course_id>/questions/<path:filename>')
def serve_course_question_video(course_id, filename):
    """提供指定课程的特定问题视频文件 (确保 Range Requests 被处理)"""
    app = current_app  # 在应用上下文中获取 app

    # 构造相对于 Flask 静态文件根目录的子目录路径
    directory_relative_to_static = os.path.join(COURSE_VIDEO_BASE_SUBDIR, str(course_id), 'questions')

    # 获取配置的静态文件夹的绝对路径
    static_folder_abs = app.static_folder
    if not static_folder_abs:
        app.logger.error("Flask app.static_folder 未配置!")
        abort(500)

        # 拼接得到包含目标文件的完整绝对目录路径
    directory_abs = os.path.join(static_folder_abs, directory_relative_to_static)

    app.logger.debug(f"显式路由: 尝试从目录提供文件 '{filename}': {directory_abs}")

    try:
        # 使用 send_from_directory 来正确处理范围请求
        # conditional=True 是默认值，确保 ETag 和 Range 处理
        return send_from_directory(directory_abs, filename, conditional=True)
    except FileNotFoundError:
        app.logger.warning(f"显式路由: 文件未找到: {os.path.join(directory_abs, filename)}")
        abort(404)
    except Exception as e:
        app.logger.error(f"显式路由: 提供文件 {filename} 从 {directory_abs} 时出错: {e}")
        abort(500)


# Base subdirectory within static folder for course-specific videos
# URL will start with /static/generated_videos/courses/
COURSE_VIDEO_BASE_SUBDIR = os.path.join('generated_videos', 'courses')
# Subdirectory for temporary audio files (within instance path)
TEMP_AUDIO_SUBDIR = 'temp_audio'


@app.route('/api/courses/<int:course_id>/generate_question_videos', methods=['POST'])
def batch_generate_question_videos(course_id):
    app = current_app

    course = Course.query.get_or_404(course_id)  # Fetch the course object early
    questions_to_process = Question.query.filter_by(course_id=course_id).all()

    if not questions_to_process:
        # ... (no questions found message remains the same) ...
        return jsonify(
            {'success': True, 'message': f'课程 {course_id} 下没有找到问题。', 'generated_count': 0, 'skipped_count': 0,
             'failed_count': 0, 'questions': []}), 200

    generated_count = 0
    skipped_count = 0
    failed_count = 0
    errors = []
    updated_questions_data = []

    app.logger.info(f"开始为课程 {course_id} 的 {len(questions_to_process)} 个问题批量生成视频...")

    # --- Determine Base Paths ---
    static_folder_path = app.static_folder
    if not static_folder_path:
        # ... (handle missing static folder config) ...
        app.logger.error("Flask app.static_folder is not configured!")
        return jsonify({'success': False, 'message': '服务器静态文件夹未配置。'}), 500

    temp_audio_dir_abs = os.path.join(app.instance_path, TEMP_AUDIO_SUBDIR)

    # --- Base directory for course-specific videos ---
    # e.g., /path/to/project/static/generated_videos/courses
    course_video_base_dir_abs = os.path.join(static_folder_path, COURSE_VIDEO_BASE_SUBDIR)

    # --- Ensure Temp Directory Exists ---
    try:
        # We create course-specific dirs inside the loop
        os.makedirs(temp_audio_dir_abs, exist_ok=True)
    except OSError as e:
        app.logger.error(f"创建临时音频目录失败: {e}")
        return jsonify({'success': False, 'message': f'无法创建必要的服务器临时目录: {e}'}), 500

    for question in questions_to_process:
        temp_audio_save_path = None
        video_save_path_abs = None
        relative_video_url = None  # Define here for clarity

        try:
            # --- Construct Course and Question Specific Paths ---
            # Filesystem subdirectory for this specific course and question type
            # e.g., generated_videos/courses/5/questions
            course_question_subdir_rel = os.path.join(COURSE_VIDEO_BASE_SUBDIR, str(course_id), 'questions')
            # Absolute filesystem directory for this course's question videos
            # e.g., /path/to/project/static/generated_videos/courses/5/questions
            course_question_dir_abs = os.path.join(static_folder_path, course_question_subdir_rel)

            # --- Ensure the course-specific video directory exists ---
            try:
                os.makedirs(course_question_dir_abs, exist_ok=True)
            except OSError as e:
                error_msg = f"为课程 {course_id} 创建视频目录失败: {e}"
                app.logger.error(error_msg)
                errors.append(error_msg)
                failed_count += 1
                updated_questions_data.append(question.to_dict())  # Append current data before skipping
                continue  # Skip this question if directory creation fails

            # --- Define Filename and Final Paths ---
            # Filename now only needs question ID for uniqueness within its course dir
            video_filename = f"question_{question.id}.mp4"

            # Construct the relative URL path (using posixpath for forward slashes)
            # e.g., /static/generated_videos/courses/5/questions/question_123.mp4
            relative_video_url = "/" + posixpath.join('static', course_question_subdir_rel, video_filename)

            # Construct the absolute filesystem path for saving the video
            # e.g., /path/to/project/static/generated_videos/courses/5/questions/question_123.mp4
            video_save_path_abs = os.path.join(course_question_dir_abs, video_filename)

            # --- Check if video already exists (using new paths) ---
            if question.video_url == relative_video_url and os.path.exists(video_save_path_abs):
                app.logger.info(
                    f"问题 {question.id} (课程 {course_id}) 已有视频 ({relative_video_url}) 且文件存在，跳过。")
                skipped_count += 1
                updated_questions_data.append(question.to_dict())
                continue
            elif question.video_url:
                app.logger.warning(
                    f"问题 {question.id} (课程 {course_id}) 已有视频URL ({question.video_url}) 但与预期({relative_video_url})不符或文件不存在，将重新生成。")

            if not question.content:
                app.logger.warning(f"问题 {question.id} (课程 {course_id}) 内容为空，跳过。")
                skipped_count += 1
                updated_questions_data.append(question.to_dict())
                continue

            # --- Prepare Paths for Generation ---
            temp_audio_filename = f"question_{question.id}_course_{course_id}_{uuid.uuid4()}.wav"  # Make temp name unique across courses too
            temp_audio_save_path = os.path.join(temp_audio_dir_abs, temp_audio_filename)

            app.logger.info(
                f"正在为问题 {question.id} (课程 {course_id}) 生成视频... 输出到文件系统: {video_save_path_abs}, 临时音频: {temp_audio_save_path}")

            # --- Call Video Generation Function ---
            success = text_to_talking_head(
                text=question.content,
                output_path=video_save_path_abs,
                audio_path=temp_audio_save_path,
            )

            if success:
                # --- Update Database with RELATIVE URL ---
                question.video_url = relative_video_url
                db.session.commit()
                generated_count += 1
                app.logger.info(
                    f"问题 {question.id} (课程 {course_id}) 视频生成成功，URL: {relative_video_url}, 文件: {video_save_path_abs}")
            else:
                failed_count += 1
                error_msg = f"问题 {question.id} (课程 {course_id}) 视频生成函数返回失败。"
                errors.append(error_msg)
                app.logger.error(error_msg)

        except Exception as e:
            db.session.rollback()
            failed_count += 1
            error_msg = f"为问题 {question.id} (课程 {course_id}) 处理时发生异常: {str(e)}"
            errors.append(error_msg)
            app.logger.error(error_msg)
            app.logger.error(traceback.format_exc())

        finally:
            # --- Clean Up Temporary Audio File ---
            if temp_audio_save_path and os.path.exists(temp_audio_save_path):
                try:
                    os.remove(temp_audio_save_path)
                    app.logger.debug(f"已删除临时音频文件: {temp_audio_save_path}")
                except OSError as rm_err:
                    app.logger.error(f"无法删除临时音频文件 {temp_audio_save_path}: {rm_err}")

        # Append the (potentially updated) question data after processing each question
        # Ensure the question object is refreshed if rollback occurred, or use latest data
        # Re-fetching might be safer after potential rollback/commit issues
        # db.session.refresh(question) # Or re-query if needed
        updated_questions_data.append(question.to_dict())  # Assumes to_dict gets latest state

    app.logger.info(
        f"课程 {course_id} 视频批量生成完成。成功: {generated_count}, 跳过: {skipped_count}, 失败: {failed_count}")

    return jsonify({
        'success': True,
        'message': f'课程 {course_id} 视频批量生成处理完成。',
        'total_questions': len(questions_to_process),
        'generated_count': generated_count,
        'skipped_count': skipped_count,
        'failed_count': failed_count,
        'errors': errors,
        'questions': updated_questions_data
    })

# --- 获取单个问题视频 URL 的路由 ---
@app.route('/api/questions/<int:question_id>/video_url', methods=['GET'])
def get_question_video_url(question_id):
    """获取指定问题的视频 URL (如果已生成)"""
    question = Question.query.get_or_404(question_id)
    if question.video_url:
        return jsonify({'success': True, 'video_url': question.video_url})
    else:
        # 如果希望在获取时若没有视频则触发单个生成，可以在这里调用之前的单个生成逻辑
        # 但根据当前需求，这里只负责获取已有的
        return jsonify({'success': False, 'message': '该问题尚未生成视频或正在生成中。'}), 404

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.password == data.get('password'):
        session['user_id'] = user.id
        return jsonify({'success': True, 'user': user.to_dict()})
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/current_user', methods=['GET'])
def current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return jsonify({'logged_in': True, 'user': user.to_dict()})
    return jsonify({'logged_in': False})

# 课程管理
@app.route('/api/courses', methods=['GET'])
def get_courses():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role == 'teacher':
        courses = user.teaching_courses.all()
    else:
        # 学生可以查看所有课程，不局限于已选择的课程
        courses = Course.query.all()
    
    return jsonify({'success': True, 'courses': [course.to_dict() for course in courses]})

@app.route('/api/courses', methods=['POST'])
def create_course():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以创建课程'}), 403
    
    title = request.form.get('title')
    description = request.form.get('description')
    
    # 处理图片上传
    image_file = request.files.get('image')
    image_path = None
    if image_file:
        filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
        image_path = os.path.join('course_images', filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
    
    # 处理课程文件上传
    course_file = request.files.get('file')
    file_path = None
    if course_file:
        filename = secure_filename(f"{uuid.uuid4()}_{course_file.filename}")
        file_path = os.path.join('course_files', filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        course_file.save(full_path)
        
        # 生成知识图谱
        try:
            file_content = read_file_content(full_path)
            if file_content:
                knowledge_points = knowledge_extract(file_content)
                knowledge_graph_json = generate_knowledge_graph(knowledge_points)
                
                # 生成问题和答案
                subject, questions, answers = question_ask(knowledge_points, 5)  # 生成5个问题
            else:
                knowledge_graph_json = json.dumps({"name": "知识图谱", "children": []})
                questions = []
                answers = []
        except Exception as e:
            print(f"生成知识图谱和问题时出错: {str(e)}")
            knowledge_graph_json = json.dumps({"name": "知识图谱", "children": []})
            questions = []
            answers = []
    else:
        knowledge_graph_json = json.dumps({"name": "知识图谱", "children": []})
        questions = []
        answers = []
    
    # 创建课程
    course = Course(
        title=title,
        description=description,
        image_path=image_path,
        file_path=file_path,
        knowledge_graph=knowledge_graph_json  # 确保知识图谱JSON保存到数据库
    )
    course.teachers.append(user)
    
    db.session.add(course)
    db.session.flush()  # 刷新会话以获取课程ID
    
    # 添加问题
    for i in range(len(questions)):
        if i < len(answers):  # 确保问题和答案数量一致
            question = Question(
                content=questions[i],
                reference_answer=answers[i],
                course_id=course.id
            )
            db.session.add(question)
    
    db.session.commit()
    
    return jsonify({'success': True, 'course': course.to_dict()})

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({'success': True, 'course': course.to_dict()})

@app.route('/api/courses/<int:course_id>/knowledge_graph', methods=['GET'])
def get_knowledge_graph(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({'success': True, 'knowledge_graph': json.loads(course.knowledge_graph)})

@app.route('/api/courses/<int:course_id>/questions', methods=['GET'])
def get_course_questions(course_id):
    questions = Question.query.filter_by(course_id=course_id).all()
    return jsonify({'success': True, 'questions': [q.to_dict() for q in questions]})

# 学生提交答案
@app.route('/api/questions/<int:question_id>/answer', methods=['POST'])
def submit_answer(question_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'student':
        return jsonify({'success': False, 'message': '只有学生可以提交答案'}), 403
    
    question = Question.query.get_or_404(question_id)
    answer_content = request.json.get('answer')
    
    # 评估答案
    try:
        evaluation = evaluate_student_answer(
            question.content, 
            answer_content, 
            question.reference_answer
        )
    except Exception as e:
        print(f"评估答案时出错: {str(e)}")
        evaluation = {"level": "无法评估", "score": 0, "feedback": "系统无法评估您的答案，请稍后再试。"}
    
    # 保存学生答案和评估结果
    student_answer = StudentAnswer(
        content=answer_content,
        score=evaluation.get('score', 0),
        feedback=evaluation.get('feedback', ''),
        student_id=user_id,
        question_id=question_id
    )
    
    db.session.add(student_answer)
    db.session.commit()
    print(evaluation)
    return jsonify({
        'success': True, 
        'evaluation': evaluation,
        'answer_id': student_answer.id
    })

# 用户管理（仅限教师）
@app.route('/api/students', methods=['GET'])
def get_students():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看学生列表'}), 403
    
    students = User.query.filter_by(role='student').all()
    return jsonify({'success': True, 'students': [s.to_dict() for s in students]})

@app.route('/api/courses/<int:course_id>/students', methods=['POST'])
def add_student_to_course(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以添加学生到课程'}), 403
    
    course = Course.query.get_or_404(course_id)
    
    # 检查是否是该课程的教师
    if user not in course.teachers:
        return jsonify({'success': False, 'message': '您不是该课程的教师'}), 403
    
    student_id = request.json.get('student_id')
    student = User.query.get_or_404(student_id)
    
    if student.role != 'student':
        return jsonify({'success': False, 'message': '只能添加学生角色到课程'}), 400
    
    if student in course.students:
        return jsonify({'success': False, 'message': '该学生已在课程中'}), 400
    
    course.students.append(student)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': '教育系统API服务运行正常',
        'api_version': '1.0',
        'endpoints': {
            'login': '/api/login',
            'courses': '/api/courses',
            'questions': '/api/questions/{id}/answer'
        },
        'test_accounts': {
            'teacher': 'teacher1/123456',
            'student': 'student1/123456'
        }
    })

# 添加获取学生的答案历史记录
@app.route('/api/courses/<int:course_id>/my-answers', methods=['GET'])
def get_student_course_answers(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    # 获取该课程的所有问题
    course_questions = Question.query.filter_by(course_id=course_id).all()
    question_ids = [q.id for q in course_questions]
    
    # 获取学生对这些问题的答案
    answers = StudentAnswer.query.filter(
        StudentAnswer.student_id == user_id,
        StudentAnswer.question_id.in_(question_ids)
    ).all()
    
    return jsonify({
        'success': True,
        'answers': [answer.to_dict() for answer in answers]
    })

# 添加获取课程所有学生答题情况的API
@app.route('/api/courses/<int:course_id>/answers', methods=['GET'])
def get_course_answers(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看所有学生答题情况'}), 403
    
    # 获取该课程的所有问题
    course_questions = Question.query.filter_by(course_id=course_id).all()
    question_ids = [q.id for q in course_questions]
    
    # 查询所有学生对这些问题的答案
    student_answers = StudentAnswer.query.filter(
        StudentAnswer.question_id.in_(question_ids)
    ).all()
    
    # 准备返回结果
    enriched_answers = []
    for answer in student_answers:
        student = User.query.get(answer.student_id)
        question = Question.query.get(answer.question_id)
        
        answer_dict = answer.to_dict()
        answer_dict['student_name'] = student.username if student else "未知学生"
        answer_dict['question_content'] = question.content if question else "未知问题"
        
        enriched_answers.append(answer_dict)
    
    return jsonify({
        'success': True,
        'answers': enriched_answers
    })

# 添加统计API
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看统计数据'}), 403
    
    # 获取基础统计数据
    course_count = Course.query.count()
    student_count = User.query.filter_by(role='student').count()
    question_count = Question.query.count()
    answer_count = StudentAnswer.query.count()
    
    return jsonify({
        'success': True,
        'course_count': course_count,
        'student_count': student_count,
        'question_count': question_count,
        'answer_count': answer_count
    })

# 添加学生答题情况统计API
@app.route('/api/score-statistics', methods=['GET'])
def get_score_statistics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看统计数据'}), 403
    
    # 获取所有学生的答题分数分布
    student_answers = StudentAnswer.query.filter(StudentAnswer.score.isnot(None)).all()
    
    # 分数范围统计
    score_ranges = {
        '0-60': 0,
        '60-70': 0,
        '70-80': 0,
        '80-90': 0,
        '90-100': 0
    }
    
    for answer in student_answers:
        score = answer.score
        if score < 60:
            score_ranges['0-60'] += 1
        elif score < 70:
            score_ranges['60-70'] += 1
        elif score < 80:
            score_ranges['70-80'] += 1
        elif score < 90:
            score_ranges['80-90'] += 1
        else:
            score_ranges['90-100'] += 1
    
    # 转换为前端需要的格式
    statistics = [
        {'score_range': key, 'count': value}
        for key, value in score_ranges.items()
    ]
    
    return jsonify({
        'success': True,
        'statistics': statistics
    })

# 添加课程特定的学生答题情况统计API
@app.route('/api/courses/<int:course_id>/score-statistics', methods=['GET'])
def get_course_score_statistics(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看统计数据'}), 403
    
    # 确认课程存在
    course = Course.query.get_or_404(course_id)
    
    # 获取课程题目ID列表
    question_ids = [q.id for q in Question.query.filter_by(course_id=course_id).all()]
    
    # 如果没有题目,返回空数据
    if not question_ids:
        return jsonify({
            'success': True,
            'statistics': []
        })
    
    # 获取所有回答了这些题目且有分数的答案
    student_answers = StudentAnswer.query.filter(
        StudentAnswer.question_id.in_(question_ids),
        StudentAnswer.score.isnot(None)
    ).all()
    
    # 分数范围统计
    score_ranges = {
        '0-60': 0,
        '60-70': 0,
        '70-80': 0,
        '80-90': 0,
        '90-100': 0
    }
    
    for answer in student_answers:
        score = answer.score
        if score < 60:
            score_ranges['0-60'] += 1
        elif score < 70:
            score_ranges['60-70'] += 1
        elif score < 80:
            score_ranges['70-80'] += 1
        elif score < 90:
            score_ranges['80-90'] += 1
        else:
            score_ranges['90-100'] += 1
    
    # 转换为前端需要的格式
    statistics = [
        {'score_range': key, 'count': value}
        for key, value in score_ranges.items()
    ]
    
    return jsonify({
        'success': True,
        'statistics': statistics
    })

# 添加学生学习分析数据API
@app.route('/api/student/learning-analytics', methods=['GET'])
def get_student_learning_analytics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if user.role != 'student':
        return jsonify({'success': False, 'message': '只有学生可以查看个人学习分析'}), 403
    
    try:
        # 获取该学生的所有答题记录
        student_answers = StudentAnswer.query.filter_by(student_id=user_id).all()
        
        # 计算总答题数
        total_questions = len(student_answers)
        
        # 计算平均分
        if total_questions > 0:
            average_score = sum(answer.score for answer in student_answers if answer.score is not None) / total_questions
        else:
            average_score = 0
        
        # 获取学生参与的课程
        courses_data = {}
        course_progress = []
        completed_courses = 0
        in_progress_courses = 0
        not_started_courses = 0
        
        # 获取所有课程
        all_courses = Course.query.all()
        total_courses = len(all_courses)
        
        # 获取学生已回答的课程问题
        answered_course_ids = set()
        for answer in student_answers:
            if answer.question and answer.question.course_id:
                course_id = answer.question.course_id
                if course_id not in courses_data:
                    courses_data[course_id] = {
                        'total_questions': 0,
                        'answered_questions': 0,
                        'total_score': 0
                    }
                
                courses_data[course_id]['answered_questions'] += 1
                if answer.score is not None:
                    courses_data[course_id]['total_score'] += answer.score
                
                answered_course_ids.add(course_id)
        
        # 计算每个课程的总问题数并确定课程状态
        for course in all_courses:
            course_questions = Question.query.filter_by(course_id=course.id).count()
            
            if course.id in courses_data:
                courses_data[course.id]['total_questions'] = course_questions
                answered_percent = (courses_data[course.id]['answered_questions'] / course_questions * 100) if course_questions > 0 else 0
                
                # 确定课程状态
                if answered_percent >= 90:  # 90%以上视为已完成
                    completed_courses += 1
                elif answered_percent > 0:  # 有答题但未达90%视为进行中
                    in_progress_courses += 1
                else:
                    not_started_courses += 1
            else:
                # 未参与的课程
                not_started_courses += 1
        
        # 构建课程进度数据
        course_progress = [
            {'value': completed_courses, 'name': '已完成课程'},
            {'value': in_progress_courses, 'name': '进行中课程'},
            {'value': not_started_courses, 'name': '未开始课程'}
        ]
        
        # 获取最高分课程
        highest_course = None
        highest_avg_score = 0
        
        for course_id, data in courses_data.items():
            if data['answered_questions'] > 0:
                avg_score = data['total_score'] / data['answered_questions']
                if avg_score > highest_avg_score:
                    highest_avg_score = avg_score
                    course = Course.query.get(course_id)
                    if course:
                        highest_course = course.title
        
        # 计算总学习时长 (示例：假设每个答题用时15分钟)
        total_learning_hours = (total_questions * 15) / 60
        
        # 获取最近回答的题目及分数
        recent_question_scores = []
        
        # 按回答时间降序排序，优先展示最近回答的题目
        from datetime import datetime
        sorted_answers = sorted(
            [a for a in student_answers if a.score is not None and a.question is not None],
            key=lambda x: x.created_at if x.created_at else datetime.now(),
            reverse=True
        )
        
        # 取最近10个回答
        for i, answer in enumerate(sorted_answers[:10]):
            question = answer.question
            course = Course.query.get(question.course_id) if question.course_id else None
            
            recent_question_scores.append({
                'questionId': question.id,
                'questionTitle': truncate_text(question.content, 20),  # 截断长文本
                'score': answer.score,
                'courseName': course.title if course else '未知课程'
            })
        
        # 如果没有答题记录，添加一些示例数据以便前端可以显示图表
        if not recent_question_scores:
            recent_question_scores = [
                {'questionId': 1, 'questionTitle': '示例题目1', 'score': 80, 'courseName': '示例课程'},
                {'questionId': 2, 'questionTitle': '示例题目2', 'score': 65, 'courseName': '示例课程'},
                {'questionId': 3, 'questionTitle': '示例题目3', 'score': 90, 'courseName': '示例课程'},
                {'questionId': 4, 'questionTitle': '示例题目4', 'score': 75, 'courseName': '示例课程'}
            ]
        
        # 生成过去7天的学习趋势数据
        from datetime import datetime, timedelta
        
        dates = []
        hours = []
        questions_count = []
        
        today = datetime.now().date()
        
        # 统计每日答题数量
        daily_questions = {}
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = f"{date.month}/{date.day}"
            dates.append(date_str)
            daily_questions[date] = 0
        
        # 统计每天实际回答的题目数量
        for answer in student_answers:
            if answer.created_at:
                answer_date = answer.created_at.date()
                # 仅统计最近7天的数据
                if answer_date in daily_questions:
                    daily_questions[answer_date] += 1
        
        # 生成趋势数据
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            
            # 获取该日期的实际答题数，如果没有则使用0
            day_questions = daily_questions[date]
            questions_count.append(day_questions)
            
            # 估算学习时长 (每题15分钟)
            day_hours = (day_questions * 15) / 60
            hours.append(round(day_hours, 1))
        
        # 如果没有学习记录，添加一些随机数据
        if all(q == 0 for q in questions_count):
            import random
            questions_count = [random.randint(5, 20) for _ in range(7)]
            hours = [round(q * 15 / 60, 1) for q in questions_count]
        
        # 根据平均分确定学习效率等级
        if average_score >= 90:
            efficiency_rating = "优秀"
        elif average_score >= 80:
            efficiency_rating = "良好"
        elif average_score >= 70:
            efficiency_rating = "一般"
        else:
            efficiency_rating = "需努力"
        
        # 构建返回数据
        return jsonify({
            'success': True,
            'total_learning_hours': round(total_learning_hours, 1),
            'completed_courses': completed_courses,
            'total_questions': total_questions,
            'average_score': round(average_score, 1),
            'highest_course': highest_course or '暂无',
            'efficiency_rating': efficiency_rating,
            'course_progress': course_progress,
            'recent_question_scores': recent_question_scores,
            'learning_trend': {
                'dates': dates,
                'hours': hours,
                'questions': questions_count
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error generating learning analytics: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'生成学习分析数据时出错: {str(e)}'}), 500

# 辅助函数：截断文本
def truncate_text(text, max_length=20):
    if not text:
        return "未知问题"
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

# 手动数据库迁移函数
@app.cli.command('migrate-student-answer')
def migrate_student_answer():
    """手动迁移StudentAnswer表，添加created_at字段"""
    try:
        with db.engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(db.text("SHOW COLUMNS FROM student_answer LIKE 'created_at'"))
            exists = result.fetchone() is not None
            
            if not exists:
                # 添加created_at字段
                conn.execute(db.text("ALTER TABLE student_answer ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("成功添加created_at字段到student_answer表")
            else:
                print("created_at字段已存在")
        
        db.session.commit()
        print("迁移完成")
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        db.session.rollback()

# 初始化数据库
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    
    # 创建测试用户
    if not User.query.filter_by(username='teacher1').first():
        teacher = User(username='teacher1', password='123456', role='teacher')
        db.session.add(teacher)
    
    if not User.query.filter_by(username='student1').first():
        student = User(username='student1', password='123456', role='student')
        db.session.add(student)
    
    db.session.commit()
    print('数据库初始化完成')

# 获取特定学生的课程
@app.route('/api/students/<int:student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以查看学生课程'}), 403
    
    # 确保学生存在
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        return jsonify({'success': False, 'message': '指定的用户不是学生'}), 400
    
    # 获取学生选择的课程
    student_courses = student.enrolled_courses.all()
    
    # 转换为字典列表
    courses_data = []
    for course in student_courses:
        courses_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'image_path': course.image_path
        })
    
    return jsonify({
        'success': True,
        'courses': courses_data
    })

# 获取特定学生的答题记录
@app.route('/api/students/<int:student_id>/answers', methods=['GET'])
def get_student_answers(student_id):
    user_id = session.get('user_id')
    print(f"API调用: /api/students/{student_id}/answers，调用者ID: {user_id}")
    
    if not user_id:
        print("错误: 用户未登录")
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        print(f"错误: 未找到用户ID {user_id}")
        return jsonify({'success': False, 'message': '用户不存在'}), 404
        
    print(f"用户角色: {user.role}")
    if user.role != 'teacher':
        print("错误: 非教师用户尝试访问")
        return jsonify({'success': False, 'message': '只有教师可以查看学生答题记录'}), 403
    
    # 确保学生存在
    student = User.query.get_or_404(student_id)
    if not student:
        print(f"错误: 未找到学生ID {student_id}")
        return jsonify({'success': False, 'message': '学生不存在'}), 404
        
    if student.role != 'student':
        print(f"错误: 用户ID {student_id} 不是学生角色")
        return jsonify({'success': False, 'message': '指定的用户不是学生'}), 400
    
    try:
        # 获取学生的答题记录
        student_answers = StudentAnswer.query.filter_by(student_id=student_id).all()
        print(f"查询到 {len(student_answers)} 条答题记录")
        
        # 按课程分组答题记录
        course_answers = {}
        
        for answer in student_answers:
            question = Question.query.get(answer.question_id)
            if not question:
                continue
                
            course = Course.query.get(question.course_id)
            if not course:
                continue
            
            course_id = question.course_id
            
            # 初始化课程数据结构
            if course_id not in course_answers:
                course_answers[course_id] = {
                    'course_id': course_id,
                    'course_title': course.title,
                    'total_answers': 0,
                    'average_score': 0,
                    'total_score': 0,
                    'answers': []
                }
            
            # 添加答题记录
            answer_data = {
                'id': answer.id,
                'content': answer.content,
                'score': answer.score,
                'feedback': answer.feedback,
                'question_id': answer.question_id,
                'question_content': question.content,
                'created_at': answer.created_at.isoformat() if answer.created_at else None
            }
            
            course_answers[course_id]['answers'].append(answer_data)
            course_answers[course_id]['total_answers'] += 1
            if answer.score is not None:
                course_answers[course_id]['total_score'] += answer.score
        
        # 计算每个课程的平均分
        result = []
        for course_id, data in course_answers.items():
            if data['total_answers'] > 0:
                data['average_score'] = round(data['total_score'] / data['total_answers'], 1)
            
            # 按时间倒序排序答题记录
            data['answers'].sort(key=lambda x: x['created_at'] if x['created_at'] else '', reverse=True)
            
            result.append(data)
        
        # 按答题数量倒序排序课程
        result.sort(key=lambda x: x['total_answers'], reverse=True)
        
        print(f"成功处理 {len(result)} 个课程的答题记录")
        return jsonify({
            'success': True,
            'courses': result
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"处理学生答题记录时出错: {str(e)}")
        print(error_trace)
        return jsonify({'success': False, 'message': f'处理学生答题记录时出错: {str(e)}'}), 500

# 添加测试路由，用于调试学生答题记录
@app.route('/api/test/student-answers', methods=['GET'])
def test_student_answers():
    try:
        # 查询所有学生答题记录
        all_answers = StudentAnswer.query.all()
        
        # 查询表的结构信息
        with db.engine.connect() as conn:
            table_info = conn.execute(db.text("DESCRIBE student_answer")).fetchall()
            table_structure = [dict(zip(['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'], row)) for row in table_info]
        
        # 统计每个学生的答题数量
        student_stats = {}
        for answer in all_answers:
            if answer.student_id not in student_stats:
                student_stats[answer.student_id] = 0
            student_stats[answer.student_id] += 1
        
        # 获取所有学生信息
        all_students = User.query.filter_by(role='student').all()
        students_info = [{'id': s.id, 'username': s.username, 'answer_count': student_stats.get(s.id, 0)} for s in all_students]
        
        return jsonify({
            'success': True,
            'table_structure': table_structure,
            'total_answers': len(all_answers),
            'students': students_info,
            'first_5_answers': [answer.to_dict() for answer in all_answers[:5]] if all_answers else []
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"测试查询学生答题记录时出错: {str(e)}")
        print(error_trace)
        return jsonify({'success': False, 'message': f'测试查询出错: {str(e)}'}), 500

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        # 从数据库中获取课程
        course = Course.query.get(course_id)
        
        # 如果课程不存在，返回404错误
        if not course:
            return jsonify({"error": "课程不存在"}), 404
            
        # 首先删除与该课程相关的学生答案记录
        course_questions = Question.query.filter_by(course_id=course_id).all()
        question_ids = [q.id for q in course_questions]
        
        if question_ids:
            # 删除学生对这些问题的所有答案
            StudentAnswer.query.filter(StudentAnswer.question_id.in_(question_ids)).delete(synchronize_session=False)
            
            # 删除课程的所有问题
            Question.query.filter_by(course_id=course_id).delete(synchronize_session=False)
        
        # 删除课程与教师和学生的关联（多对多关系）
        # 这些关联会自动删除，因为我们使用了db.Table定义关联表
        
        # 最后删除课程
        db.session.delete(course)
        db.session.commit()
        
        # 返回成功消息
        return jsonify({"message": "课程删除成功"}), 200
    except Exception as e:
        # 发生错误时回滚会话
        db.session.rollback()
        print(f"删除课程时出错: {str(e)}")
        return jsonify({"error": "删除课程失败"}), 500

# 添加一个新的路由，处理没有/api前缀的问题添加请求
@app.route('/courses/<int:course_id>/questions', methods=['POST'])
def add_course_question_no_prefix(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以添加问题'}), 403
    
    # 确认课程存在
    course = Course.query.get_or_404(course_id)
    
    # 获取请求数据
    data = request.json
    content = data.get('content')
    reference_answer = data.get('reference_answer')
    
    if not content or not reference_answer:
        return jsonify({'success': False, 'message': '问题内容和参考答案不能为空'}), 400
    
    try:
        # 创建新问题
        question = Question(
            content=content,
            reference_answer=reference_answer,
            course_id=course_id
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '问题添加成功',
            'question': question.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"添加问题时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'添加问题失败: {str(e)}'}), 500

# 同时为了保持一致性，也添加带/api前缀的路由
@app.route('/api/courses/<int:course_id>/questions', methods=['POST'])
def add_course_question(course_id):
    return add_course_question_no_prefix(course_id)

# 添加删除问题的路由（不带/api前缀）
@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question_no_prefix(question_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以删除问题'}), 403
    
    # 确认问题存在
    question = Question.query.get_or_404(question_id)
    
    try:
        # 先删除与此问题相关的所有学生答案
        StudentAnswer.query.filter_by(question_id=question_id).delete(synchronize_session=False)
        
        # 删除问题
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '问题删除成功'
        })
    except Exception as e:
        db.session.rollback()
        print(f"删除问题时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'删除问题失败: {str(e)}'}), 500

# 同时为了保持一致性，也添加带/api前缀的路由
@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    return delete_question_no_prefix(question_id)

# 添加不带/api前缀的课程更新路由
@app.route('/courses/<int:course_id>', methods=['PUT'])
def update_course_no_prefix(course_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以更新课程'}), 403
    
    # 确认课程存在
    course = Course.query.get_or_404(course_id)
    
    # 检查当前用户是否是该课程的教师
    if user not in course.teachers:
        return jsonify({'success': False, 'message': '您不是该课程的教师'}), 403
    
    # 获取表单数据
    title = request.form.get('title')
    description = request.form.get('description')
    
    # 更新课程基本信息
    if title:
        course.title = title
    if description:
        course.description = description
    
    # 处理图片上传
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        try:
            # 删除旧图片（如果存在且不是默认图片）
            if course.image_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], course.image_path)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], course.image_path))
            
            # 保存新图片
            filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
            image_path = os.path.join('course_images', filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
            course.image_path = image_path
        except Exception as e:
            print(f"更新课程图片时出错: {str(e)}")
            return jsonify({'success': False, 'message': f'更新课程图片失败: {str(e)}'}), 500
    
    # 处理课程文件上传
    course_file = request.files.get('file')
    if course_file and course_file.filename:
        try:
            # 删除旧文件（如果存在）
            if course.file_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], course.file_path)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], course.file_path))
            
            # 保存新文件
            filename = secure_filename(f"{uuid.uuid4()}_{course_file.filename}")
            file_path = os.path.join('course_files', filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            course_file.save(full_path)
            course.file_path = file_path
            
            # 重新生成知识图谱
            try:
                file_content = read_file_content(full_path)
                if file_content:
                    knowledge_points = knowledge_extract(file_content)
                    knowledge_graph_json = generate_knowledge_graph(knowledge_points)
                    course.knowledge_graph = knowledge_graph_json
            except Exception as ke:
                print(f"更新知识图谱时出错: {str(ke)}")
                # 继续处理，即使知识图谱生成失败
        except Exception as e:
            print(f"更新课程文件时出错: {str(e)}")
            return jsonify({'success': False, 'message': f'更新课程文件失败: {str(e)}'}), 500
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '课程更新成功', 'course': course.to_dict()})
    except Exception as e:
        db.session.rollback()
        print(f"保存课程更新时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'更新课程失败: {str(e)}'}), 500

# 同时为了保持一致性，也添加带/api前缀的路由
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    return update_course_no_prefix(course_id)

# 添加编辑问题的路由（带/api前缀）
@app.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    user = User.query.get(user_id)
    if user.role != 'teacher':
        return jsonify({'success': False, 'message': '只有教师可以编辑问题'}), 403
    
    # 确认问题存在
    question = Question.query.get_or_404(question_id)
    
    # 获取请求数据
    data = request.json
    content = data.get('content')
    reference_answer = data.get('reference_answer')
    
    if not content or not reference_answer:
        return jsonify({'success': False, 'message': '问题内容和参考答案不能为空'}), 400
    
    try:
        # 更新问题
        question.content = content
        question.reference_answer = reference_answer
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '问题更新成功',
            'question': question.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"更新问题时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'更新问题失败: {str(e)}'}), 500

# 添加编辑问题的路由（不带/api前缀）
@app.route('/questions/<int:question_id>', methods=['PUT'])
def update_question_no_prefix(question_id):
    return update_question(question_id)

# 添加修改密码的API接口
@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    try:
        user_id = session.get('user_id')
        print(f"修改密码请求，用户ID: {user_id}")
        
        if not user_id:
            print("修改密码失败：用户未登录")
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取请求数据
        if not request.is_json:
            print(f"修改密码失败：请求内容类型不是JSON，实际类型: {request.content_type}")
            return jsonify({'success': False, 'message': '请求格式错误，需要JSON格式'}), 400
        
        data = request.json
        print(f"请求数据: {data}")
        
        # 兼容两种可能的参数名(oldPassword/current_password)
        old_password = data.get('oldPassword') or data.get('current_password')
        new_password = data.get('newPassword') or data.get('new_password')
        
        if not old_password:
            print("修改密码失败：旧密码为空")
            return jsonify({'success': False, 'message': '旧密码不能为空'}), 400
            
        if not new_password:
            print("修改密码失败：新密码为空")
            return jsonify({'success': False, 'message': '新密码不能为空'}), 400
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            print(f"修改密码失败：用户ID {user_id} 不存在")
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 验证旧密码
        if user.password != old_password:
            print(f"修改密码失败：用户 {user.username} 提供的旧密码不正确")
            return jsonify({'success': False, 'message': '旧密码不正确'}), 403
        
        # 更新密码
        user.password = new_password
        db.session.commit()
        print(f"密码修改成功：用户 {user.username}")
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        error_msg = f"修改密码时出现异常: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': '密码修改失败，请稍后重试', 'error': str(e)}), 500

# 添加个人信息更新的API接口
@app.route('/api/user/update-info', methods=['POST'])
def update_user_info():
    try:
        user_id = session.get('user_id')
        print(f"更新个人信息请求，用户ID: {user_id}")
        
        if not user_id:
            print("更新个人信息失败：用户未登录")
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取请求数据
        if not request.is_json:
            print(f"更新个人信息失败：请求内容类型不是JSON，实际类型: {request.content_type}")
            return jsonify({'success': False, 'message': '请求格式错误，需要JSON格式'}), 400
        
        data = request.json
        print(f"请求数据: {data}")
        

        email = data.get('email')
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            print(f"更新个人信息失败：用户ID {user_id} 不存在")
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        

        has_email = hasattr(User, 'email')
        
        # 如果模型中没有这些字段，返回成功但提示需要更新数据库模型

        # 更新用户信息

        
        if has_email and email is not None:
            user.email = email
        
        # 提交更改
        db.session.commit()
        print(f"用户信息更新成功")
        
        return jsonify({
            'success': True, 
            'message': '个人信息保存成功'
        })
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"更新个人信息时出现异常: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': '保存个人信息失败，请稍后重试', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
