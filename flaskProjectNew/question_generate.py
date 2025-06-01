import json
from openai import OpenAI
import traceback
import time
import sys
import os

# 配置qwen模型api
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ.get('QWEN_API_KEY', "sk-5fb4c90206e84a7b9d88fc91e72fbe44")
)

def question_ask(main_knowledge, n):
    """
    根据知识点生成问题和参考答案
    :param main_knowledge: 知识点列表
    :param n: 生成问题的数量
    :return: (学科名称, 问题列表, 答案列表)
    """
    try:
        print(f"准备为{n}个知识点生成问题...")
        
        # 检查知识点格式是否正确
        print(f"知识点类型: {type(main_knowledge)}")
        if main_knowledge and len(main_knowledge) > 0:
            print(f"第一个知识点类型: {type(main_knowledge[0])}")
            print(f"第一个知识点内容: {main_knowledge[0]}")
            
        if not isinstance(main_knowledge, list):
            print(f"警告: 传入的知识点不是列表，而是 {type(main_knowledge)}")
            # 将非列表转换为列表
            if isinstance(main_knowledge, dict):
                main_knowledge = [main_knowledge]
            else:
                main_knowledge = [{"title": "未知主题", "content": str(main_knowledge)}]
        
        # 确保知识点列表不为空
        if not main_knowledge:
            print("警告: 传入的知识点列表为空")
            return "未知主题", [], []
        
        print(f"知识点数量: {len(main_knowledge)}")
        
        # 格式化知识点以便于AI处理
        formatted_knowledge = []
        for item in main_knowledge:
            if isinstance(item, dict):
                if 'title' in item and 'content' in item:
                    formatted_knowledge.append({
                        "title": item['title'],
                        "content": item['content']
                    })
                elif 'name' in item and 'description' in item:
                    formatted_knowledge.append({
                        "title": item['name'],
                        "content": item['description']
                    })
                else:
                    print(f"警告: 跳过未知格式的知识点: {item}")
        
        if not formatted_knowledge:
            print("警告: 无法格式化任何知识点，将使用原始知识点")
            formatted_knowledge = main_knowledge
            
        # 限制知识点数量，避免超出模型处理能力
        if len(formatted_knowledge) > 20:
            print(f"警告: 知识点数量过多({len(formatted_knowledge)}), 截取前20个")
            formatted_knowledge = formatted_knowledge[:20]
            
        main_knowledge_str = json.dumps(formatted_knowledge, ensure_ascii=False, indent=4)
        print(f"知识点字符串长度: {len(main_knowledge_str)}")
        
        # 截取部分知识点以便于查看
        print(f"知识点内容预览: {main_knowledge_str[:200]}...")
        
        # API调用重试机制
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"尝试 API 调用 (尝试 {retry_count + 1}/{max_retries})...")
                
                # 构建提示词
                prompt = f"""
                你是一位知识渊博且专业的大学老师，请你根据下面提供的知识点为学生生成{n}个重要问题和参考答案。
                每个问题都应该清晰明确，且能引发学生的深入思考。问题应该能够全面考察所给知识点的理解。
                请直接生成问题和答案，不要有多余的解释。
                
                输出格式要求为标准JSON，格式如下:
                {{
                "学科名称": "计算机网络",
                "问题列表": [
                    {{
                        "问题": "请解释TCP协议中三次握手的过程及其作用。",
                        "参考答案": "TCP三次握手是指建立TCP连接时客户端和服务器之间进行的三次通信过程。首先，客户端发送SYN报文给服务器；然后，服务器回复SYN+ACK报文；最后，客户端发送ACK报文。这个过程确保了双方都能确认对方的收发能力正常，避免了连接建立后的通信问题。"
                    }},
                    {{
                        "问题": "请比较UDP和TCP协议的主要区别。",
                        "参考答案": "UDP和TCP的主要区别在于：1) TCP是面向连接的协议，而UDP是无连接的；2) TCP提供可靠的数据传输（有确认、重传等机制），UDP不保证可靠交付；3) TCP有流量控制和拥塞控制机制，UDP没有；4) TCP报文开销较大，UDP报文结构简单；5) TCP适用于要求可靠性高但对实时性要求相对较低的应用，如文件传输；UDP适用于实时性要求高的应用，如视频流媒体。"
                    }}
                ]
                }}
                
                请确保：
                1. 生成的问题数量必须是{n}个
                2. 问题应该覆盖所提供知识点的主要内容
                3. 学科名称应根据知识点内容推断
                4. 参考答案应详细且准确
                
                注意：输出必须是标准JSON格式，不要包含JSON外的其他内容。
                """

                # 调用API
                start_time = time.time()
                print("正在调用 API 生成问题...")
                
                completion = client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": main_knowledge_str}
                    ],
                    temperature=0.7,  # 增加一些创造性
                    max_tokens=2000   # 确保有足够的token生成答案
                )
                
                print(f"API 调用完成，耗时 {time.time() - start_time:.2f} 秒")
                
                # 提取 API 响应中的内容
                output = completion.choices[0].message.content
                output = output.replace("```json", "").replace("```", "").strip()
                print(f"API 返回内容长度: {len(output)}")
                print(f"API 返回内容预览: {output[:200]}...")
                
                try:
                    # 解析JSON
                    data = json.loads(output)
                    subject = data.get("学科名称", "未知主题")
                    
                    if "问题列表" not in data:
                        print(f"错误: API 返回的 JSON 中没有 '问题列表' 字段")
                        retry_count += 1
                        continue
                    
                    # 提取问题和答案
                    question_list = []
                    reference_answer_list = []
                    
                    for item in data["问题列表"]:
                        if "问题" in item and "参考答案" in item:
                            question_list.append(item["问题"])
                            reference_answer_list.append(item["参考答案"])
                    
                    if len(question_list) == 0:
                        print("错误: 无法从API响应中提取问题")
                        retry_count += 1
                        continue
                        
                    print(f"成功提取 {len(question_list)} 个问题")
                    print("问题示例:")
                    for i, q in enumerate(question_list[:2]):
                        print(f"  问题 {i+1}: {q}")
                        print(f"  答案: {reference_answer_list[i][:100]}...")
                    
                    return subject, question_list, reference_answer_list
                    
                except json.decoder.JSONDecodeError as e:
                    print(f"JSON 解析错误: {str(e)}")
                    print(f"无效的 JSON 字符串: {output}")
                    retry_count += 1
                    
            except Exception as api_error:
                print(f"API 调用错误: {str(api_error)}")
                print(traceback.format_exc())
                retry_count += 1
                time.sleep(2)  # 等待2秒后重试
        
        # 如果所有重试都失败，返回一些基本问题
        print("所有 API 调用尝试都失败，生成基本问题")
        
        basic_questions = []
        basic_answers = []
        
        for i in range(min(n, len(formatted_knowledge))):
            item = formatted_knowledge[i]
            title = item.get("title", "未知主题")
            content = item.get("content", "")
            
            basic_questions.append(f"请介绍一下{title}的主要内容。")
            basic_answers.append(f"{content}\n\n这是关于{title}的基本内容。")
        
        # 如果知识点不足，添加通用问题
        while len(basic_questions) < n:
            idx = len(basic_questions) + 1
            basic_questions.append(f"问题{idx}: 请分析这个主题的实际应用场景。")
            basic_answers.append("这个主题在实际中有多种应用场景，包括但不限于教育、工业和日常生活。具体应用取决于具体情境和需求。")
        
        subject = "知识点综合"
        return subject, basic_questions, basic_answers
    
    except Exception as e:
        print(f"问题生成过程发生异常: {str(e)}")
        print(traceback.format_exc())
        
        # 返回一些基本问题，确保不会返回空列表
        backup_questions = [f"问题{i+1}: 请解释这个主题的基本概念。" for i in range(n)]
        backup_answers = ["这是一个重要的概念，理解它对掌握整个主题至关重要。" for _ in range(n)]
        
        return "异常处理", backup_questions, backup_answers

