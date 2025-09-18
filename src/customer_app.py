import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import random
from dishes import Dish
from utils import load_dishes

class CustomerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("顾客端")
        self.root.configure(bg="#f7f6f2")
        self.root.geometry("1400x800")  # 增加窗口大小
        
        # 确保窗口完全初始化
        self.root.update_idletasks()
        
        # 初始化变量
        self.current_preview_photo = None
        self.selected_index = None
        self.selected_dishes = []
        self.cart_selected_index = None
        
        # 设置路径
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_file = os.path.join(self.project_root, "dishes.json")
        
        print(f"顾客端 - 项目根目录: {self.project_root}")
        print(f"顾客端 - 数据文件: {self.data_file}")
        
        # 加载菜品数据
        self.dishes = load_dishes(self.data_file)
        print(f"顾客端加载了 {len(self.dishes)} 个菜品")
        
        # 设置UI
        self.setup_ui()
        
        # 刷新列表
        self.refresh_list()
    
    def setup_ui(self):
        # 主容器 - 使用Frame包装整个界面
        main_container = tk.Frame(self.root, bg="#f7f6f2")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title = tk.Label(main_container, text="🍽️ 顾客点餐端", 
                        font=("微软雅黑", 20, "bold"),
                        bg="#f7f6f2", fg="#2c3e50")
        title.pack(pady=20)
        
        # 内容区域
        content_frame = tk.Frame(main_container, bg="#f7f6f2")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # 左侧菜品列表
        left_frame = tk.Frame(content_frame, bg="#f7f6f2")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=15)
        left_frame.configure(width=400)  # 固定左侧宽度
        
        list_title = tk.Label(left_frame, text="📋 菜品菜单", 
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
                                 selectbackground="#27ae60",
                                 selectforeground="white",
                                 bd=0, highlightthickness=1,
                                 highlightcolor="#27ae60",
                                 yscrollcommand=scrollbar.set,
                                 width=35)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # 右侧预览和购物车区域
        right_frame = tk.Frame(content_frame, bg="#f7f6f2")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15)
        
        # 预览区域
        preview_title = tk.Label(right_frame, text="🖼️ 菜品预览", 
                               font=("微软雅黑", 16, "bold"),
                               bg="#f7f6f2", fg="#2c3e50")
        preview_title.pack(pady=(0, 15))
        
        # 预览图片容器 - 使用Frame包装，给预览图片更多空间
        preview_container = tk.Frame(right_frame, bg="#f7f6f2")
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 预览图片标签 - 让它占据容器的大部分空间
        self.preview_label = tk.Label(preview_container, 
                                    bg="#ffffff",
                                    text="点击左侧菜品查看预览图片",
                                    font=("微软雅黑", 12),
                                    fg="#7f8c8d",
                                    relief=tk.RIDGE, bd=2)
        self.preview_label.pack(fill=tk.BOTH, expand=True)  # 让预览图片占据可用空间
        
        # 已选菜品显示区域 - 固定高度，不占用太多空间
        selected_frame = tk.Frame(right_frame, bg="#f7f6f2")
        selected_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 购物车标题和删除按钮在同一行
        cart_title_frame = tk.Frame(selected_frame, bg="#f7f6f2")
        cart_title_frame.pack(fill=tk.X)
        
        selected_title = tk.Label(cart_title_frame, text="🛒 已选菜品", 
                                font=("微软雅黑", 14, "bold"),
                                bg="#f7f6f2", fg="#2c3e50")
        selected_title.pack(side=tk.LEFT)
        
        # 删除选中菜品按钮
        delete_item_btn = tk.Button(cart_title_frame, text="🗑️ 删除选中", 
                                   command=self.delete_selected_item,
                                   bg="#e74c3c", fg="white",
                                   font=("微软雅黑", 10, "bold"),
                                   width=10, height=1,
                                   bd=0, relief=tk.FLAT,
                                   cursor="hand2",
                                   activebackground="#c0392b")
        delete_item_btn.pack(side=tk.RIGHT)
        
        # 购物车列表框 - 固定较小高度
        cart_frame = tk.Frame(selected_frame)
        cart_frame.pack(fill=tk.X, pady=5)
        
        cart_scrollbar = tk.Scrollbar(cart_frame)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cart_listbox = tk.Listbox(cart_frame,
                                      font=("微软雅黑", 10),
                                      bg="#ffffff", fg="#2c3e50",
                                      selectbackground="#e74c3c",
                                      selectforeground="white",
                                      bd=1, relief=tk.RIDGE,
                                      height=4,  # 固定购物车高度
                                      yscrollcommand=cart_scrollbar.set)
        self.cart_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        cart_scrollbar.config(command=self.cart_listbox.yview)
        
        self.cart_listbox.bind('<<ListboxSelect>>', self.on_cart_select)
        
        # 购物车统计信息
        self.cart_info_label = tk.Label(selected_frame,
                                       text="暂无选择",
                                       font=("微软雅黑", 11, "bold"),
                                       bg="#f7f6f2", fg="#2c3e50")
        self.cart_info_label.pack(pady=5)
        
        # 设置按钮 - 确保按钮始终可见，固定在窗口底部
        self.setup_buttons(main_container)
        
    def setup_buttons(self, parent):
        # 按钮框架 - 固定在主容器底部，确保始终可见
        btn_frame = tk.Frame(parent, bg="#f7f6f2")
        btn_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)
        
        # 创建一个内部框架来居中按钮
        inner_btn_frame = tk.Frame(btn_frame, bg="#f7f6f2")
        inner_btn_frame.pack()
        
        btn_config = {
            "font": ("微软雅黑", 12, "bold"),
            "width": 15,
            "height": 2,
            "bd": 0,
            "relief": tk.FLAT,
            "cursor": "hand2"
        }
        
        # 添加到购物车按钮
        add_btn = tk.Button(inner_btn_frame, text="➕ 添加菜品", 
                           command=self.add_to_cart,
                           bg="#27ae60", fg="white",
                           activebackground="#2ecc71",
                           **btn_config)
        add_btn.pack(side=tk.LEFT, padx=15)
        
        # 随机推荐按钮
        random_btn = tk.Button(inner_btn_frame, text="🎲 随机推荐",
                              command=self.random_recommend,
                              bg="#f39c12", fg="white",
                              activebackground="#e67e22",
                              **btn_config)
        random_btn.pack(side=tk.LEFT, padx=15)
        
        # 清空购物车按钮
        clear_btn = tk.Button(inner_btn_frame, text="🗑️ 清空购物车",
                             command=self.clear_cart,
                             bg="#e74c3c", fg="white",
                             activebackground="#c0392b",
                             **btn_config)
        clear_btn.pack(side=tk.LEFT, padx=15)
        
        # 确认下单按钮
        order_btn = tk.Button(inner_btn_frame, text="✅ 确认下单",
                             command=self.place_order,
                             bg="#3498db", fg="white",
                             activebackground="#2980b9",
                             **btn_config)
        order_btn.pack(side=tk.LEFT, padx=15)
        
    def on_select(self, event):
        """选择菜品时的事件处理"""
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            dish = self.dishes[self.selected_index]
            self.show_preview(dish.image_path)
    
    def on_cart_select(self, event):
        """选择购物车中的菜品"""
        selection = self.cart_listbox.curselection()
        if selection:
            self.cart_selected_index = selection[0]
            
    def show_preview(self, image_path):
        """显示菜品预览图片"""
        try:
            # 处理路径
            if os.path.isabs(image_path):
                full_path = image_path
            else:
                if image_path.startswith("images"):
                    full_path = os.path.join(self.project_root, image_path)
                else:
                    full_path = os.path.join(self.project_root, "images", image_path)
            
            print(f"顾客端尝试加载图片: {full_path}")
            
            if not os.path.exists(full_path):
                self.preview_label.config(image="", text=f"图片文件不存在:\n{image_path}")
                self.current_preview_photo = None
                return
                
            img = Image.open(full_path)
            img = img.convert('RGB')
            # 增大预览图片尺寸，让菜品清晰可见
            img.thumbnail((200, 300), Image.Resampling.LANCZOS)  # 大幅增加图片尺寸
            
            # 确保在主线程中创建PhotoImage
            self.root.after_idle(lambda: self._update_preview_image(img))
            
        except Exception as e:
            print(f"顾客端预览图片错误: {e}")
            self.preview_label.config(image="", text=f"无法加载图片:\n{str(e)}")
            self.current_preview_photo = None
    
    def _update_preview_image(self, img):
        """在主线程中更新预览图片"""
        try:
            photo = ImageTk.PhotoImage(img)
            self.current_preview_photo = photo
            self.preview_label.config(image=photo, text="")
        except Exception as e:
            print(f"顾客端更新预览图片失败: {e}")
            self.preview_label.config(image="", text=f"显示图片失败:\n{str(e)}")
    
    def refresh_list(self):
        """刷新菜品列表"""
        self.listbox.delete(0, tk.END)
        for i, dish in enumerate(self.dishes):
            self.listbox.insert(tk.END, f"{i+1}. {dish.name}")
        print(f"顾客端列表已刷新，当前共有 {len(self.dishes)} 个菜品")
        
    def add_to_cart(self):
        """添加菜品到购物车"""
        if self.selected_index is not None and self.selected_index < len(self.dishes):
            dish = self.dishes[self.selected_index]
            self.selected_dishes.append(dish.name)
            self.update_cart_display()
            messagebox.showinfo("添加成功", f"已将 '{dish.name}' 添加到购物车！")
            print(f"添加菜品到购物车: {dish.name}")
        else:
            messagebox.showinfo("提示", "请先选择要添加的菜品！")
    
    def delete_selected_item(self):
        """删除购物车中选中的菜品"""
        if self.cart_selected_index is not None and self.cart_selected_index < len(self.selected_dishes):
            deleted_dish = self.selected_dishes[self.cart_selected_index]
            
            result = messagebox.askyesno("确认删除", f"确定要从购物车中删除 '{deleted_dish}' 吗？")
            if result:
                self.selected_dishes.pop(self.cart_selected_index)
                self.cart_selected_index = None
                self.update_cart_display()
                messagebox.showinfo("删除成功", f"已从购物车中删除 '{deleted_dish}'！")
                print(f"从购物车删除菜品: {deleted_dish}")
        else:
            messagebox.showinfo("提示", "请先在购物车中选择要删除的菜品！")
    
    def random_recommend(self):
        """随机推荐菜品"""
        if not self.dishes:
            messagebox.showinfo("提示", "暂无可推荐的菜品！")
            return
            
        # 随机选择一个菜品
        random_dish = random.choice(self.dishes)
        random_index = self.dishes.index(random_dish)
        
        # 在列表中选中并显示
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(random_index)
        self.listbox.see(random_index)
        self.selected_index = random_index
        self.show_preview(random_dish.image_path)
        
        messagebox.showinfo("随机推荐", f"为您推荐: {random_dish.name}\n快来看看吧！")
        print(f"随机推荐菜品: {random_dish.name}")
    
    def clear_cart(self):
        """清空购物车"""
        if not self.selected_dishes:
            messagebox.showinfo("提示", "购物车已经是空的！")
            return
            
        result = messagebox.askyesno("确认清空", "确定要清空购物车吗？")
        if result:
            self.selected_dishes.clear()
            self.cart_selected_index = None
            self.update_cart_display()
            messagebox.showinfo("清空成功", "购物车已清空！")
            print("购物车已清空")
    
    def place_order(self):
        """确认下单"""
        if not self.selected_dishes:
            messagebox.showinfo("提示", "购物车是空的，请先选择菜品！")
            return
        
        # 统计菜品数量
        dish_count = {}
        for dish in self.selected_dishes:
            dish_count[dish] = dish_count.get(dish, 0) + 1
        
        # 生成订单详情
        order_details = "订单详情:\n" + "="*30 + "\n"
        total_items = 0
        for dish, count in dish_count.items():
            order_details += f"{dish} x {count}\n"
            total_items += count
        
        order_details += "="*30 + f"\n总计: {total_items} 道菜"
        
        result = messagebox.askyesno("确认下单", f"{order_details}\n\n确认提交订单吗？")
        if result:
            # 清空购物车
            self.selected_dishes.clear()
            self.cart_selected_index = None
            self.update_cart_display()
            
            messagebox.showinfo("下单成功", "订单已提交！\n请耐心等待，厨师正在为您准备美食~")
            print(f"订单已提交: {dict(dish_count)}")
    
    def update_cart_display(self):
        """更新购物车显示"""
        # 清空购物车列表
        self.cart_listbox.delete(0, tk.END)
        
        if not self.selected_dishes:
            self.cart_listbox.insert(tk.END, "购物车为空")
            self.cart_info_label.config(text="暂无选择")
            return
        
        # 显示购物车中的菜品（按添加顺序）
        for i, dish in enumerate(self.selected_dishes):
            self.cart_listbox.insert(tk.END, f"{i+1}. {dish}")
        
        # 统计菜品数量
        dish_count = {}
        for dish in self.selected_dishes:
            dish_count[dish] = dish_count.get(dish, 0) + 1
        
        # 更新统计信息
        unique_dishes = len(dish_count)
        total_items = len(self.selected_dishes)
        
        info_text = f"共 {unique_dishes} 种菜品，总计 {total_items} 道菜"
        if unique_dishes > 0:
            info_text += "\n(点击列表项可选中，然后点击删除按钮)"
        
        self.cart_info_label.config(text=info_text)