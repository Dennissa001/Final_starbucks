# tarjetas.py
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import qrcode

# ----------------------------
# Archivos JSON
# ----------------------------
CLIENTES_FILE = "clientes.json"
TARJETAS_FILE = "tarjetas.json"
PEDIDOS_FILE = "pedidos.json"
MENU_FILE = "menu.json"
PROMOS_FILE = "promos.json"

# ----------------------------
# Inicializar session_state
# ----------------------------
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "tarjeta_info" not in st.session_state:
    st.session_state.tarjeta_info = {}

# ----------------------------
# Funciones JSON
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
def generar_qr(texto, nombre_archivo):
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(texto)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    img_qr.save(nombre_archivo)
    return nombre_archivo

def tarjeta_existe(nombre_cliente):
    tarjetas = cargar_json(TARJETAS_FILE)
    for t in tarjetas:
        if t["cliente"] == nombre_cliente:
            return t
    return None

def crear_tarjeta(nombre_cliente, dni, celular, envio_opcion, sede, banco):
    tarjetas = cargar_json(TARJETAS_FILE)
    tarjeta_id = len(tarjetas) + 1
    fecha_creacion = datetime.now().strftime("%d/%m/%Y")

    # ---------------- Tarjeta Delante ----------------
    img_delante = Image.new('RGB', (600, 300), color=(30, 100, 160))
    draw = ImageDraw.Draw(img_delante)
    fnt = ImageFont.load_default()
    draw.text((20, 20), f"Starbucks Card", font=fnt, fill=(255,255,255))
    draw.text((20, 60), f"Cliente: {nombre_cliente}", font=fnt, fill=(255,255,255))
    draw.text((20, 90), f"DNI: {dni[-4:].rjust(len(dni), '*')}", font=fnt, fill=(255,255,255))
    draw.text((20, 120), f"Celular: {celular[-4:].rjust(len(celular), '*')}", font=fnt, fill=(255,255,255))
    draw.text((20, 150), f"Método: {envio_opcion}", font=fnt, fill=(255,255,255))
    if envio_opcion == "Recoger en sede":
        fecha_recogida = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        draw.text((20, 180), f"Sede: {sede} - Fecha: {fecha_recogida}", font=fnt, fill=(255,255,255))
    else:
        draw.text((20, 180), f"Dirección: {st.session_state.tarjeta_info.get('direccion','')}", font=fnt, fill=(255,255,255))
    draw.text((20, 210), f"Banco afiliado: {banco}", font=fnt, fill=(255,255,255))

    # QR
    qr_path = f"qr_tarjeta_{tarjeta_id}.png"
    generar_qr(f"ID:{tarjeta_id}|Cliente:{nombre_cliente}", qr_path)
    qr_img = Image.open(qr_path)
    img_delante.paste(qr_img, (450, 180))

    archivo_delante = f"tarjeta_{tarjeta_id}_delante.png"
    img_delante.save(archivo_delante)

    # ---------------- Tarjeta Atrás ----------------
    img_atras = Image.new('RGB', (600, 300), color=(100, 100, 100))
    draw = ImageDraw.Draw(img_atras)
    draw.text((20, 20), "Starbucks Card - Atrás", font=fnt, fill=(255,255,255))
    draw.text((20, 60), f"ID de tarjeta: {tarjeta_id}", font=fnt, fill=(255,255,255))
    draw.text((20, 90), f"Banco afiliado: {banco}", font=fnt, fill=(255,255,255))
    draw.text((20, 120), "Gracias por usar Starbucks!", font=fnt, fill=(255,255,255))
    archivo_atras = f"tarjeta_{tarjeta_id}_atras.png"
    img_atras.save(archivo_atras)

    # ---------------- Guardar en JSON ----------------
    tarjeta_data = {
        "id": tarjeta_id,
        "cliente": nombre_cliente,
        "dni": dni,
        "celular": celular,
        "envio_opcion": envio_opcion,
        "sede": sede,
        "banco": banco,
        "fecha_creacion": fecha_creacion,
        "archivo_delante": archivo_delante,
        "archivo_atras": archivo_atras,
        "qr": qr_path,
        "puntos": 5  # Puntos iniciales al generar tarjeta
    }
    tarjetas.append(tarjeta_data)
    guardar_json(TARJETAS_FILE, tarjetas)
    return tarjeta_data

# ----------------------------
# Funciones de pedidos
# ----------------------------
def mostrar_menu():
    menu = cargar_json(MENU_FILE)
    return menu

