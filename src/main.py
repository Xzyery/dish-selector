import tkinter as tk
from chef_app import ChefApp
from customer_app import CustomerApp

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("选择登录端口")
        self.root.configure(bg="#f7f6f2")
        self.root.geometry("400x300")
        
        # 窗口居中
        self.center_window()

        # 标题
        title = tk.Label(root, text="🍽️ 点菜系统", font=("微软雅黑", 20, "bold"),
                        bg="#f7f6f2", fg="#2c3e50")
        title.pack(pady=30)
        
        subtitle = tk.Label(root, text="请选择登录端口", font=("微软雅黑", 14),
                           bg="#f7f6f2", fg="#7f8c8d")
        subtitle.pack(pady=10)

        # 按钮框架
        btn_frame = tk.Frame(root, bg="#f7f6f2")
        btn_frame.pack(pady=40)
        
        btn_style = {
            "font": ("微软雅黑", 14, "bold"), 
            "width": 12, 
            "height": 2, 
            "bd": 0,
            "relief": tk.FLAT,
            "cursor": "hand2"
        }
        
        # 厨师端按钮
        chef_btn = tk.Button(btn_frame, text="👨‍🍳 厨师端", 
                            command=self.launch_chef_app,
                            bg="#3498db", fg="white", 
                            activebackground="#2980b9",
                            **btn_style)
        chef_btn.pack(side=tk.LEFT, padx=20)
        
        # 顾客端按钮
        customer_btn = tk.Button(btn_frame, text="🍽️ 顾客端", 
                                command=self.launch_customer_app,
                                bg="#27ae60", fg="white",
                                activebackground="#2ecc71", 
                                **btn_style)
        customer_btn.pack(side=tk.LEFT, padx=20)
        
        # 退出按钮
        exit_btn = tk.Button(root, text="❌ 退出", 
                            command=self.root.quit,
                            bg="#e74c3c", fg="white",
                            font=("微软雅黑", 12),
                            width=10, height=1,
                            bd=0, relief=tk.FLAT,
                            cursor="hand2",
                            activebackground="#c0392b")
        exit_btn.pack(pady=20)

    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def launch_chef_app(self):
        """启动厨师端"""
        print("启动厨师端...")
        
        # 隐藏启动器窗口
        self.root.withdraw()
        
        try:
            # 创建新的根窗口
            chef_root = tk.Toplevel(self.root)
            chef_root.withdraw()  # 先隐藏，等初始化完成再显示
            
            # 创建厨师应用
            chef_app = ChefApp(chef_root)
            
            # 显示厨师窗口
            chef_root.deiconify()
            
            # 当厨师窗口关闭时，重新显示启动器
            def on_chef_close():
                chef_root.destroy()
                self.root.deiconify()
            
            chef_root.protocol("WM_DELETE_WINDOW", on_chef_close)
            
        except Exception as e:
            print(f"启动厨师端失败: {e}")
            import traceback
            traceback.print_exc()
            self.root.deiconify()  # 发生错误时重新显示启动器

    def launch_customer_app(self):
        """启动顾客端"""
        print("启动顾客端...")
        
        # 隐藏启动器窗口
        self.root.withdraw()
        
        try:
            # 创建新的根窗口
            customer_root = tk.Toplevel(self.root)
            customer_root.withdraw()  # 先隐藏，等初始化完成再显示
            
            # 创建顾客应用
            customer_app = CustomerApp(customer_root)
            
            # 显示顾客窗口
            customer_root.deiconify()
            
            # 当顾客窗口关闭时，重新显示启动器
            def on_customer_close():
                customer_root.destroy()
                self.root.deiconify()
            
            customer_root.protocol("WM_DELETE_WINDOW", on_customer_close)
            
        except Exception as e:
            print(f"启动顾客端失败: {e}")
            import traceback
            traceback.print_exc()
            self.root.deiconify()  # 发生错误时重新显示启动器

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()