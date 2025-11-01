# config_manager.py
# -*- coding: utf-8 -*-
import json
import os
import threading
import shutil
from datetime import datetime
from llm_adapters import create_llm_adapter
from embedding_adapters import create_embedding_adapter


def load_config(config_file: str) -> dict:
    """从指定的 config_file 加载配置，若不存在则创建一个默认配置文件。"""

    # PenBo 修改代码，增加配置文件不存在则创建一个默认配置文件
    if not os.path.exists(config_file):
        create_config(config_file)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
            return {}


# PenBo 增加了创建默认配置文件函数
def create_config(config_file: str) -> dict:
    """创建一个创建默认配置文件。"""
    config = {
    "last_interface_format": "OpenAI",
    "last_embedding_interface_format": "OpenAI",
    "llm_configs": {
        "DeepSeek V3": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "GPT 5": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-5",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "Gemini 2.5 Pro": {
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model_name": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 32768,
            "timeout": 600,
            "interface_format": "OpenAI"
        }
    },
    "embedding_configs": {
        "OpenAI": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "text-embedding-ada-002",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        }
    },
    "default_novel_params": {
        "topic": "",
        "genre": "玄幻",
        "num_chapters": 100,
        "word_number": 3000,
        "writing_style": "",
        "user_guidance": "",
        "characters_involved": "",
        "key_items": "",
        "scene_location": "",
        "time_constraint": ""
    },
    "choose_configs": {
        "prompt_draft_llm": "DeepSeek V3",
        "chapter_outline_llm": "DeepSeek V3",
        "architecture_llm": "Gemini 2.5 Pro",
        "final_chapter_llm": "GPT 5",
        "consistency_review_llm": "DeepSeek V3"
    },
    "proxy_setting": {
        "proxy_url": "127.0.0.1",
        "proxy_port": "",
        "enabled": False
    },
    "webdav_config": {
        "webdav_url": "",
        "webdav_username": "",
        "webdav_password": ""
    }
}
    save_config(config, config_file)



