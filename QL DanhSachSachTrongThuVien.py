
import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import requests


try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

DATA_FILE = "data/books.json"
USER_FILE = "data/users.json"
BORROW_FILE = "data/borrows.json"
BG_IMAGE = "bg3.jpg"  # Hình nền mới
STATS_IMAGE = "data/stats.png"

os.makedirs("data", exist_ok=True)

def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Thư Viện")
        self.root.geometry("800x600")
        self.user_role = None
        self.username = None
        self.books = []
        self.borrows = []
        self.load_data()
        self.login_screen()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
        else:
            self.books = []
        
        if os.path.exists(BORROW_FILE):
            with open(BORROW_FILE, "r", encoding="utf-8") as f:
                self.borrows = json.load(f)
        else:
            self.borrows = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=4)
        with open(BORROW_FILE, "w", encoding="utf-8") as f:
            json.dump(self.borrows, f, indent=4)

    def crawl_books(self):
        try:
            response = requests.get("https://www.googleapis.com/books/v1/volumes?q=python+programming")
            data = response.json()
            items = data.get("items", [])
            
            for item in items[:5]:
                volume_info = item.get("volumeInfo", {})
                title = volume_info.get("title", "Tiêu Đề Không Xác Định")
                authors = volume_info.get("authors", ["Tác Giả Không Xác Định"])
                category = volume_info.get("categories", ["Chung"])[0]
                
                if not any(book["title"] == title for book in self.books):
                    self.books.append({
                        "id": str(uuid.uuid4()),
                        "title": title,
                        "author": ", ".join(authors),
                        "category": category,
                        "status": "available"
                    })
            self.save_data()
            return True
        except Exception as e:
            print(f"Lỗi thu thập dữ liệu: {e}")
            return False

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()

        login_frame = ttk.Frame(self.root, padding=20, style="Login.TFrame")
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)

        style = ttk.Style()
        style.configure("Login.TFrame", background="white")
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 11))
        style.configure("TEntry", padding=5)

        # Căn chỉnh lưới
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)
        login_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        ttk.Label(login_frame, text="Hệ Thống Quản Lý Thư Viện", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(login_frame, text="Tên Đăng Nhập").grid(row=1, column=0, pady=10, sticky="e")
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=1, column=1, pady=10, sticky="w")

        ttk.Label(login_frame, text="Mật Khẩu").grid(row=2, column=0, pady=10, sticky="e")
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=10, sticky="w")

        self.show_password_var = tk.IntVar()
        ttk.Checkbutton(login_frame, text="Hiện Mật Khẩu", variable=self.show_password_var, command=self.toggle_password).grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(login_frame, text="Đăng Nhập", command=self.login).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(login_frame, text="Đăng Ký", command=self.register_screen).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(login_frame, text="Thu Thập Sách", command=self.crawl_and_update).grid(row=6, column=0, columnspan=2, pady=10)

    def set_background(self):
        try:
            bg = Image.open(BG_IMAGE)
            bg = bg.resize((800, 600), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(bg)
            self.canvas = tk.Canvas(self.root, width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except:
            self.canvas = tk.Canvas(self.root, width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            for i in range(600):
                blue = int(255 * (i / 600))
                color = f"#{0:02x}{0:02x}{blue:02x}"
                self.canvas.create_line(0, i, 800, i, fill=color)

    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def crawl_and_update(self):
        if self.crawl_books():
            messagebox.showinfo("Thành Công", "Đã thu thập và thêm sách thành công.")
        else:
            messagebox.showerror("Lỗi", "Không thể thu thập sách.")

    def register_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        reg_frame = ttk.Frame(self.root, padding=20, style="Login.TFrame")
        reg_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

        reg_frame.grid_columnconfigure(0, weight=1)
        reg_frame.grid_columnconfigure(1, weight=1)
        reg_frame.grid_rowconfigure(tuple(range(9)), weight=1)

        self.reg_username = tk.StringVar()
        self.reg_password = tk.StringVar()
        self.reg_name = tk.StringVar()
        self.reg_phone = tk.StringVar()
        self.reg_email = tk.StringVar()
        self.reg_address = tk.StringVar()
        self.reg_role = tk.StringVar(value="docgia")

        fields = [
            ("Tên Đăng Nhập", self.reg_username),
            ("Mật Khẩu", self.reg_password),
            ("Họ Tên", self.reg_name),
            ("Số Điện Thoại", self.reg_phone),
            ("Email", self.reg_email),
            ("Địa Chỉ", self.reg_address),
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(reg_frame, text=label).grid(row=i, column=0, pady=10, sticky="e")
            ttk.Entry(reg_frame, textvariable=var).grid(row=i, column=1, pady=10, sticky="w")

        ttk.Label(reg_frame, text="Vai Trò").grid(row=len(fields), column=0, pady=10, sticky="e")
        ttk.OptionMenu(reg_frame, self.reg_role, "docgia", "admin", "thuthu").grid(row=len(fields), column=1, pady=10, sticky="w")

        ttk.Button(reg_frame, text="Đăng Ký", command=self.register).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        ttk.Button(reg_frame, text="Quay Lại", command=self.login_screen).grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

    def register(self):
        username = self.reg_username.get()
        password = hash_password(self.reg_password.get())
        name = self.reg_name.get()
        phone = self.reg_phone.get()
        email = self.reg_email.get()
        address = self.reg_address.get()
        role = self.reg_role.get()

        if not all([username, password, name, phone, email, address, role]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        users = []
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)

        for user in users:
            if user["username"] == username:
                messagebox.showwarning("Lỗi", "Tên đăng nhập đã tồn tại.")
                return

        users.append({
            "username": username,
            "password": password,
            "role": role,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address
        })

        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)

        messagebox.showinfo("Thành Công", "Đăng ký thành công. Vui lòng đăng nhập.")
        self.login_screen()

    def login(self):
        username = self.username_entry.get()
        password = hash_password(self.password_entry.get())

        if not os.path.exists(USER_FILE):
            messagebox.showerror("Lỗi", "Không có dữ liệu người dùng.")
            return

        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        for user in users:
            if user["username"] == username and user["password"] == password:
                self.user_role = user["role"]
                self.username = username
                self.main_screen()
                return

        messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        main_frame = ttk.Frame(self.root, padding=20, style="Login.TFrame")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(tuple(range(6)), weight=1)

        ttk.Label(main_frame, text=f"Chào mừng, {self.username} ({self.user_role})", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        if self.user_role == "admin":
            ttk.Label(main_frame, text="(Quản lý toàn bộ hệ thống)").grid(row=1, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Quản Lý Sách", command=self.manage_books).grid(row=2, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Thống Kê Sách", command=self.stats_screen).grid(row=3, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Quản Lý Mượn Sách", command=self.manage_borrows).grid(row=4, column=0, columnspan=2, pady=10)
        elif self.user_role == "thuthu":
            ttk.Label(main_frame, text="(Quản lý sách và mượn sách)").grid(row=1, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Quản Lý Sách", command=self.manage_books).grid(row=2, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Quản Lý Mượn Sách", command=self.manage_borrows).grid(row=3, column=0, columnspan=2, pady=10)
        elif self.user_role == "docgia":
            ttk.Label(main_frame, text="(Tìm kiếm và mượn sách)").grid(row=1, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Tìm Kiếm Sách", command=self.search_books_screen).grid(row=2, column=0, columnspan=2, pady=10)
            ttk.Button(main_frame, text="Sách Đang Mượn", command=self.my_borrows).grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(main_frame, text="Đăng Xuất", command=self.login_screen).grid(row=5, column=0, columnspan=2, pady=10)

    def manage_books(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        book_frame = ttk.Frame(self.root, padding=20)
        book_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)

        book_frame.grid_columnconfigure(0, weight=1)
        book_frame.grid_columnconfigure(1, weight=1)
        book_frame.grid_rowconfigure(tuple(range(6)), weight=1)

        columns = ("ID", "Tiêu Đề", "Tác Giả", "Thể Loại", "Trạng Thái")
        self.tree = ttk.Treeview(book_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(book_frame, text="Tiêu Đề").grid(row=1, column=0, pady=10, sticky="e")
        self.book_title = tk.StringVar()
        ttk.Entry(book_frame, textvariable=self.book_title).grid(row=1, column=1, pady=10, sticky="w")

        ttk.Label(book_frame, text="Tác Giả").grid(row=2, column=0, pady=10, sticky="e")
        self.book_author = tk.StringVar()
        ttk.Entry(book_frame, textvariable=self.book_author).grid(row=2, column=1, pady=10, sticky="w")

        ttk.Label(book_frame, text="Thể Loại").grid(row=3, column=0, pady=10, sticky="e")
        self.book_category = tk.StringVar()
        ttk.Entry(book_frame, textvariable=self.book_category).grid(row=3, column=1, pady=10, sticky="w")

        ttk.Button(book_frame, text="Thêm Sách", command=self.add_book).grid(row=4, column=0, pady=10)
        ttk.Button(book_frame, text="Sửa Sách", command=self.edit_book).grid(row=4, column=1, pady=10)
        ttk.Button(book_frame, text="Xóa Sách", command=self.delete_book).grid(row=5, column=0, pady=10)
        ttk.Button(book_frame, text="Quay Lại", command=self.main_screen).grid(row=5, column=1, pady=10)

        self.update_book_list()

    def add_book(self):
        title = self.book_title.get()
        author = self.book_author.get()
        category = self.book_category.get()

        if not all([title, author, category]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        book = {
            "id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "category": category,
            "status": "available"
        }
        self.books.append(book)
        self.save_data()
        self.update_book_list()
        self.book_title.set("")
        self.book_author.set("")
        self.book_category.set("")
        messagebox.showinfo("Thành Công", "Đã thêm sách thành công.")

    def edit_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một cuốn sách để sửa.")
            return

        book_id = self.tree.item(selected)["values"][0]
        title = self.book_title.get()
        author = self.book_author.get()
        category = self.book_category.get()

        if not all([title, author, category]):
            messagebox.showwarning("Thiếu Thông Tin", "Vui lòng điền đầy đủ tất cả các trường.")
            return

        for book in self.books:
            if book["id"] == book_id:
                book["title"] = title
                book["author"] = author
                book["category"] = category
                break

        self.save_data()
        self.update_book_list()
        self.book_title.set("")
        self.book_author.set("")
        self.book_category.set("")
        messagebox.showinfo("Thành Công", "Đã cập nhật sách thành công.")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một cuốn sách để xóa.")
            return

        book_id = self.tree.item(selected)["values"][0]
        if any(borrow["book_id"] == book_id and not borrow["returned"] for borrow in self.borrows):
            messagebox.showwarning("Lỗi", "Không thể xóa sách đang được mượn.")
            return

        self.books = [book for book in self.books if book["id"] != book_id]
        self.save_data()
        self.update_book_list()
        messagebox.showinfo("Thành Công", "Đã xóa sách thành công.")

    def update_book_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for book in self.books:
            status = "Có Sẵn" if book["status"] == "available" else "Đang Mượn"
            self.tree.insert("", "end", values=(book["id"], book["title"], book["author"], book["category"], status))

    def search_books_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        search_frame = ttk.Frame(self.root, padding=20)
        search_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)

        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_rowconfigure(tuple(range(6)), weight=1)

        ttk.Label(search_frame, text="Tìm Kiếm Sách").grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(search_frame, text="Từ Khóa").grid(row=1, column=0, pady=10, sticky="e")
        self.search_term = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_term).grid(row=1, column=1, pady=10, sticky="w")

        ttk.Label(search_frame, text="Thể Loại").grid(row=2, column=0, pady=10, sticky="e")
        self.search_category = tk.StringVar()
        categories = list(set(book["category"] for book in self.books)) + ["Tất Cả"]
        ttk.Combobox(search_frame, textvariable=self.search_category, values=categories).grid(row=2, column=1, pady=10, sticky="w")

        columns = ("ID", "Tiêu Đề", "Tác Giả", "Thể Loại", "Trạng Thái")
        self.search_tree = ttk.Treeview(search_frame, columns=columns, show="headings")
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=120)
        self.search_tree.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(search_frame, text="Tìm Kiếm", command=self.search_books).grid(row=4, column=0, pady=10)
        ttk.Button(search_frame, text="Mượn Sách", command=self.borrow_book).grid(row=4, column=1, pady=10)
        ttk.Button(search_frame, text="Quay Lại", command=self.main_screen).grid(row=5, column=0, columnspan=2, pady=10)

        self.search_books()

    def search_books(self):
        term = self.search_term.get().lower()
        category = self.search_category.get()

        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        for book in self.books:
            if (not term or term in book["title"].lower() or term in book["author"].lower()) and \
               (category == "Tất Cả" or not category or book["category"] == category):
                status = "Có Sẵn" if book["status"] == "available" else "Đang Mượn"
                self.search_tree.insert("", "end", values=(book["id"], book["title"], book["author"], book["category"], status))

    def borrow_book(self):
        if self.user_role != "docgia":
            messagebox.showwarning("Không Có Quyền", "Chỉ độc giả mới có thể mượn sách.")
            return

        selected = self.search_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một cuốn sách để mượn.")
            return

        book_id = self.search_tree.item(selected)["values"][0]
        book = next((b for b in self.books if b["id"] == book_id), None)
        if not book or book["status"] != "available":
            messagebox.showwarning("Lỗi", "Sách không có sẵn để mượn.")
            return

        borrow = {
            "id": str(uuid.uuid4()),
            "book_id": book_id,
            "username": self.username,
            "borrow_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "returned": False
        }
        self.borrows.append(borrow)
        book["status"] = "borrowed"
        self.save_data()
        self.search_books()
        messagebox.showinfo("Thành Công", "Đã mượn sách thành công.")

    def manage_borrows(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        borrow_frame = ttk.Frame(self.root, padding=20)
        borrow_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        borrow_frame.grid_columnconfigure(0, weight=1)
        borrow_frame.grid_columnconfigure(1, weight=1)
        borrow_frame.grid_rowconfigure((0, 1), weight=1)

        columns = ("ID", "Tiêu Đề Sách", "Tên Người Mượn", "Ngày Mượn", "Ngày Trả", "Trạng Thái")
        self.borrow_tree = ttk.Treeview(borrow_frame, columns=columns, show="headings")
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=100)
        self.borrow_tree.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Button(borrow_frame, text="Trả Sách", command=self.return_book).grid(row=1, column=0, pady=10)
        ttk.Button(borrow_frame, text="Quay Lại", command=self.main_screen).grid(row=1, column=1, pady=10)

        self.update_borrow_list()

    def update_borrow_list(self):
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)
        for borrow in self.borrows:
            book = next((b for b in self.books if b["id"] == borrow["book_id"]), None)
            title = book["title"] if book else "Không Xác Định"
            status = "Đã Trả" if borrow["returned"] else "Đang Mượn"
            self.borrow_tree.insert("", "end", values=(borrow["id"], title, borrow["username"], borrow["borrow_date"], borrow["due_date"], status))

    def return_book(self):
        selected = self.borrow_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một bản ghi mượn để trả.")
            return

        borrow_id = self.borrow_tree.item(selected)["values"][0]
        borrow = next((b for b in self.borrows if b["id"] == borrow_id), None)
        if not borrow or borrow["returned"]:
            messagebox.showwarning("Lỗi", "Bản ghi mượn không hợp lệ hoặc đã được trả.")
            return

        borrow["returned"] = True
        book = next((b for b in self.books if b["id"] == borrow["book_id"]), None)
        if book:
            book["status"] = "available"
        self.save_data()
        self.update_borrow_list()
        messagebox.showinfo("Thành Công", "Đã trả sách thành công.")

    def my_borrows(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        borrow_frame = ttk.Frame(self.root, padding=20)
        borrow_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        borrow_frame.grid_columnconfigure(0, weight=1)
        borrow_frame.grid_columnconfigure(1, weight=1)
        borrow_frame.grid_rowconfigure((0, 1), weight=1)

        columns = ("ID", "Tiêu Đề Sách", "Ngày Mượn", "Ngày Trả", "Trạng Thái")
        self.borrow_tree = ttk.Treeview(borrow_frame, columns=columns, show="headings")
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.borrow_tree.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Button(borrow_frame, text="Quay Lại", command=self.main_screen).grid(row=1, column=0, columnspan=2, pady=10)

        for borrow in self.borrows:
            if borrow["username"] == self.username:
                book = next((b for b in self.books if b["id"] == borrow["book_id"]), None)
                title = book["title"] if book else "Không Xác Định"
                status = "Đã Trả" if borrow["returned"] else "Đang Mượn"
                self.borrow_tree.insert("", "end", values=(borrow["id"], title, borrow["borrow_date"], borrow["due_date"], status))

    def generate_stats_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            return False

        categories = {}
        statuses = {"available": 0, "borrowed": 0}
        for book in self.books:
            categories[book["category"]] = categories.get(book["category"], 0) + 1
            statuses[book["status"]] = statuses.get(book["status"], 0) + 1

        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        cat_names = list(categories.keys())
        cat_counts = list(categories.values())
        plt.bar(cat_names, cat_counts, color='skyblue')
        plt.title("Sách Theo Thể Loại")
        plt.xlabel("Thể Loại")
        plt.ylabel("Số Lượng Sách")
        plt.xticks(rotation=45, ha="right")

        plt.subplot(1, 2, 2)
        status_names = ["Có Sẵn", "Đang Mượn"]
        status_counts = [statuses["available"], statuses["borrowed"]]
        plt.bar(status_names, status_counts, color='lightgreen')
        plt.title("Sách Theo Trạng Thái")
        plt.xlabel("Trạng Thái")
        plt.ylabel("Số Lượng Sách")

        plt.tight_layout()
        plt.savefig(STATS_IMAGE)
        plt.close()
        return True

    def stats_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_background()
        stats_frame = ttk.Frame(self.root, padding=20)
        stats_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(tuple(range(10)), weight=1)

        chart_success = self.generate_stats_chart()
        
        if chart_success:
            try:
                stats_img = Image.open(STATS_IMAGE)
                stats_img = stats_img.resize((600, 300), Image.LANCZOS)
                self.stats_image = ImageTk.PhotoImage(stats_img)
                ttk.Label(stats_frame, image=self.stats_image).grid(row=0, column=0, columnspan=2, pady=10)
            except:
                ttk.Label(stats_frame, text="Lỗi tải biểu đồ thống kê").grid(row=0, column=0, columnspan=2, pady=10)
        else:
            ttk.Label(stats_frame, text="Chưa cài đặt Matplotlib, không hiển thị biểu đồ").grid(row=0, column=0, columnspan=2, pady=10)

        categories = {}
        statuses = {"available": 0, "borrowed": 0}
        for book in self.books:
            categories[book["category"]] = categories.get(book["category"], 0) + 1
            statuses[book["status"]] = statuses.get(book["status"], 0) + 1

        ttk.Label(stats_frame, text="Thống Kê Sách", font=("Arial", 16, "bold")).grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(stats_frame, text="Thể Loại:").grid(row=2, column=0, sticky="w", pady=5)
        for i, (cat, count) in enumerate(categories.items(), 3):
            ttk.Label(stats_frame, text=f"{cat}: {count} cuốn").grid(row=i, column=0, sticky="w", pady=2)

        ttk.Label(stats_frame, text="Trạng Thái:").grid(row=len(categories)+3, column=0, sticky="w", pady=5)
        ttk.Label(stats_frame, text=f"Có Sẵn: {statuses['available']} cuốn").grid(row=len(categories)+4, column=0, sticky="w", pady=2)
        ttk.Label(stats_frame, text=f"Đang Mượn: {statuses['borrowed']} cuốn").grid(row=len(categories)+5, column=0, sticky="w", pady=2)

        ttk.Button(stats_frame, text="Quay Lại", command=self.main_screen).grid(row=len(categories)+6, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()