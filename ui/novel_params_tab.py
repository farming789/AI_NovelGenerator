# ui/novel_params_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.context_menu import TextWidgetContextMenu
from tooltips import tooltips

def build_novel_params_area(self, start_row=1):
    self.params_frame = ctk.CTkScrollableFrame(self.right_frame, orientation="vertical")
    self.params_frame.grid(row=start_row, column=0, sticky="nsew", padx=5, pady=5)
    self.params_frame.columnconfigure(1, weight=1)

    # 1) 主题(Topic)
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="主题(Topic):", tooltip_key="topic", row=0, column=0, font=("Microsoft YaHei", 12), sticky="ne")
    self.topic_text = ctk.CTkTextbox(self.params_frame, height=80, wrap="word", font=("Microsoft YaHei", 12))
    TextWidgetContextMenu(self.topic_text)
    self.topic_text.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    if hasattr(self, 'topic_default') and self.topic_default:
        self.topic_text.insert("0.0", self.topic_default)

    # 2) 类型(Genre)
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="类型(Genre):", tooltip_key="genre", row=1, column=0, font=("Microsoft YaHei", 12))
    genre_entry = ctk.CTkEntry(self.params_frame, textvariable=self.genre_var, font=("Microsoft YaHei", 12))
    genre_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # 3) 章节数 & 每章字数
    row_for_chapter_and_word = 2
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="章节数 & 每章字数:", tooltip_key="num_chapters", row=row_for_chapter_and_word, column=0, font=("Microsoft YaHei", 12))
    chapter_word_frame = ctk.CTkFrame(self.params_frame)
    chapter_word_frame.grid(row=row_for_chapter_and_word, column=1, padx=5, pady=5, sticky="ew")
    chapter_word_frame.columnconfigure((0, 1, 2, 3), weight=0)
    num_chapters_label = ctk.CTkLabel(chapter_word_frame, text="章节数:", font=("Microsoft YaHei", 12))
    num_chapters_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    num_chapters_entry = ctk.CTkEntry(chapter_word_frame, textvariable=self.num_chapters_var, width=60, font=("Microsoft YaHei", 12))
    num_chapters_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    word_number_label = ctk.CTkLabel(chapter_word_frame, text="每章字数:", font=("Microsoft YaHei", 12))
    word_number_label.grid(row=0, column=2, padx=(15, 5), pady=5, sticky="e")
    word_number_entry = ctk.CTkEntry(chapter_word_frame, textvariable=self.word_number_var, width=60, font=("Microsoft YaHei", 12))
    word_number_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    # 4) 保存路径
    row_fp = 3
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="保存路径:", tooltip_key="filepath", row=row_fp, column=0, font=("Microsoft YaHei", 12))
    self.filepath_frame = ctk.CTkFrame(self.params_frame)
    self.filepath_frame.grid(row=row_fp, column=1, padx=5, pady=5, sticky="nsew")
    self.filepath_frame.columnconfigure(0, weight=1)
    filepath_entry = ctk.CTkEntry(self.filepath_frame, textvariable=self.filepath_var, font=("Microsoft YaHei", 12))
    filepath_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    browse_btn = ctk.CTkButton(self.filepath_frame, text="浏览...", command=self.browse_folder, width=60, font=("Microsoft YaHei", 12))
    browse_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    # 5) 章节号
    row_chap_num = 4
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="章节号:", tooltip_key="chapter_num", row=row_chap_num, column=0, font=("Microsoft YaHei", 12))
    chapter_num_entry = ctk.CTkEntry(self.params_frame, textvariable=self.chapter_num_var, width=80, font=("Microsoft YaHei", 12))
    chapter_num_entry.grid(row=row_chap_num, column=1, padx=5, pady=5, sticky="w")

    # 6) 内容指导
    row_user_guide = 5
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="内容指导:", tooltip_key="user_guidance", row=row_user_guide, column=0, font=("Microsoft YaHei", 12), sticky="ne")
    self.user_guide_text = ctk.CTkTextbox(self.params_frame, height=80, wrap="word", font=("Microsoft YaHei", 12))
    TextWidgetContextMenu(self.user_guide_text)
    self.user_guide_text.grid(row=row_user_guide, column=1, padx=5, pady=5, sticky="nsew")
    if hasattr(self, 'user_guidance_default') and self.user_guidance_default:
        self.user_guide_text.insert("0.0", self.user_guidance_default)

    # 7) 写作风格
    row_writing_style = 6
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="写作风格:", tooltip_key="writing_style", row=row_writing_style, column=0, font=("Microsoft YaHei", 12))
    writing_style_entry = ctk.CTkEntry(self.params_frame, textvariable=self.writing_style_var, font=("Microsoft YaHei", 12))
    writing_style_entry.grid(row=row_writing_style, column=1, padx=5, pady=5, sticky="ew")

    # 8) 可选元素：核心人物/关键道具/空间坐标/时间压力
    row_idx = 7
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="核心人物:", tooltip_key="characters_involved", row=row_idx, column=0, font=("Microsoft YaHei", 12))
    
    # 核心人物输入框+按钮容器
    char_inv_frame = ctk.CTkFrame(self.params_frame)
    char_inv_frame.grid(row=row_idx, column=1, padx=5, pady=5, sticky="nsew")
    char_inv_frame.columnconfigure(0, weight=1)
    char_inv_frame.rowconfigure(0, weight=1)
    
    # 三行文本输入框
    self.char_inv_text = ctk.CTkTextbox(char_inv_frame, height=60, wrap="word", font=("Microsoft YaHei", 12))
    self.char_inv_text.grid(row=0, column=0, padx=(0,5), pady=5, sticky="nsew")
    if hasattr(self, 'characters_involved_var'):
        self.char_inv_text.insert("0.0", self.characters_involved_var.get())
    
    # 导入按钮
    import_btn = ctk.CTkButton(char_inv_frame, text="导入", width=60, 
                             command=self.show_character_import_window,
                             font=("Microsoft YaHei", 12))
    import_btn.grid(row=0, column=1, padx=(0,5), pady=5, sticky="e")
    row_idx += 1
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="关键道具:", tooltip_key="key_items", row=row_idx, column=0, font=("Microsoft YaHei", 12))
    key_items_entry = ctk.CTkEntry(self.params_frame, textvariable=self.key_items_var, font=("Microsoft YaHei", 12))
    key_items_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
    row_idx += 1
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="空间坐标:", tooltip_key="scene_location", row=row_idx, column=0, font=("Microsoft YaHei", 12))
    scene_loc_entry = ctk.CTkEntry(self.params_frame, textvariable=self.scene_location_var, font=("Microsoft YaHei", 12))
    scene_loc_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
    row_idx += 1
    create_label_with_help_for_novel_params(self, parent=self.params_frame, label_text="时间压力:", tooltip_key="time_constraint", row=row_idx, column=0, font=("Microsoft YaHei", 12))
    time_const_entry = ctk.CTkEntry(self.params_frame, textvariable=self.time_constraint_var, font=("Microsoft YaHei", 12))
    time_const_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")

    # 9) 额外设置（多样化开关）
    row_idx += 1
    extra_frame = ctk.CTkFrame(self.params_frame)
    extra_frame.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=(10,5), sticky="nsew")
    extra_frame.columnconfigure(1, weight=1)
    title = ctk.CTkLabel(extra_frame, text="额外设置（可选，增强多样性）", font=("Microsoft YaHei", 12, "bold"))
    title.grid(row=0, column=0, columnspan=2, padx=5, pady=(6,2), sticky="w")

    # 叙事范式
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="叙事范式:", tooltip_key="narrative_paradigm", row=1, column=0, font=("Microsoft YaHei", 12))
    entry_np = ctk.CTkEntry(extra_frame, textvariable=self.narrative_paradigm_var, font=("Microsoft YaHei", 12))
    entry_np.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # 题材杂交
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="题材杂交:", tooltip_key="hybrid_genre", row=2, column=0, font=("Microsoft YaHei", 12))
    entry_hg = ctk.CTkEntry(extra_frame, textvariable=self.hybrid_genre_var, font=("Microsoft YaHei", 12))
    entry_hg.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # 风格剖面
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="风格剖面:", tooltip_key="style_profile", row=3, column=0, font=("Microsoft YaHei", 12))
    entry_sp = ctk.CTkEntry(extra_frame, textvariable=self.style_profile_var, font=("Microsoft YaHei", 12))
    entry_sp.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    # 视角矩阵
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="视角矩阵:", tooltip_key="perspective_matrix", row=4, column=0, font=("Microsoft YaHei", 12))
    entry_pm = ctk.CTkEntry(extra_frame, textvariable=self.perspective_matrix_var, font=("Microsoft YaHei", 12))
    entry_pm.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    # 场景目标
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="场景目标:", tooltip_key="scene_objectives", row=5, column=0, font=("Microsoft YaHei", 12))
    entry_so = ctk.CTkEntry(extra_frame, textvariable=self.scene_objectives_var, font=("Microsoft YaHei", 12))
    entry_so.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    # 母题预算
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="母题预算:", tooltip_key="motif_budget", row=6, column=0, font=("Microsoft YaHei", 12))
    entry_mb = ctk.CTkEntry(extra_frame, textvariable=self.motif_budget_var, font=("Microsoft YaHei", 12))
    entry_mb.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    # 知识注入比例
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="知识注入比例:", tooltip_key="knowledge_injection_policy", row=7, column=0, font=("Microsoft YaHei", 12))
    entry_kp = ctk.CTkEntry(extra_frame, textvariable=self.knowledge_injection_policy_var, font=("Microsoft YaHei", 12))
    entry_kp.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

    # seed
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="随机种子(seed):", tooltip_key="seed", row=8, column=0, font=("Microsoft YaHei", 12))
    entry_seed = ctk.CTkEntry(extra_frame, textvariable=self.seed_var, font=("Microsoft YaHei", 12))
    entry_seed.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

    # 变体因子
    create_label_with_help_for_novel_params(self, parent=extra_frame, label_text="变体因子:", tooltip_key="variation_factor", row=9, column=0, font=("Microsoft YaHei", 12))
    entry_vf = ctk.CTkEntry(extra_frame, textvariable=self.variation_factor_var, font=("Microsoft YaHei", 12))
    entry_vf.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

