# ui/main_window.py
# -*- coding: utf-8 -*-
import os
import threading
import logging
import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from .role_library import RoleLibrary
from llm_adapters import create_llm_adapter

from config_manager import (
    load_config, save_config, test_llm_config, test_embedding_config,
    list_novel_projects, create_novel_project, load_novel_config, save_novel_config,
    get_current_novel_config, migrate_legacy_config
)
from utils import read_file, save_string_to_txt, clear_file_content
from tooltips import tooltips

from ui.context_menu import TextWidgetContextMenu
from ui.main_tab import build_main_tab, build_left_layout, build_right_layout
from ui.config_tab import build_config_tabview, load_config_btn, save_config_btn
from ui.novel_params_tab import build_novel_params_area, build_optional_buttons_area
from ui.generation_handlers import (
    generate_novel_architecture_ui,
    generate_chapter_blueprint_ui,
    generate_chapter_draft_ui,
    finalize_chapter_ui,
    do_consistency_check,
    import_knowledge_handler,
    clear_vectorstore_handler,
    show_plot_arcs_ui,
    generate_batch_ui
)
from ui.setting_tab import build_setting_tab, load_novel_architecture, save_novel_architecture
from ui.directory_tab import build_directory_tab, load_chapter_blueprint, save_chapter_blueprint
from ui.character_tab import build_character_tab, load_character_state, save_character_state
from ui.summary_tab import build_summary_tab, load_global_summary, save_global_summary
from ui.chapters_tab import build_chapters_tab, refresh_chapters_list, on_chapter_selected, load_chapter_content, save_current_chapter, prev_chapter, next_chapter
from ui.other_settings import build_other_settings_tab