def save_config(config_data: dict, config_file: str) -> bool:
    """将 config_data 保存到 config_file 中，返回 True/False 表示是否成功。"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    def task():
        try:
            log_func("开始测试LLM配置...")
            llm_adapter = create_llm_adapter(
                interface_format=interface_format,
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            test_prompt = "Please reply 'OK'"
            response = llm_adapter.invoke(test_prompt)
            if response:
                log_func("✅ LLM配置测试成功！")
                log_func(f"测试回复: {response}")
            else:
                log_func("❌ LLM配置测试失败：未获取到响应")
        except Exception as e:
            log_func(f"❌ LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")

    threading.Thread(target=task, daemon=True).start()

def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    def task():
        try:
            log_func("开始测试Embedding配置...")
            embedding_adapter = create_embedding_adapter(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )

            test_text = "测试文本"
            embeddings = embedding_adapter.embed_query(test_text)
            if embeddings and len(embeddings) > 0:
                log_func("✅ Embedding配置测试成功！")
                log_func(f"生成的向量维度: {len(embeddings)}")
            else:
                log_func("❌ Embedding配置测试失败：未获取到向量")
        except Exception as e:
            log_func(f"❌ Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")

    threading.Thread(target=task, daemon=True).start()


# =============== 小说配置管理功能 ===============

def get_novels_root_dir() -> str:
    """获取小说项目根目录路径"""
    return os.path.join(os.getcwd(), "novels")


def ensure_novels_dir() -> str:
    """确保小说项目目录存在，返回目录路径"""
    novels_dir = get_novels_root_dir()
    os.makedirs(novels_dir, exist_ok=True)
    return novels_dir


def list_novel_projects() -> list:
    """列出所有小说项目"""
    novels_dir = ensure_novels_dir()
    projects = []
    
    for item in os.listdir(novels_dir):
        project_path = os.path.join(novels_dir, item)
        if os.path.isdir(project_path):
            config_file = os.path.join(project_path, "novel_config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    projects.append({
                        "name": item,
                        "path": project_path,
                        "title": config.get("novel_info", {}).get("title", item),
                        "created_at": config.get("novel_info", {}).get("created_at", ""),
                        "last_modified": config.get("novel_info", {}).get("last_modified", "")
                    })
                except:
                    # 配置文件损坏，跳过
                    continue
    
    # 按最后修改时间排序
    projects.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
    return projects


def create_novel_project(project_name: str, global_config: dict) -> str:
    """创建新的小说项目"""
    novels_dir = ensure_novels_dir()
    project_path = os.path.join(novels_dir, project_name)
    
    if os.path.exists(project_path):
        raise ValueError(f"项目 '{project_name}' 已存在")
    
    # 创建项目目录
    os.makedirs(project_path, exist_ok=True)
    
    # 创建小说配置文件
    novel_config = {
        "novel_info": {
            "title": project_name,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        },
        "novel_params": global_config.get("default_novel_params", {}).copy(),
        "generation_state": {
            "current_chapter": 1,
            "architecture_generated": False,
            "blueprint_generated": False,
            "last_generation_step": "none"
        }
    }
    
    # 设置默认文件路径
    novel_config["novel_params"]["filepath"] = project_path
    
    save_novel_config(project_path, novel_config)
    return project_path


def load_novel_config(project_path: str) -> dict:
    """加载指定项目的小说配置"""
    config_file = os.path.join(project_path, "novel_config.json")
    
    if not os.path.exists(config_file):
        # 如果配置文件不存在，创建默认配置
        novels_dir = ensure_novels_dir()
        global_config_file = os.path.join(os.getcwd(), "config.json")
        global_config = load_config(global_config_file)
        
        novel_config = {
            "novel_info": {
                "title": os.path.basename(project_path),
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat()
            },
            "novel_params": global_config.get("default_novel_params", {}).copy(),
            "generation_state": {
                "current_chapter": 1,
                "architecture_generated": False,
                "blueprint_generated": False,
                "last_generation_step": "none"
            }
        }
        
        # 设置默认文件路径
        novel_config["novel_params"]["filepath"] = project_path
        save_novel_config(project_path, novel_config)
        return novel_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"无法加载小说配置: {str(e)}")


def save_novel_config(project_path: str, novel_config: dict) -> bool:
    """保存小说配置到指定项目"""
    config_file = os.path.join(project_path, "novel_config.json")
    
    # 更新最后修改时间
    if "novel_info" not in novel_config:
        novel_config["novel_info"] = {}
    novel_config["novel_info"]["last_modified"] = datetime.now().isoformat()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(novel_config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        return False


def delete_novel_project(project_name: str) -> bool:
    """删除小说项目"""
    novels_dir = ensure_novels_dir()
    project_path = os.path.join(novels_dir, project_name)
    
    if not os.path.exists(project_path):
        return False
    
    try:
        shutil.rmtree(project_path)
        return True
    except Exception as e:
        return False


# 迁移逻辑不再需要，已移除 migrate_legacy_config


def get_current_novel_config(project_path: str) -> dict:
    """获取当前小说项目的配置，如果不存在则创建默认项目"""
    if not project_path or not os.path.exists(project_path):
        # 如果没有指定项目路径，使用第一个可用项目
        projects = list_novel_projects()
        if projects:
            project_path = projects[0]["path"]
        else:
            # 创建默认项目
            novels_dir = ensure_novels_dir()
            global_config_file = os.path.join(os.getcwd(), "config.json")
            global_config = load_config(global_config_file)
            default_path = os.path.join(novels_dir, "默认小说项目")
            if os.path.exists(default_path):
                project_path = default_path
            else:
                project_path = create_novel_project("默认小说项目", global_config)
    
    return load_novel_config(project_path)