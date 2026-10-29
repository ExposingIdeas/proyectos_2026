import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import re

class CASSpreadsheet:
    def __init__(self, root, rows=12, cols=6):
        self.root = root
        self.root.title("Hoja de Cálculo CAS en Python")
        self.rows = rows
        self.cols = cols

        # Almacenamiento
        self.raw_data = {}        # Guarda fórmulas: {'A1': '=x**2'}
        self.evaluated_data = {}  # Guarda resultados evaluados: {'A1': x**2}
        self.cells = {}           # Widgets Entry
        self.current_cell = None

        # Configuración CAS
        self.init_cas_env()

        # Construir Interfaz
        self.create_widgets()

    def init_cas_env(self):
        """Inicializa variables simbólicas y funciones de SymPy."""
        self.cas_symbols = sp.symbols('x y z t a b c')
        self.cas_env = {s.name: s for s in self.cas_symbols}
        for attr in dir(sp):
            if not attr.startswith("_"):
                self.cas_env[attr] = getattr(sp, attr)

    def col_to_letter(self, col_idx):
        return chr(ord('A') + col_idx)

    def create_widgets(self):
        # Barra superior de fórmulas
        top_frame = ttk.Frame(self.root, padding=5)
        top_frame.pack(fill=tk.X)

        self.cell_label = ttk.Label(top_frame, text="--", width=5, font=("Arial", 10, "bold"))
        self.cell_label.pack(side=tk.LEFT, padx=5)

        self.formula_var = tk.StringVar()
        self.formula_entry = ttk.Entry(top_frame, textvariable=self.formula_var, font=("Consolas", 11))
        self.formula_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.formula_entry.bind("<Return>", lambda e: self.on_formula_submit())

        # Grid de Celdas
        grid_frame = ttk.Frame(self.root, padding=5)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezados de Columna (A, B, C...)
        for c in range(self.cols):
            lbl = ttk.Label(grid_frame, text=self.col_to_letter(c), anchor="center", font=("Arial", 9, "bold"))
            lbl.grid(row=0, column=c+1, sticky="nsew", padx=1, pady=1)

        # Encabezados de Fila y Celdas
        for r in range(self.rows):
            row_lbl = ttk.Label(grid_frame, text=str(r+1), anchor="center", font=("Arial", 9, "bold"))
            row_lbl.grid(row=r+1, column=0, sticky="nsew", padx=2, pady=1)

            for c in range(self.cols):
                cell_id = f"{self.col_to_letter(c)}{r+1}"
                entry = ttk.Entry(grid_frame, font=("Arial", 10), justify="left")
                entry.grid(row=r+1, column=c+1, sticky="nsew", padx=1, pady=1)

                # Eventos: FocusIn (mostrar fórmula), FocusOut y Return (guardar y recalcular)
                entry.bind("<FocusIn>", lambda e, cid=cell_id: self.on_cell_focus_in(cid))
                entry.bind("<FocusOut>", lambda e, cid=cell_id: self.on_cell_focus_out(cid))
                entry.bind("<Return>", lambda e, cid=cell_id: self.on_cell_return(cid))

                self.cells[cell_id] = entry
                self.raw_data[cell_id] = ""

        # Distribución elástica
        for c in range(self.cols + 1):
            grid_frame.columnconfigure(c, weight=1)
        for r in range(self.rows + 1):
            grid_frame.rowconfigure(r, weight=1)

    def on_cell_focus_in(self, cell_id):
        self.current_cell = cell_id
        self.cell_label.config(text=cell_id)
        
        # Al entrar en la celda, mostrar la fórmula original para edición
        raw_val = self.raw_data.get(cell_id, "")
        self.formula_var.set(raw_val)
        
        self.cells[cell_id].delete(0, tk.END)
        self.cells[cell_id].insert(0, raw_val)

    def on_cell_focus_out(self, cell_id):
        # Guardar automáticamente al perder el foco (clic en otra celda)
        new_val = self.cells[cell_id].get().strip()
        self.raw_data[cell_id] = new_val
        self.recalculate_all()

    def on_cell_return(self, cell_id):
        # Al pulsar Enter, guardar y quitar el foco de edición
        new_val = self.cells[cell_id].get().strip()
        self.raw_data[cell_id] = new_val
        self.root.focus_set()  # Esto activa <FocusOut> y recalcula de forma segura

    def on_formula_submit(self):
        if self.current_cell:
            self.raw_data[self.current_cell] = self.formula_var.get().strip()
            self.root.focus_set()

    def eval_cell(self, cell_id, visiting=None):
        if visiting is None:
            visiting = set()

        if cell_id in visiting:
            raise RecursionError("Ciclo detectado")

        visiting.add(cell_id)
        raw = self.raw_data.get(cell_id, "").strip()

        if not raw:
            return ""

        # Si no comienza con '=', intentamos evaluar como expresión directa o valor simbólico
        if not raw.startswith("="):
            try:
                return sp.sympify(raw, locals=self.cas_env)
            except Exception:
                return raw

        expr_str = raw[1:]

        # Normalizar nombres de celdas a mayúsculas (ej: a1 -> A1)
        expr_str = re.sub(r'\b[a-zA-Z][0-9]+\b', lambda m: m.group(0).upper(), expr_str)

        local_scope = dict(self.cas_env)

        # Buscar celdas referenciadas
        referenced_cells = re.findall(r'\b[A-Z][0-9]+\b', expr_str)
        for ref in referenced_cells:
            if ref in self.raw_data and self.raw_data[ref] != "":
                val = self.eval_cell(ref, visiting.copy())
                local_scope[ref] = val
            else:
                local_scope[ref] = 0

        try:
            return eval(expr_str, {"__builtins__": {}}, local_scope)
        except Exception as e:
            return f"#ERROR"

    def recalculate_all(self):
        # 1. Evaluar todas las celdas
        for cell_id in self.cells:
            try:
                self.evaluated_data[cell_id] = self.eval_cell(cell_id)
            except Exception:
                self.evaluated_data[cell_id] = "#ERROR"

        # 2. Refrescar la pantalla con los resultados evaluados
        for cell_id, entry in self.cells.items():
            if cell_id != self.current_cell or self.root.focus_get() != entry:
                val = self.evaluated_data.get(cell_id, "")
                entry.delete(0, tk.END)
                entry.insert(0, str(val))

        # Mantener la barra superior actualizada
        if self.current_cell:
            self.formula_var.set(self.raw_data.get(self.current_cell, ""))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("850x450")
    app = CASSpreadsheet(root)
    root.mainloop()