class NovelGeneratorGUI:
    """
    小说生成器的主GUI类，包含所有的界面布局、事件处理、与后端逻辑的交互等。
    """
    def __init__(self, master):
        self.master = master
        self.master.title("AI小说生成器")
        try:
            if os.path.exists("icon.ico"):
                self.master.iconbitmap("icon.ico")
        except Exception:
            pass
        self.master.geometry("1350x840")

        # --------------- 配置文件路径 ---------------
        self.config_file = "config.json"
        self.loaded_config = load_config(self.config_file)
        
        # --------------- 小说项目管理 ---------------
        self.current_novel_project = None
        self.current_novel_config = None
        
        # 配置迁移将在UI创建后进行

        if self.loaded_config:
            last_llm = next(iter(self.loaded_config["llm_configs"].values())).get("interface_format", "OpenAI")

            last_embedding = self.loaded_config.get("last_embedding_interface_format", "OpenAI")
        else:
            last_llm = "OpenAI"
            last_embedding = "OpenAI"

        # if self.loaded_config and "llm_configs" in self.loaded_config and last_llm in self.loaded_config["llm_configs"]:
        #     llm_conf = next(iter(self.loaded_config["llm_configs"]))
        # else:
        #     llm_conf = {
        #         "api_key": "",
        #         "base_url": "https://api.openai.com/v1",
        #         "model_name": "gpt-4o-mini",
        #         "temperature": 0.7,
        #         "max_tokens": 8192,
        #         "timeout": 600
        #     }
        llm_conf = next(iter(self.loaded_config["llm_configs"].values()))
        choose_configs = self.loaded_config.get("choose_configs", {})


        if self.loaded_config and "embedding_configs" in self.loaded_config and last_embedding in self.loaded_config["embedding_configs"]:
            emb_conf = self.loaded_config["embedding_configs"][last_embedding]
        else:
            emb_conf = {
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model_name": "text-embedding-ada-002",
                "retrieval_k": 4
            }

        # PenBo 增加代理功能支持
        proxy_url = self.loaded_config["proxy_setting"]["proxy_url"]
        proxy_port = self.loaded_config["proxy_setting"]["proxy_port"]
        if self.loaded_config["proxy_setting"]["enabled"]:
            os.environ['HTTP_PROXY'] = f"http://{proxy_url}:{proxy_port}"
            os.environ['HTTPS_PROXY'] = f"http://{proxy_url}:{proxy_port}"
        else:
            os.environ.pop('HTTP_PROXY', None)  
            os.environ.pop('HTTPS_PROXY', None)



        # -- LLM通用参数 --
        # self.llm_conf_name = next(iter(self.loaded_config["llm_configs"]))
        self.api_key_var = ctk.StringVar(value=llm_conf.get("api_key", ""))
        self.base_url_var = ctk.StringVar(value=llm_conf.get("base_url", "https://api.openai.com/v1"))
        self.interface_format_var = ctk.StringVar(value=llm_conf.get("interface_format", "OpenAI"))
        self.model_name_var = ctk.StringVar(value=llm_conf.get("model_name", "gpt-4o-mini"))
        self.temperature_var = ctk.DoubleVar(value=llm_conf.get("temperature", 0.7))
        self.max_tokens_var = ctk.IntVar(value=llm_conf.get("max_tokens", 8192))
        self.timeout_var = ctk.IntVar(value=llm_conf.get("timeout", 600))
        self.interface_config_var = ctk.StringVar(value=next(iter(self.loaded_config["llm_configs"])))



        # -- Embedding相关 --
        self.embedding_interface_format_var = ctk.StringVar(value=last_embedding)
        self.embedding_api_key_var = ctk.StringVar(value=emb_conf.get("api_key", ""))
        self.embedding_url_var = ctk.StringVar(value=emb_conf.get("base_url", "https://api.openai.com/v1"))
        self.embedding_model_name_var = ctk.StringVar(value=emb_conf.get("model_name", "text-embedding-ada-002"))
        self.embedding_retrieval_k_var = ctk.StringVar(value=str(emb_conf.get("retrieval_k", 4)))


        # -- 生成配置相关 --
        self.architecture_llm_var = ctk.StringVar(value=choose_configs.get("architecture_llm", "DeepSeek"))
        self.chapter_outline_llm_var = ctk.StringVar(value=choose_configs.get("chapter_outline_llm", "DeepSeek"))
        self.final_chapter_llm_var = ctk.StringVar(value=choose_configs.get("final_chapter_llm", "DeepSeek"))
        self.consistency_review_llm_var = ctk.StringVar(value=choose_configs.get("consistency_review_llm", "DeepSeek"))
        self.prompt_draft_llm_var = ctk.StringVar(value=choose_configs.get("prompt_draft_llm", "DeepSeek"))





        # -- 小说参数相关 --
        if self.current_novel_config and "novel_params" in self.current_novel_config:
            op = self.current_novel_config["novel_params"]
            self.topic_default = op.get("topic", "")
            self.genre_var = ctk.StringVar(value=op.get("genre", "玄幻"))
            self.num_chapters_var = ctk.StringVar(value=str(op.get("num_chapters", 10)))
            self.word_number_var = ctk.StringVar(value=str(op.get("word_number", 3000)))
            self.filepath_var = ctk.StringVar(value=op.get("filepath", ""))
            self.chapter_num_var = ctk.StringVar(value=str(self.current_novel_config.get("generation_state", {}).get("current_chapter", 1)))
            self.characters_involved_var = ctk.StringVar(value=op.get("characters_involved", ""))
            self.key_items_var = ctk.StringVar(value=op.get("key_items", ""))
            self.scene_location_var = ctk.StringVar(value=op.get("scene_location", ""))
            self.time_constraint_var = ctk.StringVar(value=op.get("time_constraint", ""))
            self.writing_style_var = ctk.StringVar(value=op.get("writing_style", ""))
            self.user_guidance_default = op.get("user_guidance", "")
            
            # WebDAV相关变量
            self.webdav_url_var = ctk.StringVar(value="")
            self.webdav_username_var = ctk.StringVar(value="")
            self.webdav_password_var = ctk.StringVar(value="")
        else:
            # 使用默认值
            self.topic_default = ""
            self.genre_var = ctk.StringVar(value="玄幻")
            self.num_chapters_var = ctk.StringVar(value="10")
            self.word_number_var = ctk.StringVar(value="3000")
            self.filepath_var = ctk.StringVar(value="")
            self.chapter_num_var = ctk.StringVar(value="1")
            self.characters_involved_var = ctk.StringVar(value="")
            self.key_items_var = ctk.StringVar(value="")
            self.scene_location_var = ctk.StringVar(value="")
            self.time_constraint_var = ctk.StringVar(value="")
            self.writing_style_var = ctk.StringVar(value="")
            self.user_guidance_default = ""
            
            # WebDAV相关变量
            self.webdav_url_var = ctk.StringVar(value="")
            self.webdav_username_var = ctk.StringVar(value="")
            self.webdav_password_var = ctk.StringVar(value="")

        # --------------- 整体Tab布局 ---------------
        self.tabview = ctk.CTkTabview(self.master)
        self.tabview.pack(fill="both", expand=True)

        # 创建各个标签页
        build_main_tab(self)
        build_novel_params_area(self, start_row=1)
        build_optional_buttons_area(self, start_row=2)
        build_setting_tab(self)
        build_directory_tab(self)
        build_character_tab(self)
        build_summary_tab(self)
        build_chapters_tab(self)
        build_config_tabview(self)  # 移到章节管理之后，作为独立的"软件设置"标签页
        build_other_settings_tab(self)
        
        # UI创建完成后，先进行配置迁移，然后初始化小说项目
        if "other_params" in self.loaded_config:
            self.migrate_legacy_config()
        
        self.init_current_novel_project()


    # ----------------- 通用辅助函数 -----------------
    def show_tooltip(self, key: str):
        info_text = tooltips.get(key, "暂无说明")
        messagebox.showinfo("参数说明", info_text)

    def safe_get_int(self, var, default=1):
        try:
            val_str = str(var.get()).strip()
            return int(val_str)
        except:
            var.set(str(default))
            return default

    def log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def safe_log(self, message: str):
        self.master.after(0, lambda: self.log(message))

    def disable_button_safe(self, btn):
        self.master.after(0, lambda: btn.configure(state="disabled"))

    def enable_button_safe(self, btn):
        self.master.after(0, lambda: btn.configure(state="normal"))

    def handle_exception(self, context: str):
        full_message = f"{context}\n{traceback.format_exc()}"
        logging.error(full_message)
        self.safe_log(full_message)

    def show_chapter_in_textbox(self, text: str):
        self.chapter_result.delete("0.0", "end")
        self.chapter_result.insert("0.0", text)
        self.chapter_result.see("end")
    
    def test_llm_config(self):
        """
        测试当前的LLM配置是否可用
        """
        interface_format = self.interface_format_var.get().strip()
        api_key = self.api_key_var.get().strip()
        base_url = self.base_url_var.get().strip()
        model_name = self.model_name_var.get().strip()
        temperature = self.temperature_var.get()
        max_tokens = self.max_tokens_var.get()
        timeout = self.timeout_var.get()

        test_llm_config(
            interface_format=interface_format,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            log_func=self.safe_log,
            handle_exception_func=self.handle_exception
        )

    def test_embedding_config(self):
        """
        测试当前的Embedding配置是否可用
        """
        api_key = self.embedding_api_key_var.get().strip()
        base_url = self.embedding_url_var.get().strip()
        interface_format = self.embedding_interface_format_var.get().strip()
        model_name = self.embedding_model_name_var.get().strip()

        test_embedding_config(
            api_key=api_key,
            base_url=base_url,
            interface_format=interface_format,
            model_name=model_name,
            log_func=self.safe_log,
            handle_exception_func=self.handle_exception
        )
    
    def browse_folder(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.filepath_var.set(selected_dir)

    def show_character_import_window(self):
        """显示角色导入窗口"""
        import_window = ctk.CTkToplevel(self.master)
        import_window.title("导入角色信息")
        import_window.geometry("600x500")
        import_window.transient(self.master)  # 设置为父窗口的临时窗口
        import_window.grab_set()  # 保持窗口在顶层
        
        # 主容器
        main_frame = ctk.CTkFrame(import_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 滚动容器
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 获取角色库路径
        role_lib_path = os.path.join(self.filepath_var.get().strip(), "角色库")
        self.selected_roles = []  # 存储选中的角色名称
        
        # 动态加载角色分类
        if os.path.exists(role_lib_path):
            # 配置网格布局参数
            scroll_frame.columnconfigure(0, weight=1)
            max_roles_per_row = 4
            current_row = 0
            
            for category in os.listdir(role_lib_path):
                category_path = os.path.join(role_lib_path, category)
                if os.path.isdir(category_path):
                    # 创建分类容器
                    category_frame = ctk.CTkFrame(scroll_frame)
                    category_frame.grid(row=current_row, column=0, sticky="w", pady=(10,5), padx=5)
                    
                    # 添加分类标签
                    category_label = ctk.CTkLabel(category_frame, text=f"【{category}】", 
                                                font=("Microsoft YaHei", 12, "bold"))
                    category_label.grid(row=0, column=0, padx=(0,10), sticky="w")
                    
                    # 初始化角色排列参数
                    role_count = 0
                    row_num = 0
                    col_num = 1  # 从第1列开始（第0列是分类标签）
                    
                    # 添加角色复选框
                    for role_file in os.listdir(category_path):
                        if role_file.endswith(".txt"):
                            role_name = os.path.splitext(role_file)[0]
                            if not any(name == role_name for _, name in self.selected_roles):
                                chk = ctk.CTkCheckBox(category_frame, text=role_name)
                                chk.grid(row=row_num, column=col_num, padx=5, pady=2, sticky="w")
                                self.selected_roles.append((chk, role_name))
                                
                                # 更新行列位置
                                role_count += 1
                                col_num += 1
                                if col_num > max_roles_per_row:
                                    col_num = 1
                                    row_num += 1
                    
                    # 如果没有角色，调整分类标签占满整行
                    if role_count == 0:
                        category_label.grid(columnspan=max_roles_per_row+1, sticky="w")
                    
                    # 更新主布局的行号
                    current_row += 1
                    
                    # 添加分隔线
                    separator = ctk.CTkFrame(scroll_frame, height=1, fg_color="gray")
                    separator.grid(row=current_row, column=0, sticky="ew", pady=5)
                    current_row += 1
        
        # 底部按钮框架
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        # 选择按钮
        def confirm_selection():
            selected = [name for chk, name in self.selected_roles if chk.get() == 1]
            self.char_inv_text.delete("0.0", "end")
            self.char_inv_text.insert("0.0", ", ".join(selected))
            import_window.destroy()
            
        btn_confirm = ctk.CTkButton(btn_frame, text="选择", command=confirm_selection)
        btn_confirm.pack(side="left", padx=20)
        
        # 取消按钮
        btn_cancel = ctk.CTkButton(btn_frame, text="取消", command=import_window.destroy)
        btn_cancel.pack(side="right", padx=20)

    def show_role_library(self):
        save_path = self.filepath_var.get().strip()
        if not save_path:
            messagebox.showwarning("警告", "请先设置保存路径")
            return
        
        # 初始化LLM适配器
        llm_adapter = create_llm_adapter(
            interface_format=self.interface_format_var.get(),
            base_url=self.base_url_var.get(),
            model_name=self.model_name_var.get(),
            api_key=self.api_key_var.get(),
            temperature=self.temperature_var.get(),
            max_tokens=self.max_tokens_var.get(),
            timeout=self.timeout_var.get()
        )
        
        # 传递LLM适配器实例到角色库
        if hasattr(self, '_role_lib'):
            if self._role_lib.window and self._role_lib.window.winfo_exists():
                self._role_lib.window.destroy()
        
        self._role_lib = RoleLibrary(self.master, save_path, llm_adapter)  # 新增参数

    # ----------------- 将导入的各模块函数直接赋给类方法 -----------------
    generate_novel_architecture_ui = generate_novel_architecture_ui
    generate_chapter_blueprint_ui = generate_chapter_blueprint_ui
    generate_chapter_draft_ui = generate_chapter_draft_ui
    finalize_chapter_ui = finalize_chapter_ui
    do_consistency_check = do_consistency_check
    generate_batch_ui = generate_batch_ui
    import_knowledge_handler = import_knowledge_handler
    clear_vectorstore_handler = clear_vectorstore_handler
    show_plot_arcs_ui = show_plot_arcs_ui
    load_config_btn = load_config_btn
    save_config_btn = save_config_btn
    load_novel_architecture = load_novel_architecture
    save_novel_architecture = save_novel_architecture
    load_chapter_blueprint = load_chapter_blueprint
    save_chapter_blueprint = save_chapter_blueprint
    load_character_state = load_character_state
    save_character_state = save_character_state
    load_global_summary = load_global_summary
    save_global_summary = save_global_summary
    refresh_chapters_list = refresh_chapters_list
    on_chapter_selected = on_chapter_selected
    save_current_chapter = save_current_chapter
    prev_chapter = prev_chapter
    next_chapter = next_chapter
    test_llm_config = test_llm_config
    test_embedding_config = test_embedding_config
    browse_folder = browse_folder
    
    # =============== 小说项目管理方法 ===============
    
    def migrate_legacy_config(self):
        """迁移旧配置到新结构"""
        try:
            self.log("检测到旧配置结构，正在迁移...")
            self.loaded_config = migrate_legacy_config(self.loaded_config)
            save_config(self.loaded_config, self.config_file)
            self.log("✅ 配置迁移完成")
        except Exception as e:
            self.log(f"❌ 配置迁移失败: {str(e)}")
            self.handle_exception("配置迁移")
    
    def init_current_novel_project(self):
        """初始化当前小说项目"""
        try:
            projects = list_novel_projects()
            if projects:
                # 使用第一个项目（最新的）
                self.current_novel_project = projects[0]["path"]
                self.current_novel_config = load_novel_config(self.current_novel_project)
                self.log(f"✅ 已加载小说项目: {projects[0]['title']}")
            else:
                # 创建默认项目
                self.current_novel_project = create_novel_project("默认小说项目", self.loaded_config)
                self.current_novel_config = load_novel_config(self.current_novel_project)
                self.log("✅ 已创建默认小说项目")
        except Exception as e:
            self.log(f"❌ 初始化小说项目失败: {str(e)}")
            self.handle_exception("初始化小说项目")
    
    def show_novel_project_manager(self):
        """显示小说项目管理窗口"""
        manager_window = ctk.CTkToplevel(self.master)
        manager_window.title("小说项目管理")
        manager_window.geometry("600x500")
        manager_window.transient(self.master)
        manager_window.grab_set()
        
        # 主容器
        main_frame = ctk.CTkFrame(manager_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ctk.CTkLabel(main_frame, text="小说项目管理", 
                                  font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(10, 20))
        
        # 项目列表
        projects_frame = ctk.CTkFrame(main_frame)
        projects_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        projects_label = ctk.CTkLabel(projects_frame, text="现有项目:", 
                                     font=("Microsoft YaHei", 12, "bold"))
        projects_label.pack(pady=(10, 5))
        
        # 项目列表
        self.projects_listbox = tk.Listbox(projects_frame, height=8)
        self.projects_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 刷新项目列表
        self.refresh_projects_list()
        
        # 按钮框架
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        # 按钮
        btn_new = ctk.CTkButton(btn_frame, text="新建项目", command=self.create_new_project)
        btn_new.pack(side="left", padx=5)
        
        btn_switch = ctk.CTkButton(btn_frame, text="切换项目", command=self.switch_project)
        btn_switch.pack(side="left", padx=5)
        
        btn_delete = ctk.CTkButton(btn_frame, text="删除项目", command=self.delete_project)
        btn_delete.pack(side="left", padx=5)
        
        btn_refresh = ctk.CTkButton(btn_frame, text="刷新", command=self.refresh_projects_list)
        btn_refresh.pack(side="left", padx=5)
        
        btn_close = ctk.CTkButton(btn_frame, text="关闭", command=manager_window.destroy)
        btn_close.pack(side="right", padx=5)
    
    def refresh_projects_list(self):
        """刷新项目列表"""
        try:
            self.projects_listbox.delete(0, tk.END)
            projects = list_novel_projects()
            
            for project in projects:
                display_text = f"{project['title']} ({project['name']})"
                if project['path'] == self.current_novel_project:
                    display_text = f"★ {display_text}"
                self.projects_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            self.log(f"❌ 刷新项目列表失败: {str(e)}")
    
    def create_new_project(self):
        """创建新项目"""
        dialog = ctk.CTkInputDialog(text="请输入新项目名称:", title="新建小说项目")
        project_name = dialog.get_input()
        
        if project_name and project_name.strip():
            try:
                project_path = create_novel_project(project_name.strip(), self.loaded_config)
                self.log(f"✅ 已创建新项目: {project_name}")
                self.refresh_projects_list()
            except Exception as e:
                self.log(f"❌ 创建项目失败: {str(e)}")
                messagebox.showerror("错误", f"创建项目失败: {str(e)}")
    
    def switch_project(self):
        """切换项目"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            projects = list_novel_projects()
            if selection[0] < len(projects):
                selected_project = projects[selection[0]]
                
                # 保存当前项目配置
                self.save_current_novel_config()
                
                # 切换到新项目
                self.current_novel_project = selected_project["path"]
                self.current_novel_config = load_novel_config(self.current_novel_project)
                
                # 更新UI
                self.update_ui_from_novel_config()
                
                self.log(f"✅ 已切换到项目: {selected_project['title']}")
                self.refresh_projects_list()
                
        except Exception as e:
            self.log(f"❌ 切换项目失败: {str(e)}")
            messagebox.showerror("错误", f"切换项目失败: {str(e)}")
    
    def delete_project(self):
        """删除项目"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            projects = list_novel_projects()
            if selection[0] < len(projects):
                selected_project = projects[selection[0]]
                
                # 确认删除
                if messagebox.askyesno("确认删除", 
                                     f"确定要删除项目 '{selected_project['title']}' 吗？\n"
                                     f"此操作将删除所有相关文件，无法恢复！"):
                    
                    # 如果删除的是当前项目，需要切换到其他项目
                    if selected_project["path"] == self.current_novel_project:
                        remaining_projects = [p for p in projects if p["path"] != selected_project["path"]]
                        if remaining_projects:
                            self.current_novel_project = remaining_projects[0]["path"]
                            self.current_novel_config = load_novel_config(self.current_novel_project)
                            self.update_ui_from_novel_config()
                        else:
                            self.current_novel_project = None
                            self.current_novel_config = None
                    
                    # 删除项目
                    from config_manager import delete_novel_project
                    if delete_novel_project(selected_project["name"]):
                        self.log(f"✅ 已删除项目: {selected_project['title']}")
                        self.refresh_projects_list()
                    else:
                        self.log(f"❌ 删除项目失败")
                        
        except Exception as e:
            self.log(f"❌ 删除项目失败: {str(e)}")
            messagebox.showerror("错误", f"删除项目失败: {str(e)}")
    
    def save_current_novel_config(self):
        """保存当前小说配置"""
        if not self.current_novel_config or not self.current_novel_project:
            messagebox.showwarning("警告", "当前没有加载任何小说项目")
            return
        
        try:
            # 从UI读取可编辑控件的值
            # 主题与内容指导来自文本框
            try:
                topic_text = self.topic_text.get("0.0", "end").strip()
            except Exception:
                topic_text = self.topic_default
            try:
                user_guidance_text = self.user_guide_text.get("0.0", "end").strip()
            except Exception:
                user_guidance_text = self.user_guidance_default
            # 核心人物来自多行文本
            try:
                characters_involved_text = self.char_inv_text.get("0.0", "end").strip()
            except Exception:
                characters_involved_text = self.characters_involved_var.get()

            # 更新小说参数
            self.current_novel_config["novel_params"].update({
                "topic": topic_text,
                "genre": self.genre_var.get(),
                "num_chapters": int(self.num_chapters_var.get() or 0),
                "word_number": int(self.word_number_var.get() or 0),
                "filepath": self.filepath_var.get(),
                "writing_style": self.writing_style_var.get(),
                "user_guidance": user_guidance_text,
                "characters_involved": characters_involved_text,
                "key_items": self.key_items_var.get(),
                "scene_location": self.scene_location_var.get(),
                "time_constraint": self.time_constraint_var.get()
            })
            
            # 同步内存中的默认文本变量（用于后续界面显示）
            self.topic_default = topic_text
            self.user_guidance_default = user_guidance_text
            self.characters_involved_var.set(characters_involved_text)
            
            # 更新生成状态
            self.current_novel_config["generation_state"]["current_chapter"] = int(self.chapter_num_var.get() or 1)
            
            # 保存配置
            if save_novel_config(self.current_novel_project, self.current_novel_config):
                self.log("✅ 项目配置已保存")
            else:
                self.log("❌ 项目配置保存失败")
            
        except Exception as e:
            self.log(f"❌ 保存小说配置失败: {str(e)}")
    
    def update_ui_from_novel_config(self):
        """从小说配置更新UI"""
        if not self.current_novel_config:
            return
        
        try:
            # 先清空所有控件
            self.clear_ui_controls()
            
            op = self.current_novel_config.get("novel_params", {})
            
            # 更新变量
            self.topic_default = op.get("topic", "")
            self.genre_var.set(op.get("genre", "玄幻"))
            self.num_chapters_var.set(str(op.get("num_chapters", 10)))
            self.word_number_var.set(str(op.get("word_number", 3000)))
            self.filepath_var.set(op.get("filepath", ""))
            self.chapter_num_var.set(str(self.current_novel_config.get("generation_state", {}).get("current_chapter", 1)))
            self.characters_involved_var.set(op.get("characters_involved", ""))
            self.key_items_var.set(op.get("key_items", ""))
            self.scene_location_var.set(op.get("scene_location", ""))
            self.time_constraint_var.set(op.get("time_constraint", ""))
            self.writing_style_var.set(op.get("writing_style", ""))
            self.user_guidance_default = op.get("user_guidance", "")
            
            # 更新文本框控件
            self.update_text_widgets()
            
            # 更新窗口标题
            project_title = self.current_novel_config.get("novel_info", {}).get("title", "未知项目")
            self.master.title(f"AI小说生成器 - {project_title}")
            
        except Exception as e:
            self.log(f"❌ 更新UI失败: {str(e)}")
    
    def clear_ui_controls(self):
        """清空所有UI控件"""
        try:
            # 清空StringVar变量
            self.genre_var.set("")
            self.num_chapters_var.set("")
            self.word_number_var.set("")
            self.filepath_var.set("")
            self.chapter_num_var.set("")
            self.characters_involved_var.set("")
            self.key_items_var.set("")
            self.scene_location_var.set("")
            self.time_constraint_var.set("")
            self.writing_style_var.set("")
            
            # 清空文本框（如果存在）
            if hasattr(self, 'topic_text'):
                self.topic_text.delete("0.0", "end")
            if hasattr(self, 'user_guide_text'):
                self.user_guide_text.delete("0.0", "end")
            if hasattr(self, 'char_inv_text'):
                self.char_inv_text.delete("0.0", "end")
            if hasattr(self, 'novel_architecture_text'):
                self.novel_architecture_text.delete("0.0", "end")
            if hasattr(self, 'chapter_blueprint_text'):
                self.chapter_blueprint_text.delete("0.0", "end")
            if hasattr(self, 'character_state_text'):
                self.character_state_text.delete("0.0", "end")
            if hasattr(self, 'global_summary_text'):
                self.global_summary_text.delete("0.0", "end")
            if hasattr(self, 'chapter_result'):
                self.chapter_result.delete("0.0", "end")
            
            # 清空章节列表
            if hasattr(self, 'chapters_listbox'):
                self.chapters_listbox.delete(0, "end")
                
        except Exception as e:
            self.log(f"❌ 清空UI控件失败: {str(e)}")
    
    def update_text_widgets(self):
        """更新文本框控件内容"""
        try:
            # 更新主题文本框
            if hasattr(self, 'topic_text'):
                self.topic_text.insert("0.0", self.topic_default)
            
            # 更新用户指导文本框
            if hasattr(self, 'user_guide_text'):
                self.user_guide_text.insert("0.0", self.user_guidance_default)
            
            # 更新核心人物文本框
            if hasattr(self, 'char_inv_text'):
                self.char_inv_text.insert("0.0", self.characters_involved_var.get())
            
            # 刷新章节列表
            if hasattr(self, 'refresh_chapters_list'):
                self.refresh_chapters_list()
                
        except Exception as e:
            self.log(f"❌ 更新文本控件失败: {str(e)}")
