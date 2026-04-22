import socket
import tkinter as tk
from tkinter import ttk, messagebox

# ================= CONFIG =================
HOST = "136.119.140.224"   
PORT = 5005

# ================= GIRLY THEME =================
BG = "#fff0f6"
CARD = "#ffe3ec"
TEXT = "#4a4a4a"
ACCENT1 = "#ff85a2"
ACCENT2 = "#b28dff"
WARN = "#ffd166"

# ================= SOCKET =================
def enviar(msg):
    try:
        s = socket.socket()
        s.connect((HOST, PORT))
        s.send((msg + "\n").encode())
        resp = s.recv(1024).decode()
        s.close()
        log(resp)
        return resp
    except:
        log("Error de conexión")
        return "Error de conexión"

# ================= LOGS =================
def log(texto):
    log_box.insert(tk.END, texto + "\n")
    log_box.see(tk.END)

# ================= ACCIONES =================
def crear_producto():
    msg = f"PRODUCTO,{p_nombre.get()},{p_precio.get()},{p_stock.get()}"
    enviar(msg)
    messagebox.showinfo("Neptuno", "Producto registrado 💗")
    cargar_productos()

def crear_pedido():
    msg = f"PEDIDO,{p_cliente.get()},{p_id.get()},{p_cantidad.get()}"
    enviar(msg)
    messagebox.showinfo("Neptuno", "Pedido registrado 💖")
    cargar_productos()

# ================= INVENTARIO =================
def cargar_productos():
    try:
        import mysql.connector

        conn = mysql.connector.connect(
            host=HOST,
            user="appuser",
            password="1234",
            database="neptuno"
        )

        cur = conn.cursor()
        cur.execute("SELECT IdProducto, NombreProducto, UnidadesEnExistencia FROM productos")
        rows = cur.fetchall()

        for i in tree.get_children():
            tree.delete(i)

        for r in rows:
            tree.insert("", "end", values=r)

        conn.close()
        log("Inventario actualizado ✨")

    except Exception as e:
        log(f"Error BD: {e}")

# ================= UI =================
root = tk.Tk()
root.title("Neptuno System 💗")
root.geometry("900x650")
root.configure(bg=BG)

# ===== TÍTULO =====
tk.Label(
    root,
    text="NEPTUNO SYSTEM 💖",
    font=("Segoe UI", 22, "bold"),
    bg=BG,
    fg="#d63384"
).pack(pady=10)

# ===== PRODUCTOS =====
frame1 = tk.LabelFrame(root, text="Productos 💗", bg=CARD, fg=TEXT)
frame1.pack(fill="x", padx=10, pady=5)

p_nombre = tk.Entry(frame1)
p_precio = tk.Entry(frame1)
p_stock = tk.Entry(frame1)

tk.Label(frame1, text="Nombre", bg=CARD, fg=TEXT).grid(row=0, column=0)
p_nombre.grid(row=0, column=1)

tk.Label(frame1, text="Precio", bg=CARD, fg=TEXT).grid(row=0, column=2)
p_precio.grid(row=0, column=3)

tk.Label(frame1, text="Stock", bg=CARD, fg=TEXT).grid(row=0, column=4)
p_stock.grid(row=0, column=5)

tk.Button(
    frame1,
    text="Crear Producto 💕",
    bg=ACCENT1,
    fg="white",
    relief="flat",
    command=crear_producto
).grid(row=0, column=6, padx=10)

# ===== PEDIDOS =====
frame2 = tk.LabelFrame(root, text="Pedidos 💖", bg=CARD, fg=TEXT)
frame2.pack(fill="x", padx=10, pady=5)

p_cliente = tk.Entry(frame2)
p_id = tk.Entry(frame2)
p_cantidad = tk.Entry(frame2)

tk.Label(frame2, text="Cliente", bg=CARD, fg=TEXT).grid(row=0, column=0)
p_cliente.grid(row=0, column=1)

tk.Label(frame2, text="ID Producto", bg=CARD, fg=TEXT).grid(row=0, column=2)
p_id.grid(row=0, column=3)

tk.Label(frame2, text="Cantidad", bg=CARD, fg=TEXT).grid(row=0, column=4)
p_cantidad.grid(row=0, column=5)

tk.Button(
    frame2,
    text="Registrar Pedido 💕",
    bg=ACCENT2,
    fg="white",
    relief="flat",
    command=crear_pedido
).grid(row=0, column=6, padx=10)

# ===== INVENTARIO =====
frame3 = tk.LabelFrame(root, text="Inventario ✨", bg=CARD, fg=TEXT)
frame3.pack(fill="both", expand=True, padx=10, pady=5)

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
    background=CARD,
    fieldbackground=CARD,
    foreground=TEXT,
    rowheight=25
)

style.configure("Treeview.Heading",
    background="#ffd6e7",
    foreground="#4a4a4a"
)

tree = ttk.Treeview(frame3, columns=("ID", "Nombre", "Stock"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Nombre", text="Producto")
tree.heading("Stock", text="Stock")
tree.pack(fill="both", expand=True)

tk.Button(
    frame3,
    text="Refrescar Inventario 💫",
    bg=WARN,
    fg="black",
    relief="flat",
    command=cargar_productos
).pack(pady=5)

# ===== LOGS =====
frame4 = tk.LabelFrame(root, text="Logs 💬", bg=CARD, fg=TEXT)
frame4.pack(fill="both", expand=True, padx=10, pady=5)

log_box = tk.Text(frame4, bg="#fff5f8", fg="#d63384", insertbackground="black")
log_box.pack(fill="both", expand=True)

# ================= INIT =================
cargar_productos()
root.mainloop()