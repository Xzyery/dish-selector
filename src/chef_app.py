import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import uuid
import json
from dishes import Dish
from utils import load_dishes, save_dishes

class ChefApp:
    def __init__(self, root):
        self.root = root
        self.root.title("厨师管理端")
        self.root.configure(bg="#f7f6f2")
        self.root.geometry("1200x700")
        
        # 确保窗口完全初始化
        self.root.update_idletasks()
        
        # 初始化变量
        self.photo_references = {}
        self.selected_index = None
        self.current_preview_photo = None
        
        # 设置路径
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(self.project_root, "images")
        self.data_file = os.path.join(self.project_root, "dishes.json")
        
        print(f"项目根目录: {self.project_root}")
        print(f"图片目录: {self.images_dir}")
        print(f"数据文件: {self.data_file}")
        
        # 确保目录存在
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            print(f"创建图片目录: {self.images_dir}")
        
        # 初始化数据文件
        self.init_data_file()
        
        # 加载菜品数据
        self.dishes = load_dishes(self.data_file)
        print(f"加载了 {len(self.dishes)} 个菜品")
        
        # 设置UI
        self.setup_ui()
        
        # 刷新列表
        self.refresh_list()
    
    def init_data_file(self):
        """初始化数据文件"""
        if not os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                print(f"创建数据文件: {self.data_file}")
            except Exception as e:
                print(f"创建数据文件失败: {e}")
        
    def setup_ui(self):
        # 标题
        title = tk.Label(self.root, text="👨‍🍳 厨师管理端", 
                        font=("微软雅黑", 20, "bold"),
                        bg="#f7f6f2", fg="#2c3e50")
        title.pack(pady=20)
        
        # 主框架
        main_frame = tk.Frame(self.root, bg="#f7f6f2")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # 左侧菜品列表
        left_frame = tk.Frame(main_frame, bg="#f7f6f2")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        list_title = tk.Label(left_frame, text="📋 菜品列表", 
                             font=("微软雅黑", 16, "bold"),
                             bg="#f7f6f2", fg="#2c3e50")
        list_title.pack(pady=(0, 15))
        
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, 
                                 font=("微软雅黑", 12),
                                 bg="#ffffff", fg="#2c3e50",
                                 selectbackground="#3498db",
                                 selectforeground="white",
                                 bd=0, highlightthickness=1,
                                 highlightcolor="#3498db",
                                 yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # 右侧预览
        right_frame = tk.Frame(main_frame, bg="#f7f6f2")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15)
        
        preview_title = tk.Label(right_frame, text="🖼️ 菜品预览", 
                               font=("微软雅黑", 16, "bold"),
                               bg="#f7f6f2", fg="#2c3e50")
        preview_title.pack(pady=(0, 15))
        
        self.preview_label = tk.Label(right_frame, 
                                    bg="#ffffff",
                                    text="点击左侧菜品查看预览图片",
                                    font=("微软雅黑", 12),
                                    fg="#7f8c8d",
                                    relief=tk.RIDGE, bd=2)
        self.preview_label.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.setup_buttons()
        
    def setup_buttons(self):
        btn_frame = tk.Frame(self.root, bg="#f7f6f2")
        btn_frame.pack(side=tk.BOTTOM, pady=30)
        
        btn_config = {
            "font": ("微软雅黑", 12, "bold"),
            "width": 15,
            "height": 2,
            "bd": 0,
            "relief": tk.FLAT,
            "cursor": "hand2"
        }
        
        add_btn = tk.Button(btn_frame, text="➕ 添加菜品", 
                           command=self.open_add_dish_window,
                           bg="#27ae60", fg="white",
                           activebackground="#2ecc71",
                           **btn_config)
        add_btn.pack(side=tk.LEFT, padx=15)
        
        delete_btn = tk.Button(btn_frame, text="🗑️ 删除菜品",
                              command=self.delete_dish,
                              bg="#e74c3c", fg="white",
                              activebackground="#c0392b",
                              **btn_config)
        delete_btn.pack(side=tk.LEFT, padx=15)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 刷新列表",
                               command=self.refresh_list,
                               bg="#3498db", fg="white",
                               activebackground="#2980b9",
                               **btn_config)
        refresh_btn.pack(side=tk.LEFT, padx=15)
        
    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            dish = self.dishes[self.selected_index]
            self.show_preview(dish.image_path)
            
    def show_preview(self, image_path):
        try:
            # 处理路径
            if os.path.isabs(image_path):
                full_path = image_path
            else:
                if image_path.startswith("images"):
                    full_path = os.path.join(self.project_root, image_path)
                else:
                    full_path = os.path.join(self.images_dir, image_path)
            
            print(f"尝试加载图片: {full_path}")
            
            if not os.path.exists(full_path):
                self.preview_label.config(image="", text=f"图片文件不存在:\n{image_path}")
                self.current_preview_photo = None
                return
                
            img = Image.open(full_path)
            img = img.convert('RGB')
            img.thumbnail((500, 400), Image.Resampling.LANCZOS)
            
            # 确保在主线程中创建PhotoImage
            self.root.after_idle(lambda: self._update_preview_image(img))
            
        except Exception as e:
            print(f"预览图片错误: {e}")
            self.preview_label.config(image="", text=f"无法加载图片:\n{str(e)}")
            self.current_preview_photo = None
    
    def _update_preview_image(self, img):
        """在主线程中更新预览图片"""
        try:
            photo = ImageTk.PhotoImage(img)
            self.current_preview_photo = photo
            self.preview_label.config(image=photo, text="")
        except Exception as e:
            print(f"更新预览图片失败: {e}")
            self.preview_label.config(image="", text=f"显示图片失败:\n{str(e)}")
            
    def open_add_dish_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("添加新菜品")
        add_window.geometry("700x800")  # 适中的窗口大小
        add_window.configure(bg="#f7f6f2")
        add_window.grab_set()
        add_window.resizable(False, False)
        add_window.transient(self.root)
        
        # 确保窗口完全初始化
        add_window.update_idletasks()
        
        # 窗口变量
        selected_image_path = tk.StringVar()
        preview_photo_ref = [None]
        
        # 标题
        title = tk.Label(add_window, text="🍽️ 添加新菜品", 
                        font=("微软雅黑", 18, "bold"),
                        bg="#f7f6f2", fg="#2c3e50")
        title.pack(pady=20)
        
        # 菜品名称
        name_frame = tk.Frame(add_window, bg="#f7f6f2")
        name_frame.pack(pady=15, padx=40, fill=tk.X)
        
        tk.Label(name_frame, text="菜品名称:", 
                font=("微软雅黑", 14, "bold"),
                bg="#f7f6f2", fg="#2c3e50").pack(anchor='w')
                
        name_entry = tk.Entry(name_frame, 
                            font=("微软雅黑", 13),
                            width=50, bd=2, relief=tk.GROOVE)
        name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 图片预览区域
        preview_frame = tk.Frame(add_window, bg="#f7f6f2")
        preview_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(preview_frame, text="图片预览:", 
                font=("微软雅黑", 14, "bold"),
                bg="#f7f6f2", fg="#2c3e50").pack()
                
        # 调整预览标签大小 - 适中的尺寸，既能看清楚又不会太大
        preview_img_label = tk.Label(preview_frame, 
                                   bg="#ffffff",
                                   text="尚未选择图片\n\n点击下方按钮选择图片文件\n\n预览图片将在此处显示",
                                   font=("微软雅黑", 11),
                                   fg="#7f8c8d",
                                   width=65,   # 适中的宽度
                                   height=20,  # 适中的高度
                                   relief=tk.RIDGE, bd=2)
        preview_img_label.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 文件信息显示
        info_label = tk.Label(add_window, text="未选择文件", 
                             font=("微软雅黑", 10),
                             bg="#f7f6f2", fg="#7f8c8d")
        info_label.pack(pady=5)
        
        def select_image_file():
            print("=" * 50)
            print("开始选择图片文件...")
            
            file_path = filedialog.askopenfilename(
                title="选择菜品图片",
                initialdir=os.path.expanduser("~/Desktop"),
                filetypes=[
                    ("常用图片", "*.jpg *.jpeg *.png *.bmp"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("PNG", "*.png"),
                    ("BMP", "*.bmp"),
                    ("所有文件", "*.*")
                ]
            )
            
            print(f"选择的文件: {file_path}")
            
            if not file_path:
                print("用户取消选择")
                return
            
            try:
                # 详细的文件检查
                print(f"检查文件: {file_path}")
                print(f"文件存在: {os.path.exists(file_path)}")
                print(f"文件大小: {os.path.getsize(file_path)} bytes")
                print(f"可读权限: {os.access(file_path, os.R_OK)}")
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError("选择的文件不存在")
                
                if os.path.getsize(file_path) == 0:
                    raise ValueError("选择的文件为空")
                
                # 测试图片
                print("验证图片格式...")
                test_img = Image.open(file_path)
                print(f"图片格式: {test_img.format}")
                print(f"图片模式: {test_img.mode}")
                print(f"图片尺寸: {test_img.size}")
                test_img.verify()
                print("图片格式验证通过")
                
                # 生成文件名
                original_name = os.path.basename(file_path)
                file_ext = os.path.splitext(original_name)[1].lower()
                if not file_ext:
                    file_ext = '.jpg'
                
                # 使用时间戳 + 随机数生成文件名
                import time
                timestamp = int(time.time())
                random_str = str(uuid.uuid4())[:8]
                new_filename = f"dish_{timestamp}_{random_str}{file_ext}"
                
                target_path = os.path.join(self.images_dir, new_filename)
                relative_path = f"images/{new_filename}"
                
                print(f"目标路径: {target_path}")
                print(f"相对路径: {relative_path}")
                
                # 重新打开并处理图片
                img = Image.open(file_path)
                
                # 处理透明背景
                if img.mode in ('RGBA', 'LA', 'P'):
                    print(f"转换图片模式从 {img.mode} 到 RGB")
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保存图片
                print("保存图片...")
                img.save(target_path, 'JPEG', quality=95)
                print(f"图片保存成功: {target_path}")
                
                # 创建预览 - 适中的预览图片尺寸
                def create_preview():
                    try:
                        print("创建预览...")
                        img_preview = img.copy()
                        # 设置适中的预览尺寸 - 既能看清楚内容又不会太大
                        img_preview.thumbnail((480, 360), Image.Resampling.LANCZOS)
                        
                        # 确保在正确的窗口上下文中创建PhotoImage
                        photo = ImageTk.PhotoImage(img_preview, master=add_window)
                        preview_photo_ref[0] = photo
                        
                        # 更新界面
                        preview_img_label.config(image=photo, text="")
                        info_label.config(text=f"已选择: {original_name}\n保存为: {new_filename}")
                        selected_image_path.set(relative_path)
                        
                        print("图片处理完成!")
                        messagebox.showinfo("成功", f"图片选择成功!\n原文件: {original_name}\n保存为: {new_filename}")
                    except Exception as e:
                        print(f"创建预览失败: {e}")
                        messagebox.showerror("错误", f"创建预览失败: {e}")
                
                # 使用after方法在下一个UI循环中创建预览
                add_window.after(100, create_preview)
                
            except Exception as e:
                error_msg = f"处理图片失败: {str(e)}"
                print(f"错误: {error_msg}")
                print(f"错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("错误", error_msg)
        
        # 按钮
        tk.Button(add_window, text="📁 选择图片文件",
                 command=select_image_file,
                 bg="#3498db", fg="white",
                 font=("微软雅黑", 13, "bold"),
                 width=20, height=2,
                 bd=0, relief=tk.FLAT,
                 cursor="hand2").pack(pady=15)
        
        def save_dish():
            dish_name = name_entry.get().strip()
            image_path = selected_image_path.get()
            
            print(f"保存菜品: 名称='{dish_name}', 图片='{image_path}'")
            
            if not dish_name:
                messagebox.showwarning("错误", "请输入菜品名称!")
                return
                
            if not image_path:
                messagebox.showwarning("错误", "请选择菜品图片!")
                return
            
            try:
                # 验证图片文件存在
                full_image_path = os.path.join(self.project_root, image_path)
                if not os.path.exists(full_image_path):
                    raise FileNotFoundError(f"图片文件不存在: {full_image_path}")
                
                new_dish = Dish(dish_name, image_path)
                self.dishes.append(new_dish)
                save_dishes(self.dishes, self.data_file)
                
                self.refresh_list()
                
                # 选中新菜品
                new_index = len(self.dishes) - 1
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(new_index)
                self.listbox.see(new_index)
                self.show_preview(image_path)
                
                add_window.destroy()
                messagebox.showinfo("成功", f"菜品 '{dish_name}' 添加成功!")
                
            except Exception as e:
                error_msg = f"保存失败: {str(e)}"
                print(error_msg)
                messagebox.showerror("错误", error_msg)
        
        # 底部按钮
        btn_frame = tk.Frame(add_window, bg="#f7f6f2")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 保存菜品", command=save_dish,
                 bg="#27ae60", fg="white", font=("微软雅黑", 13, "bold"),
                 width=15, height=2, bd=0, relief=tk.FLAT,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ 取消", command=add_window.destroy,
                 bg="#95a5a6", fg="white", font=("微软雅黑", 13),
                 width=15, height=2, bd=0, relief=tk.FLAT,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        name_entry.focus()
        
    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for i, dish in enumerate(self.dishes):
            self.listbox.insert(tk.END, f"{i+1}. {dish.name}")
        print(f"列表已刷新，当前共有 {len(self.dishes)} 个菜品")
        
    def delete_dish(self):
        if self.selected_index is not None and self.selected_index < len(self.dishes):
            dish = self.dishes[self.selected_index]
            
            if messagebox.askyesno("确认删除", f"确定要删除菜品 '{dish.name}' 吗？"):
                try:
                    self.dishes.pop(self.selected_index)
                    save_dishes(self.dishes, self.data_file)
                    
                    self.preview_label.config(image="", text="点击左侧菜品查看预览图片")
                    self.current_preview_photo = None
                    self.refresh_list()
                    self.selected_index = None
                    
                    messagebox.showinfo("成功", f"菜品 '{dish.name}' 已删除")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {str(e)}")
        else:
            messagebox.showinfo("提示", "请先选择要删除的菜品!")