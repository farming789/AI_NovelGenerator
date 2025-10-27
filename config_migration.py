# config_migration.py
# -*- coding: utf-8 -*-
"""
配置迁移工具：将旧的全局配置迁移到新的小说项目配置结构
"""
import os
import json
import shutil
from datetime import datetime
from config_manager import (
    load_config, save_config, migrate_legacy_config,
    create_novel_project, save_novel_config, list_novel_projects
)


def backup_config(config_file: str) -> str:
    """备份配置文件"""
    if not os.path.exists(config_file):
        return ""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{config_file}.backup_{timestamp}"
    shutil.copy2(config_file, backup_file)
    return backup_file


def migrate_config_to_novel_structure(config_file: str = "config.json") -> bool:
    """
    将旧配置迁移到新的小说项目结构
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        bool: 迁移是否成功
    """
    try:
        print("开始配置迁移...")
        
        # 1. 备份原配置
        backup_file = backup_config(config_file)
        if backup_file:
            print(f"✅ 已备份原配置到: {backup_file}")
        
        # 2. 加载当前配置
        global_config = load_config(config_file)
        
        # 3. 检查是否需要迁移
        if "other_params" not in global_config:
            print("✅ 配置已经是新结构，无需迁移")
            return True
        
        print("📋 发现旧配置结构，开始迁移...")
        
        # 4. 执行迁移
        new_global_config = migrate_legacy_config(global_config)
        
        # 5. 保存新的全局配置
        if save_config(new_global_config, config_file):
            print("✅ 全局配置迁移完成")
        else:
            print("❌ 全局配置保存失败")
            return False
        
        # 6. 验证迁移结果
        projects = list_novel_projects()
        if projects:
            print(f"✅ 成功创建 {len(projects)} 个小说项目:")
            for project in projects:
                print(f"   - {project['title']} ({project['name']})")
        else:
            print("⚠️ 未找到小说项目，可能迁移失败")
            return False
        
        print("🎉 配置迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 配置迁移失败: {str(e)}")
        return False


def restore_config_from_backup(backup_file: str, config_file: str = "config.json") -> bool:
    """从备份恢复配置"""
    try:
        if not os.path.exists(backup_file):
            print(f"❌ 备份文件不存在: {backup_file}")
            return False
        
        shutil.copy2(backup_file, config_file)
        print(f"✅ 已从备份恢复配置: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ 恢复配置失败: {str(e)}")
        return False


def list_backup_files(config_file: str = "config.json") -> list:
    """列出所有备份文件"""
    backup_files = []
    base_name = os.path.basename(config_file)
    dir_name = os.path.dirname(config_file) or "."
    
    for file in os.listdir(dir_name):
        if file.startswith(f"{base_name}.backup_"):
            file_path = os.path.join(dir_name, file)
            stat = os.stat(file_path)
            backup_files.append({
                "file": file_path,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size": stat.st_size
            })
    
    # 按创建时间排序
    backup_files.sort(key=lambda x: x["created"], reverse=True)
    return backup_files


def interactive_migration():
    """交互式配置迁移"""
    print("=" * 50)
    print("AI小说生成器 - 配置迁移工具")
    print("=" * 50)
    
    # 检查当前配置
    config_file = "config.json"
    global_config = load_config(config_file)
    
    if "other_params" not in global_config:
        print("✅ 当前配置已经是新结构，无需迁移")
        return
    
    print("📋 检测到旧配置结构，需要进行迁移")
    print("\n迁移说明:")
    print("- 小说相关参数将迁移到独立的小说项目配置中")
    print("- 系统配置（API密钥、模型设置等）保持不变")
    print("- 原配置文件将自动备份")
    
    # 显示当前小说参数
    other_params = global_config.get("other_params", {})
    if other_params.get("topic"):
        print(f"\n当前小说主题: {other_params['topic'][:100]}...")
        print(f"小说类型: {other_params.get('genre', '未设置')}")
        print(f"章节数: {other_params.get('num_chapters', 0)}")
    
    # 确认迁移
    while True:
        choice = input("\n是否继续迁移? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            break
        elif choice in ['n', 'no', '否']:
            print("取消迁移")
            return
        else:
            print("请输入 y 或 n")
    
    # 执行迁移
    if migrate_config_to_novel_structure(config_file):
        print("\n🎉 迁移成功！")
        print("\n下一步:")
        print("1. 重新启动程序")
        print("2. 在界面中选择小说项目")
        print("3. 继续您的小说创作")
    else:
        print("\n❌ 迁移失败，请检查错误信息")


if __name__ == "__main__":
    interactive_migration()
