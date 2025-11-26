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

if "tarjeta_info" not in st.session_state:
    st.session_state.tarjeta_info = {}

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
def generar_tarjeta_visual(nombre_cliente, dni, celular):
    tarjetas = cargar_json(TARJETAS_FILE)
    tarjeta_id = len(tarjetas) + 1
    img = Image.new('RGB', (400, 200), color=(30, 100, 160))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    d.text((10, 50), f"Tarjeta Starbucks\nCliente: {nombre_cliente}\nDNI: {dni}\nCelular: {celular}\nID: {tarjeta_id}", font=fnt, fill=(255, 255, 255))
    archivo_tarjeta = f"tarjeta_{tarjeta_id}.png"
    img.save(archivo_tarjeta)
    
    tarjetas.append({
        "id": tarjeta_id,
        "cliente": nombre_cliente,
        "dni": dni,
        "celular": celular,
        "archivo": archivo_tarjeta,
        "fecha": str(datetime.now()),
        "tarjeta_info": st.session_state.tarjeta_info
    })
    guardar_json(TARJETAS_FILE, tarjetas)
    return archivo_tarjeta

# ----------------------------
# Funciones de pedidos
# ----------------------------
def mostrar_menu():
    menu = cargar_json(MENU_FILE)
    return menu

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

# Sidebar acceso
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
# Funciones después de login
# ----------------------------
if st.session_state.usuario_actual:
    usuario_actual = st.session_state.usuario_actual
    st.subheader(f"Bienvenido, {usuario_actual['nombre']}!")
    menu_opcion = st.radio("Elige una opción:", ["Solicitar tarjeta", "Ver menú", "Realizar pedido", "Ver mis pedidos"])

    # ----------------------------
    # Solicitar tarjeta paso a paso
    # ----------------------------
    if menu_opcion == "Solicitar tarjeta":
        st.write("🎫 Solicita tu tarjeta Starbucks")
        nombre_cliente = usuario_actual["nombre"]
        dni = st.text_input("DNI")
        celular = st.text_input("Número de celular")
        envio_opcion = st.selectbox("¿Deseas envío o recoger en sede?", ["Recoger en sede", "Envío a domicilio"])
        if envio_opcion == "Envío a domicilio":
            direccion = st.text_input("Ingresa la dirección de envío")
            st.session_state.tarjeta_info["direccion"] = direccion
        st.session_state.tarjeta_info["envio_opcion"] = envio_opcion

        if st.button("Generar tarjeta"):
            if dni and celular:
                archivo_tarjeta = generar_tarjeta_visual(nombre_cliente, dni, celular)
                st.success("Tarjeta generada con éxito!")
                st.image(archivo_tarjeta, caption="Tu tarjeta virtual")
            else:
                st.error("Debes ingresar DNI y celular")

    # ----------------------------
    # Ver menú
    # ----------------------------
    elif menu_opcion == "Ver menú":
        st.write("📜 Menú de bebidas")
        menu = mostrar_menu()
        if menu:
            st.table([{"Nombre": i["nombre"], "Precio": f"S/ {i['precio']}", "Categoría": i["categoria"]} for i in menu])
        else:
            st.info("El menú está vacío.")

    # ----------------------------
    # Realizar pedido
    # ----------------------------
    elif menu_opcion == "Realizar pedido":
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

    # ----------------------------
    # Ver mis pedidos
    # ----------------------------
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