def build_optional_buttons_area(self, start_row=2):
    self.optional_btn_frame = ctk.CTkFrame(self.right_frame)
    self.optional_btn_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
    self.optional_btn_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

    self.btn_check_consistency = ctk.CTkButton(
        self.optional_btn_frame, text="一致性审校", command=self.do_consistency_check, 
        font=("Microsoft YaHei", 12), width=100  # 固定宽度
    )
    self.btn_check_consistency.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    self.btn_import_knowledge = ctk.CTkButton(
        self.optional_btn_frame, text="导入知识库", command=self.import_knowledge_handler,
        font=("Microsoft YaHei", 12), width=100
    )
    self.btn_import_knowledge.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    self.btn_clear_vectorstore = ctk.CTkButton(
        self.optional_btn_frame, text="清空向量库", fg_color="red", 
        command=self.clear_vectorstore_handler, font=("Microsoft YaHei", 12), width=100
    )
    self.btn_clear_vectorstore.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    self.plot_arcs_btn = ctk.CTkButton(
        self.optional_btn_frame, text="查看剧情要点", command=self.show_plot_arcs_ui,
        font=("Microsoft YaHei", 12), width=100
    )
    self.plot_arcs_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # 新增角色库按钮
    self.role_library_btn = ctk.CTkButton(
        self.optional_btn_frame, text="角色库", command=self.show_role_library,
        font=("Microsoft YaHei", 12), width=100
    )
    self.role_library_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

def create_label_with_help_for_novel_params(self, parent, label_text, tooltip_key, row, column, font=None, sticky="e", padx=5, pady=5):
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    frame.columnconfigure(0, weight=0)
    label = ctk.CTkLabel(frame, text=label_text, font=font)
    label.pack(side="left")
    btn = ctk.CTkButton(frame, text="?", width=22, height=22, font=("Microsoft YaHei", 10),
                        command=lambda: messagebox.showinfo("参数说明", tooltips.get(tooltip_key, "暂无说明")))
    btn.pack(side="left", padx=3)
    return frame
