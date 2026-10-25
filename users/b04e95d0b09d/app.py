st.title("🛍️ Catálogo Rápido")
st.markdown("Explora, busca y filtra elementos de forma rápida y sencilla.")

# Inicializar elementos de ejemplo si no existen
if "productos" not in st.session_state:
    st.session_state.productos = [
        {"id": 1, "nombre": "Zapatillas Deportivas", "categoria": "Calzado", "precio": 49.99, "seccion": "Destacados", "imagen": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"},
        {"id": 2, "nombre": "Reloj Inteligente", "categoria": "Tecnología", "precio": 89.99, "seccion": "Novedades", "imagen": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"},
        {"id": 3, "nombre": "Mochila Urbana", "categoria": "Accesorios", "precio": 34.50, "seccion": "Destacados", "imagen": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
        {"id": 4, "nombre": "Auriculares Inalámbricos", "categoria": "Tecnología", "precio": 59.00, "seccion": "Novedades", "imagen": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
        {"id": 5, "nombre": "Gafas de Sol", "categoria": "Accesorios", "precio": 25.00, "seccion": "Destacados", "imagen": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400"},
        {"id": 6, "nombre": "Camiseta de Algodón", "categoria": "Ropa", "precio": 15.99, "seccion": "Novedades", "imagen": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=400"},
    ]

# Menú superior horizontal con pills
st.markdown("### 🧭 Menú Principal")
menu_seleccionado = st.pills(
    "Secciones",
    ["Ver todo", "Destacados", "Novedades"],
    default="Ver todo",
    key="menu_horizontal"
)

st.divider()

# Barra de filtros
col_busqueda, col_categoria = st.columns([2, 1])

with col_busqueda:
    texto_busqueda = st.text_input("🔍 Buscar elemento...", key="input_busqueda")

with col_categoria:
    categorias_disponibles = ["Todas"] + sorted(list(set(p["categoria"] for p in st.session_state.productos)))
    categoria_seleccionada = st.selectbox("📂 Filtrar por categoría", categorias_disponibles, key="select_categoria")

st.divider()

# Filtrado de productos
productos_filtrados = st.session_state.productos

# 1. Filtro por menú superior
if menu_seleccionado == "Destacados":
    productos_filtrados = [p for p in productos_filtrados if p["seccion"] == "Destacados"]
elif menu_seleccionado == "Novedades":
    productos_filtrados = [p for p in productos_filtrados if p["seccion"] == "Novedades"]

# 2. Filtro por categoría
if categoria_seleccionada != "Todas":
    productos_filtrados = [p for p in productos_filtrados if p["categoria"] == categoria_seleccionada]

# 3. Filtro por texto de búsqueda
if texto_busqueda:
    texto_limpio = texto_busqueda.lower()
    productos_filtrados = [p for p in productos_filtrados if texto_limpio in p["nombre"].lower() or texto_limpio in p["categoria"].lower()]

# Mostrar resultados en cuadrícula
if productos_filtrados:
    st.caption(f"Mostrando {len(productos_filtrados)} elemento(s)")
    
    # Creamos filas de 3 columnas
    for i in range(0, len(productos_filtrados), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(productos_filtrados):
                prod = productos_filtrados[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.image(prod["imagen"], use_container_width=True)
                        st.subheader(prod["nombre"])
                        st.write(f"🏷️ **Categoría:** {prod['categoria']}")
                        st.write(f"✨ **Sección:** {prod['seccion']}")
                        st.markdown(f"### 💰 {prod['precio']:.2f} €")
                        if st.button("🛒 Ver detalles", key=f"btn_{prod['id']}"):
                            st.toast(f"Has seleccionado: {prod['nombre']}")
else:
    st.info("No se han encontrado elementos que coincidan con tu búsqueda.")
