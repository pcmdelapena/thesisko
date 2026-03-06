import tkinter as tk
from tkinter import messagebox
import mariadb
import qrcode
from datetime import datetime
from PIL import ImageTk, Image

# --- DATABASE CONNECTION ---
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "prince", 
    "database": "my_project"
}

class WasteMonitoringSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Waste Monitoring")
        self.root.attributes('-fullscreen', True) 
        self.root.configure(bg="#0a0f1e") 
        
        self.current_points = 0
        self.connect_db()
        self.setup_ui()

    def connect_db(self):
        try:
            self.conn = mariadb.connect(**db_config)
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            messagebox.showerror("Database Error", f"Cannot connect to MariaDB: {e}")

    def process_scan(self, event):
        barcode = self.scan_entry.get().strip().upper()
        self.scan_entry.delete(0, tk.END)
        
        if not barcode:
            return

        self.cursor.execute("SELECT name, points FROM product_list WHERE barcode = ?", (barcode,))
        result = self.cursor.fetchone()

        if result:
            p_name, p_points = result
            self.current_points += p_points
            self.points_label.config(text=str(self.current_points))
            self.status_label.config(text=f"SUCCESS: {p_name} ACCEPTED (+{p_points} pts)", fg="#00ffcc")
        else:
            self.status_label.config(text="ERROR: UNKNOWN BOTTLE / ITEM", fg="#ff4d4d")
            
        self.scan_entry.focus_set()

    def generate_qr(self):
        if self.current_points > 0:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            qr_data = f"THESIS REWARD TICKET\nPoints: {self.current_points}\nDate: {timestamp}"
            qrcode.make(qr_data).save("reward_ticket.png")
            
            self.qr_win = tk.Toplevel(self.root)
            self.qr_win.geometry("500x600")
            self.qr_win.configure(bg="white")
            self.qr_win.attributes('-topmost', True) 
            
            img_raw = Image.open("reward_ticket.png").resize((320, 320))
            qr_img = ImageTk.PhotoImage(img_raw)
            label = tk.Label(self.qr_win, image=qr_img, bg="white")
            label.image = qr_img
            label.pack(pady=20)
            
            tk.Label(self.qr_win, text="SCAN TO CLAIM REWARD", font=("Helvetica", 16, "bold"), bg="white", fg="#333").pack()
            tk.Label(self.qr_win, text=f"TOTAL POINTS: {self.current_points}", font=("Helvetica", 24, "bold"), bg="white", fg="#1a73e8").pack(pady=5)
            
            tk.Button(self.qr_win, text="DONE (NEXT TRANSACTION)", command=self.close_qr, font=("Arial", 12, "bold"), bg="#ff4d4d", fg="white", bd=0, padx=20, pady=10).pack(pady=15)
            self.qr_win.focus_set()
        else:
            messagebox.showwarning("Empty", "No points accumulated yet.")
            self.scan_entry.focus_set()

    def close_qr(self):
        try:
            if self.qr_win.winfo_exists():
                self.qr_win.destroy()
        except:
            pass
        self.current_points = 0
        self.points_label.config(text="0")
        self.status_label.config(text="READY: PLEASE INSERT A BOTTLE", fg="#888")
        self.scan_entry.focus_set()

    # =======================================================
    # VIRTUAL ON-SCREEN KEYBOARDS (BAGONG DAGDAG!)
    # =======================================================
    def ask_with_keyboard(self, title, prompt):
        self.kb_result = None
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("750x450")
        win.configure(bg="#0a0f1e")
        win.attributes('-topmost', True)

        tk.Label(win, text=prompt, font=("Helvetica", 14, "bold"), fg="white", bg="#0a0f1e").pack(pady=10)
        entry = tk.Entry(win, font=("Helvetica", 20), justify="center", width=35)
        entry.pack(pady=10)
        entry.focus_set()

        kb_frame = tk.Frame(win, bg="#0a0f1e")
        kb_frame.pack()

        keys = [
            ['1','2','3','4','5','6','7','8','9','0'],
            ['Q','W','E','R','T','Y','U','I','O','P'],
            ['A','S','D','F','G','H','J','K','L'],
            ['Z','X','C','V','B','N','M','-','.']
        ]

        for row in keys:
            f = tk.Frame(kb_frame, bg="#0a0f1e")
            f.pack()
            for key in row:
                cmd = lambda k=key: entry.insert(tk.END, k)
                tk.Button(f, text=key, font=("Arial", 14, "bold"), width=3, height=2, bg="#333", fg="white", command=cmd).pack(side=tk.LEFT, padx=3, pady=3)

        bf = tk.Frame(kb_frame, bg="#0a0f1e")
        bf.pack(pady=5)
        tk.Button(bf, text="DEL", font=("Arial", 14, "bold"), width=6, height=2, bg="#ff4d4d", fg="white", command=lambda: entry.delete(len(entry.get())-1, tk.END) if entry.get() else None).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="SPACE", font=("Arial", 14, "bold"), width=15, height=2, bg="#555", fg="white", command=lambda: entry.insert(tk.END, " ")).pack(side=tk.LEFT, padx=5)
        
        def on_done(event=None):
            self.kb_result = entry.get().strip()
            win.destroy()
            
        tk.Button(bf, text="DONE", font=("Arial", 14, "bold"), width=6, height=2, bg="#1a73e8", fg="white", command=on_done).pack(side=tk.LEFT, padx=5)
        entry.bind('<Return>', on_done)
        self.root.wait_window(win)
        return self.kb_result

    def ask_with_numpad(self, title, prompt, is_password=False):
        self.num_result = None
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x500")
        win.configure(bg="#0a0f1e")
        win.attributes('-topmost', True)

        tk.Label(win, text=prompt, font=("Helvetica", 14, "bold"), fg="white", bg="#0a0f1e").pack(pady=10)
        show_char = "*" if is_password else ""
        entry = tk.Entry(win, font=("Helvetica", 24, "bold"), justify="center", width=15, show=show_char)
        entry.pack(pady=10)
        entry.focus_set()

        keypad = tk.Frame(win, bg="#0a0f1e")
        keypad.pack()

        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', 'DONE']
        row_idx, col_idx = 0, 0
        for btn in buttons:
            if btn == 'C':
                action = lambda: entry.delete(0, tk.END)
                bg_color = "#ff4d4d"
            elif btn == 'DONE':
                def on_done(event=None):
                    self.num_result = entry.get().strip()
                    win.destroy()
                action = on_done
                bg_color = "#1a73e8"
                entry.bind('<Return>', on_done) # Para mabasa ng scanner kung sakali
            else:
                action = lambda x=btn: entry.insert(tk.END, x)
                bg_color = "#333"

            tk.Button(keypad, text=btn, font=("Arial", 18, "bold"), width=4, height=2, bg=bg_color, fg="white", command=action).grid(row=row_idx, column=col_idx, padx=5, pady=5)
            col_idx += 1
            if col_idx > 2:
                col_idx = 0
                row_idx += 1

        self.root.wait_window(win)
        return self.num_result
    # =======================================================
    # ADMIN PANEL & REGISTRATION
    # =======================================================
    def admin_panel(self):
        pin = self.ask_with_numpad("Admin Login", "ENTER ADMIN PIN", is_password=True)
        if pin == "1722":
            self.show_admin_menu()
        elif pin is not None:
            messagebox.showerror("Denied", "Incorrect PIN.")
        self.scan_entry.focus_set()

    def show_admin_menu(self):
        self.admin_win = tk.Toplevel(self.root)
        self.admin_win.title("Admin Menu")
        self.admin_win.geometry("400x300")
        self.admin_win.configure(bg="#16213e")
        self.admin_win.attributes('-topmost', True)
        
        tk.Label(self.admin_win, text="ADMINISTRATOR MENU", font=("Helvetica", 16, "bold"), bg="#16213e", fg="#00d2ff").pack(pady=20)
        
        tk.Button(self.admin_win, text="REGISTER NEW BOTTLE", command=self.register_bottle, font=("Arial", 12, "bold"), bg="#1a73e8", fg="white", pady=10, width=25).pack(pady=10)
        tk.Button(self.admin_win, text="SHUTDOWN SYSTEM", command=self.root.destroy, font=("Arial", 12, "bold"), bg="#ff4d4d", fg="white", pady=10, width=25).pack(pady=10)
        tk.Button(self.admin_win, text="CANCEL", command=self.close_admin_menu, font=("Arial", 10), bg="#888", fg="white", pady=5, width=15).pack(pady=10)
        
        self.admin_win.protocol("WM_DELETE_WINDOW", self.close_admin_menu)

    def close_admin_menu(self):
        self.admin_win.destroy()
        self.scan_entry.focus_set()

    def register_bottle(self):
        # 1. Barcode - Gamit Numpad (Pero PWEDE MO NA I-SCAN DITO MISMO)
        barcode = self.ask_with_numpad("Scan Barcode", "SCAN THE NEW BOTTLE\n(Or type barcode):")
        if barcode:
            # 2. Name - Gamit QWERTY Keyboard
            name = self.ask_with_keyboard("Bottle Name", "Enter Bottle Name & Size\n(e.g. COKE 500ML):")
            if name:
                # 3. Points - Gamit Numpad
                pts = self.ask_with_numpad("Points", "How many points is this worth?")
                if pts and pts.isdigit():
                    try:
                        self.cursor.execute("INSERT INTO product_list (barcode, name, points) VALUES (?, ?, ?)", (barcode, name, int(pts)))
                        self.conn.commit()
                        messagebox.showinfo("Success", f"{name} saved to database!")
                    except mariadb.Error as e:
                        messagebox.showerror("Error", f"Barcode already exists or DB Error.\n{e}")
                else:
                    if pts is not None:
                        messagebox.showwarning("Invalid", "Points must be a number.")
        
        if hasattr(self, 'admin_win') and self.admin_win.winfo_exists():
            self.admin_win.destroy()
        self.scan_entry.focus_set()

    def setup_ui(self):
        # HEADER
        nav = tk.Frame(self.root, bg="#16213e", height=100)
        nav.pack(fill="x")
        tk.Label(nav, text="AUTOMATED WASTE MONITORING", font=("Impact", 36), fg="#00d2ff", bg="#16213e").pack(pady=(15, 0))
        tk.Label(nav, text="AND REWARD SYSTEM VIA QR CODE", font=("Helvetica", 14, "bold"), fg="#4ecca3", bg="#16213e").pack(pady=(0, 10))

        # MAIN BODY
        main = tk.Frame(self.root, bg="#0a0f1e")
        main.pack(expand=True)

        tk.Label(main, text="CURRENT POINTS", font=("Helvetica", 18, "bold"), fg="#ffffff", bg="#0a0f1e").pack()
        self.points_label = tk.Label(main, text="0", font=("Arial", 120, "bold"), fg="#00ffcc", bg="#0a0f1e") 
        self.points_label.pack()

        self.status_label = tk.Label(main, text="READY: PLEASE INSERT A BOTTLE", font=("Helvetica", 16, "italic"), fg="#888", bg="#0a0f1e")
        self.status_label.pack(pady=20)

        btn_claim = tk.Button(main, text="GENERATE QR REWARD", command=self.generate_qr, font=("Helvetica", 18, "bold"), bg="#1a73e8", fg="white", padx=30, pady=15, bd=0)
        btn_claim.pack()
     # HIDDEN SCANNER INPUT
        self.scan_entry = tk.Entry(self.root, width=1, bd=0, bg="#0a0f1e", fg="#0a0f1e", insertontime=0)
        self.scan_entry.pack()
        self.scan_entry.bind('<Return>', self.process_scan)
        self.scan_entry.focus_set()

        # FOCUS BINDINGS (Clicking the background returns focus to the scanner)
        def return_focus(event):
            self.scan_entry.focus_set()
        nav.bind("<Button-1>", return_focus)
        main.bind("<Button-1>", return_focus)

        tk.Button(self.root, text="ADMIN", command=self.admin_panel, font=("Arial", 10, "bold"), bg="#333", fg="#fff", bd=0, padx=10, pady=5).place(relx=0.02, rely=0.96, anchor="sw")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = WasteMonitoringSystem(app_root)
    app_root.mainloop()   
