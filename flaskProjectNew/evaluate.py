import json
import os
import logging
from openai import OpenAI
import dashscope

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('evaluate')

#评估函数
def evaluate_student_answer(question, student_answer, reference_answer):
    logger.info(f"开始评估答案 - 问题: {question[:30]}...")
    
    # 设计大模型评估prompt
    evaluation_prompt_template = """
    请根据以下信息评估学生的回答：
    ---
    **问题**：{question}
    **参考答案**：{reference_answer}
    **学生回答**：{student_answer}
    ---
    评估要求：
    1. 满分100分，从准确性（60%）、完整性（30%）、语言表达（10%）评分，并给出等级。
    2. 指出回答中的错误或遗漏。
    3. 用JSON格式返回结果，包含level,score和feedback字段。

    评估结果：
    """

    #大模型输入
    prompt = evaluation_prompt_template.format(
        question=question,
        reference_answer=reference_answer,
        student_answer=student_answer
    )
    
    #回答
    messages = [
    {'role': 'system', 'content': prompt}
    #{'role': 'user', 'content': prompt}
    ]
    
    try:
        logger.info("调用大模型API进行评估...")
        response = dashscope.Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        #api_key=os.getenv('DASHSCOPE_API_KEY'),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-5fb4c90206e84a7b9d88fc91e72fbe44",
        model="qwen-plus",
        messages=messages,
        result_format='message',
        response_format={"type": "json_object"}
        )
        
        # 解析模型输出
        if hasattr(response, 'output') and hasattr(response.output, 'choices') and len(response.output.choices) > 0:
            result = json.loads(response.output.choices[0].message.content)
            logger.info(f"评估完成 - 得分: {result.get('score', '未知')}")
            
            # 确保结果包含所需字段
            if 'score' not in result:
                result['score'] = 0
            if 'feedback' not in result:
                result['feedback'] = "评估系统未能提供反馈。"
            if 'level' not in result:
                result['level'] = "未评级"
                
            return result
        else:
            logger.error(f"API响应格式异常: {response}")
            return {"error": "评估失败，API响应格式异常", "score": 0, "feedback": "系统无法评估您的答案，请稍后再试。", "level": "未评级"}
    except Exception as e:
        logger.error(f"评估过程出错: {str(e)}")
        return {"error": f"评估失败: {str(e)}", "score": 0, "feedback": "系统评估时遇到技术问题，请稍后再试。", "level": "未评级"}
    
if __name__ == "__main__":
    question_list = [
        "计算机网络的定义是什么？"
    ]
    student_answer_list = [
        "我不知道。"
    ]
    reference_answer_list = [
        "将分散的计算机等设备相互连接，以实现资源共享与信息传递。"
    ]

    evaluation_results = []
    for i in range(len(question_list)):
        result = evaluate_student_answer(question_list[i], student_answer_list[i],
                                         reference_answer_list[i])
        evaluation_results.append(result)

    print("评估结果：")
    print(json.dumps(evaluation_results, ensure_ascii=False, indent=4))

