import customtkinter as ctk
import math
import re

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # تنظیمات پنجره
        self.title("TD - Calculator Pro")
        self.geometry("400x700")
        self.minsize(350, 600)
        self.configure(fg_color="#000000")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # وضعیت
        self.expression = ""
        self.display_expr = ""
        self.memory = 0.0
        self.last_was_result = False
        self.scientific_visible = False

        # رنگ‌ها (استایل iOS)
        self.c_num = "#333333"
        self.c_num_hover = "#737373"
        self.c_op = "#FF9500"
        self.c_op_hover = "#FFB143"
        self.c_func = "#A5A5A5"
        self.c_func_hover = "#D4D4D4"
        self.c_eq = "#FF9500"
        self.c_eq_hover = "#FFB143"

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- نمایشگر ---
        display_frame = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        display_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(20, 10))
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_rowconfigure(1, weight=2)

        self.history_label = ctk.CTkLabel(
            display_frame, text="", font=ctk.CTkFont("Segoe UI", 18),
            text_color="#888888", anchor="e"
        )
        self.history_label.grid(row=0, column=0, sticky="se", padx=5)

        self.main_display = ctk.CTkLabel(
            display_frame, text="0", font=ctk.CTkFont("Segoe UI", 48, weight="bold"),
            text_color="white", anchor="e"
        )
        self.main_display.grid(row=1, column=0, sticky="se", padx=5, pady=5)

        # --- دکمه بازشو مهندسی ---
        self.toggle_btn = ctk.CTkButton(
            self, text="Scientific ▼", width=120, height=30,
            fg_color=self.c_func, text_color="black", hover_color=self.c_func_hover,
            font=ctk.CTkFont("Segoe UI", 12), command=self._toggle_scientific
        )
        self.toggle_btn.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 5))

        # --- پنل مهندسی (مخفی در ابتدا) ---
        self.sci_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sci_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for r in range(3):
            self.sci_frame.grid_rowconfigure(r, weight=1)

        sci_buttons = [
            ("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2), ("log", 0, 3),
            ("ln", 1, 0), ("x²", 1, 1), ("√", 1, 2), ("1/x", 1, 3),
            ("π", 2, 0), ("e", 2, 1), ("(", 2, 2), (")", 2, 3),
        ]
        for text, r, c in sci_buttons:
            ctk.CTkButton(
                self.sci_frame, text=text, font=ctk.CTkFont("Segoe UI", 16),
                fg_color=self.c_func, text_color="black", hover_color=self.c_func_hover,
                command=lambda t=text: self._sci_press(t)
            ).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        # --- دکمه‌های اصلی ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for r in range(6):
            self.btn_frame.grid_rowconfigure(r, weight=1)

        buttons = [
            ("MC", 0, 0, "func"), ("MR", 0, 1, "func"), ("M+", 0, 2, "func"), ("M-", 0, 3, "func"),
            ("C", 1, 0, "func"), ("±", 1, 1, "func"), ("%", 1, 2, "func"), ("÷", 1, 3, "op"),
            ("7", 2, 0, "num"), ("8", 2, 1, "num"), ("9", 2, 2, "num"), ("×", 2, 3, "op"),
            ("4", 3, 0, "num"), ("5", 3, 1, "num"), ("6", 3, 2, "num"), ("-", 3, 3, "op"),
            ("1", 4, 0, "num"), ("2", 4, 1, "num"), ("3", 4, 2, "num"), ("+", 4, 3, "op"),
            ("⌫", 5, 0, "func"), ("0", 5, 1, "num"), (".", 5, 2, "num"), ("=", 5, 3, "eq"),
        ]

        for text, r, c, btype in buttons:
            self._make_button(text, r, c, btype)

    def _make_button(self, text, row, col, btype):
        cfg = {
            "num": (self.c_num, "white", self.c_num_hover, 24),
            "op": (self.c_op, "white", self.c_op_hover, 28),
            "func": (self.c_func, "black", self.c_func_hover, 20),
            "eq": (self.c_eq, "white", self.c_eq_hover, 28),
        }
        fg, tx, hv, sz = cfg[btype]
        ctk.CTkButton(
            self.btn_frame, text=text, font=ctk.CTkFont("Segoe UI", sz),
            fg_color=fg, text_color=tx, hover_color=hv,
            command=lambda t=text: self._press(t)
        ).grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    def _toggle_scientific(self):
        self.scientific_visible = not self.scientific_visible
        if self.scientific_visible:
            self.toggle_btn.configure(text="Scientific ▲")
            self.sci_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 5))
            self.btn_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
            self.geometry("400x820")
        else:
            self.toggle_btn.configure(text="Scientific ▼")
            self.sci_frame.grid_remove()
            self.btn_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
            self.geometry("400x700")

    def _press(self, text):
        if self.last_was_result and text not in ("=", "C", "⌫", "M+", "M-", "MC", "MR", "%", "±"):
            if text in ("+", "-", "×", "÷"):
                self.last_was_result = False
            else:
                self._clear()

        if text in "0123456789":
            self._digit(text)
        elif text == ".":
            self._dot()
        elif text in ("+", "-", "×", "÷"):
            self._operator(text)
        elif text == "=":
            self._equal()
        elif text == "C":
            self._clear()
        elif text == "⌫":
            self._backspace()
        elif text == "±":
            self._negate()
        elif text == "%":
            self._percent()
        elif text in ("MC", "MR", "M+", "M-"):
            self._memory(text)

    def _sci_press(self, text):
        if self.last_was_result:
            self.last_was_result = False

        if text == "π":
            self._set_num(str(math.pi))
        elif text == "e":
            self._set_num(str(math.e))
        elif text == "x²":
            self._unary(lambda x: x * x, "sqr")
        elif text == "√":
            self._unary(math.sqrt, "√")
        elif text == "1/x":
            self._unary(lambda x: 1 / x if x != 0 else float("inf"), "1/")
        elif text in ("sin", "cos", "tan"):
            f = {"sin": math.sin, "cos": math.cos, "tan": math.tan}[text]
            self._unary(f, text)
        elif text in ("log", "ln"):
            f = math.log10 if text == "log" else math.log
            self._unary(f, text)
        elif text in ("(", ")"):
            self.expression += text
            self.display_expr += text
            self._update()

    def _set_num(self, val):
        if self.last_was_result:
            self.expression = val
            self.display_expr = val
            self.last_was_result = False
        else:
            self.expression += val
            self.display_expr += val
        self._update()

    def _digit(self, d):
        self.expression += d
        self.display_expr += d
        self._update()

    def _dot(self):
        parts = re.split(r"([+\-×÷()])", self.expression)
        current = parts[-1] if parts else ""
        if "." not in current:
            self.expression += "."
            self.display_expr += "."
            self._update()

    def _operator(self, op):
        if not self.expression:
            return
        # جایگزینی خودکار عملگر قبلی
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1]
            self.display_expr = self.display_expr.rstrip()[:-1].rstrip()
        sym = {"×": "*", "÷": "/"}.get(op, op)
        self.expression += sym
        self.display_expr += f" {op} "
        self._update()
        self.last_was_result = False

    def _equal(self):
        if not self.expression:
            return
        try:
            expr = self.expression.replace("×", "*").replace("÷", "/")
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                elif abs(result) < 1e-10:
                    result = 0
                else:
                    result = round(result, 10)
            self.history_label.configure(text=self.display_expr + " =")
            self.expression = str(result)
            self.display_expr = str(result)
            self.last_was_result = True
        except ZeroDivisionError:
            self.display_expr = "Error: ÷0"
            self.expression = ""
            self.last_was_result = True
        except Exception:
            self.display_expr = "Error"
            self.expression = ""
            self.last_was_result = True
        self._update()

    def _clear(self):
        self.expression = ""
        self.display_expr = ""
        self.history_label.configure(text="")
        self.last_was_result = False
        self._update()

    def _backspace(self):
        if self.last_was_result or "Error" in self.display_expr:
            self._clear()
            return
        if not self.expression:
            return
        self.expression = self.expression[:-1]
        self.display_expr = self.display_expr[:-1]
        self._update()

    def _negate(self):
        try:
            if not self.expression:
                return
            val = -float(self.expression)
            self.expression = str(val)
            self.display_expr = str(val)
            self._update()
        except:
            pass

    def _percent(self):
        try:
            if not self.expression:
                return
            val = float(self.expression) / 100
            self.expression = str(val)
            self.display_expr = str(val)
            self._update()
        except:
            pass

    def _unary(self, func, symbol):
        try:
            val = float(self.expression)
            res = func(val)
            if isinstance(res, float):
                if res.is_integer():
                    res = int(res)
                elif abs(res) < 1e-10:
                    res = 0
                else:
                    res = round(res, 10)
            self.history_label.configure(text=f"{symbol}({self.display_expr})")
            self.expression = str(res)
            self.display_expr = str(res)
            self.last_was_result = True
            self._update()
        except:
            self.display_expr = "Error"
            self.expression = ""
            self.last_was_result = True
            self._update()

    def _memory(self, op):
        try:
            val = float(self.expression) if self.expression else 0
            if op == "M+":
                self.memory += val
            elif op == "M-":
                self.memory -= val
            elif op == "MC":
                self.memory = 0
            elif op == "MR":
                self.expression = str(self.memory)
                self.display_expr = str(self.memory)
                if float(self.memory).is_integer():
                    self.display_expr = str(int(self.memory))
                    self.expression = self.display_expr
                self._update()
        except:
            pass

    def _update(self):
        text = self.display_expr if self.display_expr else "0"
        self.main_display.configure(text=text)

    def _bind_keys(self):
        self.bind("<Key>", self._on_key)
        self.bind("<Return>", lambda e: self._equal())
        self.bind("<BackSpace>", lambda e: self._backspace())
        self.bind("<Escape>", lambda e: self._clear())
        self.bind("<Delete>", lambda e: self._clear())

    def _on_key(self, event):
        c = event.char
        if c in "0123456789":
            self._digit(c)
        elif c in "+-*/":
            self._operator(c.replace("*", "×").replace("/", "÷"))
        elif c == ".":
            self._dot()
        elif c == "\r":
            self._equal()
        elif c == "\x08":
            self._backspace()
        elif c == "\x1b":
            self._clear()
        elif c == "(":
            self.expression += "("
            self.display_expr += "("
            self._update()
        elif c == ")":
            self.expression += ")"
            self.display_expr += ")"
            self._update()


if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