def hacer_pedido(cliente, items, banco):
    pedidos = cargar_json(PEDIDOS_FILE)
    pedido_id = len(pedidos) + 1
    total = sum(item["precio"] for item in items)
    fecha_pedido = datetime.now().strftime("%d/%m/%Y %H:%M")
    pedidos.append({
        "id": pedido_id,
        "cliente": cliente["nombre"],
        "items": items,
        "total": total,
        "banco": banco,
        "fecha": fecha_pedido
    })
    guardar_json(PEDIDOS_FILE, pedidos)

    # Actualizar puntos en tarjeta
    tarjetas = cargar_json(TARJETAS_FILE)
    for t in tarjetas:
        if t["cliente"] == cliente["nombre"]:
            puntos_ganados = int(total // 10)
            t["puntos"] += puntos_ganados
            guardar_json(TARJETAS_FILE, tarjetas)
            break
    return pedido_id, total, fecha_pedido, puntos_ganados

# ----------------------------
# Promociones
# ----------------------------
def mostrar_promos():
    promos = cargar_json(PROMOS_FILE)
    if not promos:
        st.info("No hay promociones disponibles")
        return

    st.subheader("🎉 Promociones disponibles")

    # Mostrar en filas de 3 columnas
    col = st.columns(3)
    for i, promo in enumerate(promos):
        imagen_path = promo.get("imagen", "")
        with col[i % 3]:
            if os.path.exists(imagen_path):
                st.image(imagen_path, width=200)
            else:
                st.image("promos/placeholder.png", width=200)  # Imagen genérica si no hay
            st.markdown(f"**{promo['nombre']}**")
            st.write(promo['descripcion'])


# ----------------------------
# Interfaz Streamlit
# ----------------------------
st.title("☕ Sistema Starbucks Avanzado")

# Sidebar acceso
opcion = st.sidebar.selectbox("Acceso", ["Login", "Registrar"])

# ----------------------------
# Registro
# ----------------------------
if opcion == "Registrar":
    st.subheader("Crear cuenta")
    nombre = st.text_input("Nombre completo")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if registrar_usuario(nombre, email, password):
            st.success("Usuario registrado. Ahora inicia sesión.")
        else:
            st.error("El email ya está registrado.")

# ----------------------------
# Login
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
    menu_opcion = st.radio("Elige una opción:", ["Tarjeta", "Realizar pedido", "Promociones", "Ver mis pedidos"])

    # ----------------------------
    # Tarjeta
    # ----------------------------
    if menu_opcion == "Tarjeta":
        tarjeta = tarjeta_existe(usuario_actual["nombre"])
        if tarjeta:
            # Ya tiene tarjeta
            st.image(tarjeta["archivo_delante"], caption="Tarjeta Delante")
            st.image(tarjeta["archivo_atras"], caption="Tarjeta Atrás")
            st.write(f"**Puntos acumulados:** {tarjeta['puntos']}")
            st.write("**Beneficios:** Obtén descuentos al acumular puntos")
        else:
            # Generar tarjeta
            st.write("🎫 Solicita tu tarjeta Starbucks")
            dni = st.text_input("DNI")
            celular = st.text_input("Número de celular")
            envio_opcion = st.selectbox("Método de entrega:", ["Recoger en sede", "Envío a domicilio"])
            st.session_state.tarjeta_info["envio_opcion"] = envio_opcion

            sede = ""
            if envio_opcion == "Recoger en sede":
                sede = st.selectbox("Selecciona la sede:", ["Lima Norte", "Lima Centro", "Miraflores", "San Isidro"])
                fecha_recogida = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
                st.info(f"Fecha estimada de recogida: {fecha_recogida}")
            else:
                direccion = st.text_input("Ingresa la dirección de envío")
                st.session_state.tarjeta_info["direccion"] = direccion

            banco = st.selectbox("Selecciona el banco afiliado:", ["BCP", "Interbank", "Scotiabank", "BBVA", "Otro"])

            if st.button("Generar tarjeta"):
                if dni and celular:
                    tarjeta_data = crear_tarjeta(usuario_actual["nombre"], dni, celular, envio_opcion, sede, banco)
                    st.success("Tarjeta generada con éxito! Has recibido 5 puntos iniciales.")
                    st.image(tarjeta_data["archivo_delante"], caption="Tarjeta Delante")
                    st.image(tarjeta_data["archivo_atras"], caption="Tarjeta Atrás")
                    st.write(f"**Puntos acumulados:** {tarjeta_data['puntos']}")
                    st.write("**Beneficios:** Obtén descuentos al acumular puntos")
                else:
                    st.error("Debes ingresar DNI y celular")

    # ----------------------------
    # Realizar pedido
    # ----------------------------
    elif menu_opcion == "Realizar pedido":
        st.write("🛒 Realiza tu pedido")
        menu = mostrar_menu()
        if menu:
            opciones = [f"{item['nombre']} - S/ {item['precio']}" for item in menu]
            seleccion = st.multiselect("Selecciona tus bebidas:", opciones)
            items_seleccionados = [menu[i] for i in range(len(menu)) if opciones[i] in seleccion]

            banco = st.selectbox("Selecciona el banco para pago:", ["BCP", "Interbank", "Scotiabank", "BBVA", "Otro"])

            if st.button("Enviar pedido"):
                if items_seleccionados:
                    pedido_id, total, fecha_pedido, puntos_ganados = hacer_pedido(usuario_actual, items_seleccionados, banco)
                    st.success(f"Pedido #{pedido_id} registrado. Total: S/ {total} - Fecha: {fecha_pedido}")
                    st.info(f"Puntos ganados en este pedido: {puntos_ganados}")
                else:
                    st.error("Selecciona al menos un item.")
        else:
            st.info("El menú está vacío.")

    # ----------------------------
    # Promociones
    # ----------------------------
    elif menu_opcion == "Promociones":
        mostrar_promos()

    # ----------------------------
    # Ver mis pedidos
    # ----------------------------
    elif menu_opcion == "Ver mis pedidos":
        pedidos = cargar_json(PEDIDOS_FILE)
        mis_pedidos = [p for p in pedidos if p["cliente"] == usuario_actual["nombre"]]
        if mis_pedidos:
            for p in mis_pedidos:
                st.write(f"Pedido #{p['id']} - Total: S/ {p['total']} - Fecha: {p['fecha']}")
                st.write(f"Banco: {p['banco']}")
                for i in p["items"]:
                    st.write(f"  - {i['nombre']} S/ {i['precio']}")
        else:
            st.info("No tienes pedidos registrados.")