if __name__ == '__main__':
    knowledges = [
        {
            "name": "基本概念",
            "children": [
                {
                    "name": "定义",
                    "description": "将分散的计算机等设备相互连接，以实现资源共享与信息传递。"
                },
                {
                    "name": "分类",
                    "children": [
                        {
                            "name": "按范围",
                            "children": [
                                {
                                    "name": "局域网（LAN）",
                                    "description": "覆盖范围较小，通常在一个建筑物内或园区内，如学校机房网络。"
                                },
                                {
                                    "name": "城域网（MAN）",
                                    "description": "覆盖范围为城市区域，连接多个局域网。"
                                },
                                {
                                    "name": "广域网（WAN）",
                                    "description": "覆盖范围大，可跨城市、国家甚至全球，如互联网。"
                                }
                            ]
                        },
                        {
                            "name": "按拓扑结构",
                            "children": [
                                {
                                    "name": "总线型",
                                    "description": "所有设备连接在一条总线上，如早期的同轴电缆网络。"
                                },
                                {
                                    "name": "星型",
                                    "description": "以中心节点为核心，其他设备通过线缆连接到中心节点，目前应用广泛。"
                                },
                                {
                                    "name": "环型",
                                    "description": "设备连接成环，数据沿环单向传输。"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "name": "网络协议",
            "children": [
                {
                    "name": "网络层",
                    "children": [
                        {
                            "name": "IP协议",
                            "description": "负责寻址和路由，为数据包分配 IP 地址并选择传输路径。"
                        }
                    ]
                },
                {
                    "name": "传输层",
                    "children": [
                        {
                            "name": "TCP",
                            "description": "保证可靠传输，通过三次握手建立连接，确保数据按序、无差错到达。"
                        },
                        {
                            "name": "UDP",
                            "description": "用于快速传输，不保证数据可靠性，适用于实时性要求高但对数据准确性要求稍低的场景，如视频流。"
                        }
                    ]
                },
                {
                    "name": "应用层",
                    "children": [
                        {
                            "name": "HTTP",
                            "description": "用于网页传输，浏览器与服务器之间通信的协议。"
                        },
                        {
                            "name": "SMTP",
                            "description": "邮件发送协议，负责将邮件从客户端发送到邮件服务器。"
                        }
                    ]
                }
            ]
        },
        {
            "name": "网络管理",
            "children": [
                {
                    "name": "性能管理",
                    "description": "监测网络性能，如带宽利用率、延迟等，确保网络高效运行。"
                },
                {
                    "name": "故障管理",
                    "description": "检测并排除故障，通过监控设备状态和日志，快速定位和解决问题。"
                },
                {
                    "name": "配置管理",
                    "description": "管理设备配置，包括设备参数设置、软件升级等，保证网络设备正常工作。"
                }
            ]
        }
    ]
    n = 5
    subject, question_list, reference_answer_list = question_ask(knowledges, n)
    print("问题及参考答案：")
    print("学科名称:", subject)
    print("问题列表:", json.dumps(question_list, ensure_ascii=False, indent=4))
    print("参考答案列表:", json.dumps(reference_answer_list, ensure_ascii=False, indent=4))