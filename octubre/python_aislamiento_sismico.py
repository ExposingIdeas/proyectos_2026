import tkinter as tk
from tkinter import ttk, messagebox
import math

# ============================================================
# 规范参数表（E.030 简化取值，实际项目需按最新版核对）
# ============================================================
# 土壤参数 S, Tp, TL（按 E.030 表 N°3 / N°4 的常见取值）
SOIL_PARAMS = {
    "S0": {"S": 0.80, "Tp": 0.30, "TL": 3.0},
    "S1": {"S": 1.00, "Tp": 0.40, "TL": 2.5},
    "S2": {"S": 1.05, "Tp": 0.60, "TL": 2.0},
    "S3": {"S": 1.10, "Tp": 1.00, "TL": 1.6},
    "S4": {"S": 1.15, "Tp": 1.60, "TL": 1.2},
}

# 阻尼折减系数 B_M 的简化插值（占位，需替换为 E.031 附表）
def calc_BM(beta_eff):
    """beta_eff 为等效阻尼比（小数，如 0.15 表示 15%）"""
    beta_pct = beta_eff * 100.0
    # 简化分段线性插值（仅用于演示，非规范正式值）
    table = [(2, 0.8), (5, 1.0), (10, 1.2), (20, 1.5), (30, 1.7), (40, 1.9)]
    if beta_pct <= table[0][0]:
        return table[0][1]
    if beta_pct >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= beta_pct <= x1:
            return y0 + (y1 - y0) * (beta_pct - x0) / (x1 - x0)
    return 1.0

def calc_C(T, Tp, TL):
    """E.030 地震放大系数 C"""
    if T < 0.2 * Tp:
        return 1.0 + 7.5 * (T / Tp)   # 新版 E.030 可能包含此短周期段
    elif T < Tp:
        return 2.5
    elif T < TL:
        return 2.5 * (Tp / T)
    else:
        return 2.5 * (Tp * TL / T ** 2)

# ============================================================
# 核心计算函数
# ============================================================
def compute_isolation(P_kN, K_min, K_max, beta, Z, U, S, Tp, TL):
    """
    返回：(工况名, D_M(m), T_M(s), V_b(kN))
    """
    g = 9.81
    m = P_kN / g  # 质量 (t)
    
    results = []
    for label, K in [("下限刚度", K_min), ("上限刚度", K_max)]:
        # 等效周期 T_M = 2π√(M/K)
        T_M = 2.0 * math.pi * math.sqrt(m / K)
        C_val = calc_C(T_M, Tp, TL)
        # S_aM = 1.5 * Z * U * C * S * g  （E.031 对 SMC 的要求，1.5 为系数）
        SaM = 1.5 * Z * U * C_val * S * g  # m/s²
        BM = calc_BM(beta)
        # D_M = SaM * T_M² / (4π² * B_M)
        D_M = (SaM * T_M ** 2) / (4.0 * math.pi ** 2 * BM)
        V_b = K * D_M  # 隔震层剪力 (kN)
        results.append((label, D_M, T_M, V_b))
    return results

# ============================================================
# GUI
# ============================================================
class IsolationCalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Calculadora de Aislamiento Sísmico (RNE E.031) — 简化版")
        root.geometry("720x620")
        root.resizable(False, False)

        main = ttk.Frame(root, padding=12)
        main.pack(fill="both", expand=True)

        # --- 输入区 ---
        input_frame = ttk.LabelFrame(main, text="Datos de entrada", padding=10)
        input_frame.pack(fill="x", pady=5)

        # 使用 grid 布局
        row = 0
        def add_entry(parent, label, default, r, c, width=14):
            ttk.Label(parent, text=label).grid(row=r, column=c*2, sticky="e", padx=4, pady=3)
            var = tk.StringVar(value=str(default))
            ttk.Entry(parent, textvariable=var, width=width).grid(row=r, column=c*2+1, sticky="w", padx=4, pady=3)
            return var

        self.var_P = add_entry(input_frame, "Peso total P (kN):", 8000, 0, 0)
        self.var_Z = add_entry(input_frame, "Factor zona Z:", 0.45, 0, 1)
        self.var_U = add_entry(input_frame, "Factor uso U:", 1.0, 1, 0)
        self.var_Kmin = add_entry(input_frame, "K_min (kN/m):", 4000, 1, 1)
        self.var_Kmax = add_entry(input_frame, "K_max (kN/m):", 6000, 2, 0)
        self.var_beta = add_entry(input_frame, "Amortiguamiento β (ej. 0.15):", 0.15, 2, 1)

        # 土壤类型下拉
        ttk.Label(input_frame, text="Perfil de suelo:").grid(row=3, column=0, sticky="e", padx=4, pady=3)
        self.soil_var = tk.StringVar(value="S2")
        soil_combo = ttk.Combobox(input_frame, textvariable=self.soil_var,
                                  values=list(SOIL_PARAMS.keys()), width=8, state="readonly")
        soil_combo.grid(row=3, column=1, sticky="w", padx=4, pady=3)

        # --- 按钮 ---
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Calcular", command=self.on_calculate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpiar resultados", command=self.clear_results).pack(side="left", padx=5)

        # --- 结果区 ---
        result_frame = ttk.LabelFrame(main, text="Resultados (envolvente)", padding=10)
        result_frame.pack(fill="both", expand=True, pady=5)

        columns = ("Caso", "T_M (s)", "D_M (m)", "V_b (kN)")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="x")

        self.summary_label = ttk.Label(result_frame, text="", foreground="darkgreen", font=("Arial", 10, "bold"))
        self.summary_label.pack(pady=10)

        # --- 提示 ---
        note = ttk.Label(main, text="⚠ 本工具为教学演示，B_M 表与最新 E.030 参数需按官方规范替换后方可用于实际工程。",
                         foreground="gray", wraplength=680)
        note.pack(pady=5)

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.summary_label.config(text="")

    def on_calculate(self):
        try:
            P = float(self.var_P.get())
            Z = float(self.var_Z.get())
            U = float(self.var_U.get())
            K_min = float(self.var_Kmin.get())
            K_max = float(self.var_Kmax.get())
            beta = float(self.var_beta.get())
            soil = self.soil_var.get()
            sp = SOIL_PARAMS[soil]
            S, Tp, TL = sp["S"], sp["Tp"], sp["TL"]
        except ValueError:
            messagebox.showerror("错误", "请检查输入是否为有效数字。")
            return
        except KeyError:
            messagebox.showerror("错误", "土壤类型无效。")
            return

        if P <= 0 or K_min <= 0 or K_max <= 0 or K_min >= K_max:
            messagebox.showerror("错误", "P、K 必须为正，且 K_min < K_max。")
            return

        self.clear_results()
        res = compute_isolation(P, K_min, K_max, beta, Z, U, S, Tp, TL)

        for label, D_M, T_M, V_b in res:
            self.tree.insert("", "end", values=(label, f"{T_M:.3f}", f"{D_M:.4f}", f"{V_b:.1f}"))

        # 包络：取 D_M 较大者和 V_b 较大者
        D_env = max(r[1] for r in res)
        V_env = max(r[3] for r in res)
        self.summary_label.config(
            text=f"包络设计值：D_M = {D_env:.4f} m   |   V_b = {V_env:.1f} kN"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = IsolationCalculatorApp(root)
    root.mainloop()