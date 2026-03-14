import streamlit as st
import pandas as pd
import datetime
import pickle
import os

# --- CLASE ORIGINAL ADAPTADA ---
class SheetInventory:
    def __init__(self, sheet_name, full_sheet_length=13.0):
        self.sheet_name = sheet_name
        self.full_sheet_length = full_sheet_length
        self.full_sheets_count = 0
        self.cuts = []
        self.min_cut_length_to_save = 1.5

    def add_full_sheets(self, quantity):
        if quantity > 0:
            self.full_sheets_count += quantity
            return True
        return False

# --- FUNCIONES DE PERSISTENCIA ---
INVENTORY_FILE = 'inventory.pkl'

def save_data(inv_dict):
    with open(INVENTORY_FILE, 'wb') as f:
        pickle.dump(inv_dict, f)

def load_data():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'rb') as f:
            return pickle.load(f)
    return {
        "T101 galvanizada": SheetInventory("T101 galvanizada"),
        "T101 zincalum": SheetInventory("T101 zincalum"),
        "Acanalada galvanizada": SheetInventory("Acanalada galvanizada"),
        "Acanalada zincalum": SheetInventory("Acanalada zincalum")
    }

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Control de Stock - Chapas", layout="wide")
st.title("📦 Gestión de Inventario de Chapas")

# Cargar inventario al iniciar
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data()

# --- BARRA LATERAL: AGREGAR STOCK ---
with st.sidebar:
    st.header("➕ Cargar Nuevo Stock")
    tipo_chapa = st.selectbox("Selecciona tipo", list(st.session_state.inventory.keys()))
    cantidad = st.number_input("Cantidad de chapas (13m)", min_value=1, value=1)
    if st.button("Añadir al Inventario"):
        st.session_state.inventory[tipo_chapa].add_full_sheets(cantidad)
        save_data(st.session_state.inventory)
        st.success(f"Añadidas {cantidad} unidades a {tipo_chapa}")

# --- CUERPO PRINCIPAL: CORTES ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("✂️ Realizar Pedido de Corte")
    chapa_pedido = st.selectbox("Tipo de chapa para cortar", list(st.session_state.inventory.keys()), key="corte_tipo")
    largo_pedido = st.number_input("Largo necesario (metros)", min_value=0.1, max_value=13.0, step=0.1)
    
    if st.button("Procesar Corte"):
        inv_obj = st.session_state.inventory[chapa_pedido]
        # Lógica de búsqueda de recortes
        suitable_cuts = [c for c in inv_obj.cuts if c >= largo_pedido]
        
        if suitable_cuts:
            selected_cut = min(suitable_cuts)
            inv_obj.cuts.remove(selected_cut)
            sobrante = selected_cut - largo_pedido
            if sobrante >= inv_obj.min_cut_length_to_save:
                inv_obj.cuts.append(round(sobrante, 2))
            st.balloons()
            st.info(f"Se usó un RECORTE de {selected_cut}m. Sobrante: {sobrante:.2f}m")
        elif inv_obj.full_sheets_count > 0:
            inv_obj.full_sheets_count -= 1
            sobrante = inv_obj.full_sheet_length - largo_pedido
            if sobrante >= inv_obj.min_cut_length_to_save:
                inv_obj.cuts.append(round(sobrante, 2))
            st.success(f"Corte realizado de CHAPA NUEVA. Sobrante: {sobrante:.2f}m")
        else:
            st.error("❌ No hay stock disponible (ni recortes ni chapas completas).")
        
        save_data(st.session_state.inventory)

with col2:
    st.subheader("📊 Estado Actual")
    for nombre, datos in st.session_state.inventory.items():
        with st.expander(f"{nombre} ({datos.full_sheets_count} enteras)"):
            st.write(f"**Recortes disponibles:** {sorted(datos.cuts, reverse=True)}")
