# tarjetas.py
import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ----------------------------
# Archivos JSON
# ----------------------------
CLIENTES_FILE = "clientes.json"
TARJETAS_FILE = "tarjetas.json"
PEDIDOS_FILE = "pedidos.json"
MENU_FILE = "menu.json"

# ----------------------------
# Inicializar session_state
# ----------------------------
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# ----------------------------
# Funciones para manejar JSON
# ----------------------------
def cargar_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file, "r") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------
# Funciones de usuario
# ----------------------------
def registrar_usuario(nombre, email, password):
    clientes = cargar_json(CLIENTES_FILE)
    if any(c["email"] == email for c in clientes):
        return False
    clientes.append({"nombre": nombre, "email": email, "password": password})
    guardar_json(CLIENTES_FILE, clientes)
    return True

def login_usuario(email, password):
    clientes = cargar_json(CLIENTES_FILE)
    for cliente in clientes:
        if cliente["email"] == email and cliente["password"] == password:
            return cliente
    return None

# ----------------------------
# Funciones de tarjeta
# ----------------------------
def generar_tarjeta(nombre_cliente):
    tarjetas = cargar_json(TARJETAS_FILE)
    tarjeta_id = len(tarjetas) + 1
    # Crear imagen simple
    img = Image.new('RGB', (400, 200), color=(30, 100, 160))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    d.text((10, 80), f"Tarjeta Starbucks\nCliente: {nombre_cliente}\nID: {tarjeta_id}", font=fnt, fill=(255, 255, 255))
    archivo_tarjeta = f"tarjeta_{tarjeta_id}.png"
    img.save(archivo_tarjeta)
    
    tarjetas.append({"id": tarjeta_id, "cliente": nombre_cliente, "archivo": archivo_tarjeta, "fecha": str(datetime.now())})
    guardar_json(TARJETAS_FILE, tarjetas)
    return archivo_tarjeta

# ----------------------------
# Funciones de pedidos
# ----------------------------
def mostrar_menu():
    return cargar_json(MENU_FILE)

def hacer_pedido(cliente, items):
    pedidos = cargar_json(PEDIDOS_FILE)
    pedido_id = len(pedidos) + 1
    total = sum(item["precio"] for item in items)
    pedidos.append({
        "id": pedido_id,
        "cliente": cliente["nombre"],
        "items": items,
        "total": total,
        "fecha": str(datetime.now())
    })
    guardar_json(PEDIDOS_FILE, pedidos)
    return pedido_id, total

# ----------------------------
# Interfaz Streamlit
# ----------------------------
st.title("☕ Sistema Starbucks Simulado")

# Sidebar para login o registro
opcion = st.sidebar.selectbox("Acceso", ["Login", "Registrar"])

# ----------------------------
# Registro de usuario
# ----------------------------
if opcion == "Registrar":
    st.subheader("Crear cuenta")
    nombre = st.text_input("Nombre completo")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if registrar_usuario(nombre, email, password):
            st.success("Usuario registrado con éxito. Ahora inicia sesión.")
        else:
            st.error("El email ya está registrado.")

# ----------------------------
# Login de usuario
# ----------------------------
elif opcion == "Login":
    st.subheader("Iniciar sesión")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        usuario = login_usuario(email, password)
        if usuario:
            st.success(f"Bienvenido {usuario['nombre']}!")
            st.session_state.usuario_actual = usuario
        else:
            st.error("Email o contraseña incorrectos.")

# ----------------------------
# Funciones una vez logueado
# ----------------------------
if st.session_state.usuario_actual:
    usuario_actual = st.session_state.usuario_actual
    st.subheader(f"Bienvenido, {usuario_actual['nombre']}!")
    menu_opcion = st.radio("Elige una opción:", ["Solicitar tarjeta", "Ver menú", "Hacer pedido", "Ver mis pedidos"])

    if menu_opcion == "Solicitar tarjeta":
        st.write("🎫 Genera tu tarjeta Starbucks virtual")
        if st.button("Generar tarjeta"):
            archivo_tarjeta = generar_tarjeta(usuario_actual["nombre"])
            st.image(archivo_tarjeta, caption="Tu tarjeta virtual")

    elif menu_opcion == "Ver menú":
        st.write("📜 Menú de bebidas")
        menu = mostrar_menu()
        for item in menu:
            st.write(f"{item['nombre']} - S/ {item['precio']} ({item['categoria']})")

    elif menu_opcion == "Hacer pedido":
        st.write("🛒 Realiza tu pedido")
        menu = mostrar_menu()
        opciones = [f"{item['nombre']} - S/ {item['precio']}" for item in menu]
        seleccion = st.multiselect("Selecciona tus bebidas:", opciones)
        items_seleccionados = [menu[i] for i in range(len(menu)) if opciones[i] in seleccion]
        if st.button("Enviar pedido"):
            if items_seleccionados:
                pedido_id, total = hacer_pedido(usuario_actual, items_seleccionados)
                st.success(f"Pedido #{pedido_id} registrado. Total: S/ {total}")
            else:
                st.error("Selecciona al menos un item.")

    elif menu_opcion == "Ver mis pedidos":
        pedidos = cargar_json(PEDIDOS_FILE)
        mis_pedidos = [p for p in pedidos if p["cliente"] == usuario_actual["nombre"]]
        if mis_pedidos:
            for p in mis_pedidos:
                st.write(f"Pedido #{p['id']} - Total: S/ {p['total']} - Fecha: {p['fecha']}")
                for i in p["items"]:
                    st.write(f"  - {i['nombre']} S/ {i['precio']}")
        else:
            st.info("No tienes pedidos registrados.")

