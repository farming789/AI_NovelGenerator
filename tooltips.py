# tooltips.py
# -*- coding: utf-8 -*-

tooltips = {
    "api_key": "在这里填写你的API Key。如果使用OpenAI官方接口，请在 https://platform.openai.com/account/api-keys 获取。",
    "base_url": "模型的接口地址。若使用OpenAI官方：https://api.openai.com/v1。若使用Ollama本地部署，则类似 http://localhost:11434/v1。调用Gemini模型则无需填写。",
    "interface_format": "指定LLM接口兼容格式，可选DeepSeek、OpenAI、Ollama、ML Studio、Gemini等。\n\n注意："+
                        "OpenAI 兼容是指的可以通过该标准请求的任何接口，不是只允许使用api.openai.com接口\n"+
                        "例如Ollama接口格式也兼容OpenAI，可以无需修改直接使用\n"+
                        "ML Studio接口格式与OpenAI接口格式也一致。",
    "model_name": "要使用的模型名称，例如deepseek-reasoner、gpt-4o等。如果是Ollama等，请填写你下载好的本地模型名。",
    "temperature": "生成文本的随机度。数值越大越具有发散性，越小越严谨。",
    "max_tokens": "限制单次生成的最大Token数。范围1~100000，请根据模型上下文及需求填写合适值。\n"+
                  "以下是一些常见模型的最大值：\n"+
                  "o1：100,000\n"+
                  "o1-mini：65,536\n"+
                  "gpt-4o：16384\n"+
                  "gpt-4o-mini：16384\n"+
                  "deepseek-reasoner：8192\n"+
                  "deepseek-chat：4096\n",
    "embedding_api_key": "调用Embedding模型时所需的API Key。",
    "embedding_interface_format": "Embedding模型接口风格，比如OpenAI或Ollama。",
    "embedding_url": "Embedding模型接口地址。",
    "embedding_model_name": "Embedding模型名称，如text-embedding-ada-002。",
    "embedding_retrieval_k": "向量检索时返回的Top-K结果数量。",
    "topic": "小说的大致主题或主要故事背景描述。",
    "genre": "小说的题材类型，如玄幻、都市、科幻等。",
    "num_chapters": "小说期望的章节总数。",
    "word_number": "每章的目标字数。",
    "filepath": "生成文件存储的根目录路径。所有txt文件、向量库等放在该目录下。",
    "chapter_num": "当前正在处理的章节号，用于生成草稿或定稿操作。",
    "user_guidance": "为本章提供的一些额外指令或写作引导。",
    "writing_style": "小说的整体写作风格，如甜蜜、悬疑、热血、温馨等。这将影响AI生成内容的基调和情感色彩。",
    "characters_involved": "本章需要重点描写或影响剧情的角色名单。",
    "key_items": "在本章中出现的重要道具、线索或物品。",
    "scene_location": "本章主要发生的地点或场景描述。",
    "time_constraint": "本章剧情中涉及的时间压力或时限设置。",
    "interface_config": "选择你要使用的AI接口配置。",
    # ===== 新增：额外设置字段的帮助提示 =====
    "narrative_paradigm": "叙事范式：规定整体叙事结构与手法。\n建议值：\n- 三幕式 / 五幕式 / 英雄之旅\n- 群像并行（多主角轮转）\n- 非线性混剪（时序打乱、插叙/倒叙）\n- 书信体/档案体（以信件、报告、聊天记录呈现）\n- 年谱体/旅行记/案件连环\n示例：‘群像并行·非线性混剪’",
    "hybrid_genre": "题材杂交：主类型+副类型的组合，加强风格混合。\n示例：\n- 科幻×宫廷斗 / 推理×成长 / 爱情×悬疑 / 末世×群像\n- 武侠×科幻（江湖门派×机甲义体）",
    "style_profile": "风格剖面：限定语言与修辞风格。可写逗号分隔的维度。\n可选维度：句法（短/中/长）、修辞（隐喻/转喻/冷面幽默/黑色寓言）、意象域（工业/海洋/矿物/宗教）、语体（口语/文言/诗性）\n示例：‘句法=短；修辞=隐喻；意象=工业；语体=冷面幽默’",
    "perspective_matrix": "视角矩阵：人称×焦点×叙述距离。\n可选项：\n- 人称：一/二/三\n- 焦点：主/副/群像/全知有限\n- 距离：外显（客观）/内隐（贴近）/自由间接引语\n示例：‘人称=三；焦点=群像；距离=自由间接引语’",
    "scene_objectives": "场景目标：用目标替代固定场景清单，避免套路。\n建议关键词：权力再分配、意义反转、证据噪声化、情感错位、信息差扩大、节奏断裂、符号回响\n示例：‘权力再分配；意义反转；证据噪声化’",
    "motif_budget": "母题预算：全书独特母题的配额与分布，限制滥用。\n写法：以‘·’或‘；’分隔，注明‘每章≤1’等限制。\n示例：‘玻璃·潮汐·回声（每章≤1）’",
    "knowledge_injection_policy": "知识注入比例：第三方知识/设定/禁忌避坑的占比控制。\n建议：技法≥60%，设定≤30%，禁忌≥10%。\n示例：‘技法≥60%/设定≤30%/禁忌≥10%’",
    "seed": "随机种子：相同输入+相同seed更易复现结果。\n建议：整数，如 42、2025。留空则由模型自身决定。",
    "variation_factor": "变体因子：在同一seed上再引入轻微差异，便于生成多版本。\n示例：A / B / C 或 1 / 2 / 3"
}
