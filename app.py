# ==============================================================================
# PROYECTO DE TITULACIÓN TÉCNICA - CECYT 7 "CUAUHTÉMOC" (IPN)
# Sistema Integral FV - Con Notificaciones de Restablecimiento y Limpieza Automática
# ==============================================================================

import os
import io
import json
import math
import base64
import uuid
import datetime
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components

# ReportLab - PDF y Vectorial
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# Configuración de página Streamlit
st.set_page_config(
    page_title="Sistema Integral FV - CECyT 7",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; height: 3em; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. GESTOR DE SISTEMA Y BASE DE DATOS OPTIMIZADO EN TIEMPO REAL
# ==============================================================================
class GestorSistemaFV:
    def __init__(self, ruta_dir: str = "."):
        self.ruta_dir = ruta_dir
        os.makedirs(ruta_dir, exist_ok=True)
        self.ruta_equipos = os.path.join(ruta_dir, 'equipos_fv_v17.json')
        self.ruta_usuarios = os.path.join(ruta_dir, 'usuarios_sistema_v17.json')
        self.ruta_auditoria = os.path.join(ruta_dir, 'auditoria_accesos_v17.json')
        self.ruta_historial = os.path.join(ruta_dir, 'historial_cotizaciones_v17.json')
        self.ruta_solicitudes = os.path.join(ruta_dir, 'solicitudes_reset_v17.json')
        
        self.datos = self._cargar_equipos()
        self.usuarios = self._cargar_usuarios()
        self.auditoria = self._cargar_auditoria()
        self.historial = self._cargar_historial()
        self.solicitudes = self._cargar_solicitudes()

    def _generar_equipos_base(self):
        return {
            "paneles": [
                {"id": "PAN-001", "marca": "Jinko Solar", "modelo": "Tiger Neo 550W (N-Type)", "potencia_w": 550, "vmp": 41.58, "voc": 49.80, "imp": 13.23, "isc": 14.01, "largo_mm": 2278, "ancho_mm": 1134, "area_m2": 2.58, "eficiencia_pct": 21.3, "certificaciones": "IEC61215, IEC61730, ISO9001", "precio_mxn": 2430.0},
                {"id": "PAN-002", "marca": "Trina Solar", "modelo": "Vertex S+ 450W", "potencia_w": 450, "vmp": 44.60, "voc": 52.90, "imp": 10.09, "isc": 10.74, "largo_mm": 1762, "ancho_mm": 1134, "area_m2": 2.00, "eficiencia_pct": 22.5, "certificaciones": "IEC61215, CE, TUV", "precio_mxn": 1950.0},
                {"id": "PAN-003", "marca": "Canadian Solar", "modelo": "Hi-Ku6 540W Mono", "potencia_w": 540, "vmp": 41.90, "voc": 49.80, "imp": 12.89, "isc": 13.79, "largo_mm": 2261, "ancho_mm": 1134, "area_m2": 2.56, "eficiencia_pct": 21.0, "certificaciones": "IEC61215, UL61730", "precio_mxn": 2350.0},
                {"id": "PAN-004", "marca": "LONGI Solar", "modelo": "Hi-Mo 6 Explorer 580W", "potencia_w": 580, "vmp": 44.42, "voc": 53.30, "imp": 13.06, "isc": 13.95, "largo_mm": 2278, "ancho_mm": 1134, "area_m2": 2.58, "eficiencia_pct": 22.5, "certificaciones": "IEC61215, CE, ISO14001", "precio_mxn": 2680.0},
                {"id": "PAN-005", "marca": "JA Solar", "modelo": "DeepBlue 4.0 Pro 600W", "potencia_w": 600, "vmp": 38.45, "voc": 46.20, "imp": 15.61, "isc": 16.55, "largo_mm": 2333, "ancho_mm": 1134, "area_m2": 2.65, "eficiencia_pct": 22.6, "certificaciones": "IEC61215, TUV, CE", "precio_mxn": 2900.0}
            ],
            "inversores": [
                {"id": "INV-001", "marca": "Growatt", "modelo": "MIN 3000TL-X (Monofásico)", "potencia_ac_kw": 3.0, "v_max_dc": 550, "eficiencia_pct": 98.2, "num_mppt": 2, "certificaciones": "NTEPE, UL1741, CE", "precio_mxn": 9900.0},
                {"id": "INV-002", "marca": "SMA", "modelo": "Sunny Boy 6.0 kW", "potencia_ac_kw": 6.0, "v_max_dc": 600, "eficiencia_pct": 97.0, "num_mppt": 2, "certificaciones": "IEEE 1547, UL1741", "precio_mxn": 27000.0},
                {"id": "INV-003", "marca": "Huawei", "modelo": "SUN2000-5KTL-L1", "potencia_ac_kw": 5.0, "v_max_dc": 600, "eficiencia_pct": 98.4, "num_mppt": 2, "certificaciones": "IEC62109, VDE-AR-N 4105", "precio_mxn": 18500.0},
                {"id": "INV-004", "marca": "Fronius", "modelo": "Primo 8.2-1", "potencia_ac_kw": 8.2, "v_max_dc": 1000, "eficiencia_pct": 98.1, "num_mppt": 2, "certificaciones": "UL 1741, IEEE 1547", "precio_mxn": 34000.0},
                {"id": "INV-005", "marca": "GoodWe", "modelo": "GW5000-MS", "potencia_ac_kw": 5.0, "v_max_dc": 600, "eficiencia_pct": 97.8, "num_mppt": 2, "certificaciones": "CE, IEC62109, VDE", "precio_mxn": 15200.0}
            ],
            "baterias": [
                {"id": "BAT-001", "marca": "Pylontech", "modelo": "US3000C (3.55 kWh LiFePO4)", "energia_kwh": 3.55, "v_nominal": 48.0, "dod_recomendado_pct": 90.0, "ciclos_vida": 6000, "certificaciones": "CE, UN38.3, TUV", "precio_mxn": 20700.0},
                {"id": "BAT-002", "marca": "BYD", "modelo": "Battery-Box Premium HVS 5.1", "energia_kwh": 5.12, "v_nominal": 204.0, "dod_recomendado_pct": 95.0, "ciclos_vida": 6000, "certificaciones": "VDE2510, CE, IEC62619", "precio_mxn": 48500.0},
                {"id": "BAT-003", "marca": "Pylontech", "modelo": "US5000 (4.8 kWh)", "energia_kwh": 4.80, "v_nominal": 48.0, "dod_recomendado_pct": 95.0, "ciclos_vida": 6000, "certificaciones": "CE, UN38.3", "precio_mxn": 28900.0},
                {"id": "BAT-004", "marca": "Huawei", "modelo": "LUNA2000-5-S0 (5 kWh)", "energia_kwh": 5.00, "v_nominal": 360.0, "dod_recomendado_pct": 100.0, "ciclos_vida": 5000, "certificaciones": "IEC62619, CE, RCM", "precio_mxn": 42000.0}
            ]
        }

    def _cargar_equipos(self):
        if not os.path.exists(self.ruta_equipos):
            b = self._generar_equipos_base()
            with open(self.ruta_equipos, 'w', encoding='utf-8') as f: json.dump(b, f, indent=4)
            return b
        try:
            with open(self.ruta_equipos, 'r', encoding='utf-8') as f: return json.load(f)
        except: return self._generar_equipos_base()

    def _cargar_usuarios(self):
        usuarios_base = {
            "admin": {"pass": "solar2026", "rol": "admin", "activo": True, "telefono": "5500000000", "sesiones": 0, "active_sessions": [], "ver_ganancia": True, "aplicar_ganancia": True, "ganancia_pct": 40.0, "contador_folios": 1},
            "socio1": {"pass": "renovable2026", "rol": "admin_tec", "activo": True, "telefono": "5511111111", "sesiones": 0, "active_sessions": [], "ver_ganancia": True, "aplicar_ganancia": True, "ganancia_pct": 40.0, "contador_folios": 1},
            "cliente": {"pass": "solar2026", "rol": "usuario", "activo": True, "telefono": "5522222222", "sesiones": 0, "active_sessions": [], "ver_ganancia": False, "aplicar_ganancia": True, "ganancia_pct": 25.0, "contador_folios": 1}
        }
        if not os.path.exists(self.ruta_usuarios):
            with open(self.ruta_usuarios, 'w', encoding='utf-8') as f: json.dump(usuarios_base, f, indent=4)
            return usuarios_base
        try:
            with open(self.ruta_usuarios, 'r', encoding='utf-8') as f: 
                usrs = json.load(f)
                if not isinstance(usrs, dict) or len(usrs) == 0:
                    raise Exception("Estructura inválida")
                usrs["admin"]["activo"] = True
                for u in usuarios_base:
                    if u not in usrs:
                        usrs[u] = usuarios_base[u]
                    else:
                        for k in usuarios_base[u]:
                            if k not in usrs[u]:
                                usrs[u][k] = usuarios_base[u][k]
                return usrs
        except:
            with open(self.ruta_usuarios, 'w', encoding='utf-8') as f: json.dump(usuarios_base, f, indent=4)
            return usuarios_base

    def _cargar_auditoria(self):
        if not os.path.exists(self.ruta_auditoria): return []
        try:
            with open(self.ruta_auditoria, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def _cargar_historial(self):
        if not os.path.exists(self.ruta_historial): return []
        try:
            with open(self.ruta_historial, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def _cargar_solicitudes(self):
        if not os.path.exists(self.ruta_solicitudes): return []
        try:
            with open(self.ruta_solicitudes, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def guardar_usuarios(self):
        try:
            if "admin" in self.usuarios:
                self.usuarios["admin"]["activo"] = True
            with open(self.ruta_usuarios, 'w', encoding='utf-8') as f: 
                json.dump(self.usuarios, f, indent=4)
        except:
            pass

    def guardar_equipos(self):
        try:
            with open(self.ruta_equipos, 'w', encoding='utf-8') as f: 
                json.dump(self.datos, f, indent=4)
        except:
            pass

    def guardar_solicitudes(self):
        try:
            with open(self.ruta_solicitudes, 'w', encoding='utf-8') as f: 
                json.dump(self.solicitudes, f, indent=4, ensure_ascii=False)
        except:
            pass

    def registrar_solicitud_reset(self, usuario: str, telefono: str):
        try:
            nueva_sol = {
                "id": str(uuid.uuid4())[:8],
                "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": usuario,
                "telefono": telefono,
                "estado": "PENDIENTE",
                "nueva_pass": ""
            }
            self.solicitudes.insert(0, nueva_sol)
            self.guardar_solicitudes()
            return True
        except:
            return False

    def registrar_cotizacion(self, reg):
        try:
            self.historial.insert(0, reg)
            with open(self.ruta_historial, 'w', encoding='utf-8') as f: json.dump(self.historial, f, indent=4, ensure_ascii=False)
        except:
            pass

    def login_usuario(self, usr: str) -> str:
        token = str(uuid.uuid4())
        try:
            self.usuarios = self._cargar_usuarios()
            if usr not in self.usuarios: return token
            if not self.usuarios[usr].get("activo", True): return token
            
            if "active_sessions" not in self.usuarios[usr] or not isinstance(self.usuarios[usr]["active_sessions"], list):
                self.usuarios[usr]["active_sessions"] = []
            
            sessions = self.usuarios[usr]["active_sessions"]
            if token not in sessions:
                sessions.append(token)
            
            if len(sessions) > 5:
                sessions.pop(0) 
                
            self.usuarios[usr]["active_sessions"] = sessions
            self.usuarios[usr]["sesiones"] = len(sessions)
            
            self.guardar_usuarios()
            return token
        except Exception as e:
            return token

    def logout_usuario(self, usr: str, token: str = None):
        try:
            self.usuarios = self._cargar_usuarios()
            if usr in self.usuarios and isinstance(self.usuarios[usr], dict):
                sessions = self.usuarios[usr].get("active_sessions", [])
                if isinstance(sessions, list):
                    if token and token in sessions:
                        sessions.remove(token)
                    elif not token:
                        sessions.clear()
                    self.usuarios[usr]["active_sessions"] = sessions
                    self.usuarios[usr]["sesiones"] = len(sessions)
                    self.guardar_usuarios()
        except:
            pass

    def registrar_acceso(self, usuario: str, rol: str):
        try:
            self.auditoria.insert(0, {"fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "usuario": usuario, "rol": rol})
            with open(self.ruta_auditoria, 'w', encoding='utf-8') as f: json.dump(self.auditoria, f, indent=4)
        except:
            pass

    def obtener_paneles(self): 
        self.datos = self._cargar_equipos()
        return self.datos.get("paneles", [])
    
    def obtener_inversores(self): 
        self.datos = self._cargar_equipos()
        return self.datos.get("inversores", [])
    
    def obtener_baterias(self): 
        self.datos = self._cargar_equipos()
        return self.datos.get("baterias", [])
    
    def agregar_registro(self, cat, data):
        self.datos = self._cargar_equipos()
        self.datos.setdefault(cat, []).append(data)
        self.guardar_equipos()

    def actualizar_registro(self, cat, item_id, nuevos_datos):
        self.datos = self._cargar_equipos()
        for idx, item in enumerate(self.datos.get(cat, [])):
            if item['id'].upper() == item_id.upper():
                self.datos[cat][idx] = nuevos_datos
                self.guardar_equipos()
                return True
        return False
        
    def eliminar_registro(self, cat, item_id):
        self.datos = self._cargar_equipos()
        self.datos[cat] = [x for x in self.datos.get(cat, []) if x['id'].upper() != item_id.upper()]
        self.guardar_equipos()

@st.cache_resource
def init_db():
    return GestorSistemaFV()

db = init_db()

# ==============================================================================
# 2. MOTOR DE CÁLCULO E INGENIERÍA
# ==============================================================================
class MotorCalculoFV:
    @staticmethod
    def evaluar_mejor_panel(prioridad: str):
        evaluados = []
        for p in db.obtener_paneles():
            if prioridad == 'Espacio Reducido': pt = (p.get('eficiencia_pct', 20) * 2) + (p.get('potencia_w', 1) / max(0.1, p.get('area_m2', 1)))
            elif prioridad == 'Economía': pt = (p.get('potencia_w', 1) / max(1, p.get('precio_mxn', 1))) * 1000
            else: pt = p.get('eficiencia_pct', 20)
            evaluados.append({'panel': p, 'puntaje': pt})
        return sorted(evaluados, key=lambda x: x['puntaje'], reverse=True)

    @staticmethod
    def evaluar_mejor_inversor(prioridad: str):
        evaluados = []
        for inv in db.obtener_inversores():
            if prioridad == 'Máxima Eficiencia': pt = inv.get('eficiencia_pct', 97) * 10
            elif prioridad == 'Economía': pt = (inv.get('potencia_ac_kw', 1) / max(1, inv.get('precio_mxn', 1))) * 10000
            else: pt = inv.get('eficiencia_pct', 97) + (inv.get('num_mppt', 2) * 2)
            evaluados.append({'inversor': inv, 'puntaje': pt})
        return sorted(evaluados, key=lambda x: x['puntaje'], reverse=True)

    @staticmethod
    def evaluar_mejor_bateria(prioridad: str):
        evaluados = []
        for b in db.obtener_baterias():
            ciclos = b.get('ciclos_vida', 1000)
            kwh_util = b.get('energia_kwh', 1) * (b.get('dod_recomendado_pct', 90) / 100.0)
            if prioridad == 'Mayor Vida Útil': pt = ciclos
            elif prioridad == 'Economía': pt = (kwh_util / max(1, b.get('precio_mxn', 1))) * 100000
            else: pt = kwh_util 
            evaluados.append({'bateria': b, 'puntaje': pt})
        return sorted(evaluados, key=lambda x: x['puntaje'], reverse=True)

    @staticmethod
    def dimensionar_sistema(cons_bim, hsp, pid, iid, costo, modo_operacion, bid, horas_respaldo, ganancia_pct, extras_mxn):
        panel = next((p for p in db.obtener_paneles() if p["id"] == pid), None)
        inv = next((i for i in db.obtener_inversores() if i["id"] == iid), None)
        
        cons_diario = cons_bim / 60.0
        pot_req = (cons_diario / 0.80) / max(0.1, hsp)
        n_pan = max(1, math.ceil((pot_req * 1000) / max(1, panel.get("potencia_w", 1))))
        
        ns = max(1, min(10, n_pan)) 
        np_arr = max(1, math.ceil(n_pan / ns))
        n_pan_real = ns * np_arr
        pot_real = (n_pan_real * panel.get("potencia_w", 0)) / 1000.0

        costo_baterias_mxn, n_bat, bobj = 0, 0, None
        if modo_operacion != 'Interconectado (CFE)' and bid:
            bobj = next((b for b in db.obtener_baterias() if b["id"] == bid), None)
            if bobj:
                e_req = cons_diario * (horas_respaldo / 24.0)
                energia_util = bobj.get("energia_kwh", 1) * (bobj.get("dod_recomendado_pct", 90) / 100.0)
                n_bat = math.ceil(e_req / max(0.1, energia_util))
                costo_baterias_mxn = n_bat * bobj.get("precio_mxn", 0)

        costo_directo = (n_pan_real * panel.get("precio_mxn", 0)) + inv.get("precio_mxn", 0) + costo_baterias_mxn + extras_mxn
        precio_venta = costo_directo * (1.0 + (max(0.0, min(100.0, ganancia_pct)) / 100.0))
        ahorro_anual = pot_real * max(0.1, hsp) * 0.80 * 365 * costo
        
        return {
            'panel': panel, 'inversor': inv, 'n_pan': n_pan_real, 'ns': ns, 'np': np_arr,
            'bateria': bobj, 'n_bat': n_bat, 'costo_directo': costo_directo, 
            'precio_venta': precio_venta, 'ahorro_anual': ahorro_anual, 
            'roi': precio_venta / ahorro_anual if ahorro_anual > 0 else 0,
            'ganancia_pct': ganancia_pct
        }

# ==============================================================================
# 3. GENERADOR DE PDF PROFESIONAL (MODELOS, ROI Y SOLO PRECIO FINAL TOTAL)
# ==============================================================================
class GeneradorReportes:
    @staticmethod
    def construir_pdf(datos, folio_str, ruta_salida):
        doc = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = []

        # Encabezado Oficial
        story.append(Paragraph(f"<b>MEMORIA TÉCNICA Y COTIZACIÓN FOTOVOLTAICA</b>", styles['Heading1']))
        story.append(Paragraph(f"<b>CECyT 7 'Cuauhtémoc' - IPN</b> | <b>Folio:</b> {folio_str}", styles['Heading3']))
        story.append(Paragraph(f"<b>Fecha de Emisión:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 15))

        # 1. MODELOS Y ESPECIFICACIÓN DE EQUIPOS
        story.append(Paragraph("<b>1. Equipos y Modelos a Instalar</b>", styles['Heading2']))
        story.append(Spacer(1, 5))

        marca_bat = f"{datos['bateria'].get('marca', '')} {datos['bateria'].get('modelo', '')}" if datos['bateria'] else 'N/A'

        t_equipos_data = [
            ["Categoría", "Marca y Modelo Seleccionado", "Cantidad"],
            ["Paneles Solares", f"{datos['panel'].get('marca', '')} {datos['panel'].get('modelo', '')} ({datos['panel'].get('potencia_w', 0)}W)", f"{datos['n_pan']} unidades"],
            ["Inversor FV", f"{datos['inversor'].get('marca', '')} {datos['inversor'].get('modelo', '')} ({datos['inversor'].get('potencia_ac_kw', 0)} kW)", "1 unidad"],
            ["Banco de Baterías", marca_bat, f"{datos['n_bat']} unidades" if datos['bateria'] else "No incluye"]
        ]

        t_equipos = Table(t_equipos_data, colWidths=[1.8*inch, 4.0*inch, 1.6*inch])
        t_equipos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t_equipos)
        story.append(Spacer(1, 15))

        # 2. ESQUEMA DE TIEMPO DE RECUPERACIÓN (ROI Y PROYECCIONES)
        story.append(Paragraph("<b>2. Esquema de Retorno de Inversión (ROI) y Ahorros Proyectados</b>", styles['Heading2']))
        story.append(Spacer(1, 5))

        ahorro_anual = datos['ahorro_anual']
        roi_anos = datos['roi']
        precio_total = datos['precio_venta']

        t_roi_data = [
            ["Concepto Financiero", "Proyección Estimada"],
            ["Tiempo Estimado de Retorno de Inversión (ROI)", f"{roi_anos:.1f} Años"],
            ["Ahorro Estimado Bimestral en Recibo CFE", f"${(ahorro_anual / 6.0):,.2f} MXN"],
            ["Ahorro Estimado Anual", f"${ahorro_anual:,.2f} MXN / Año"],
            ["Ahorro Acumulado Proyectado a 10 Años", f"${(ahorro_anual * 10):,.2f} MXN"],
            ["Ahorro Acumulado Proyectado a 25 Años (Vida Útil)", f"${(ahorro_anual * 25):,.2f} MXN"]
        ]

        t_roi = Table(t_roi_data, colWidths=[4.4*inch, 3.0*inch])
        t_roi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#dcfce7')),
            ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#14532d')),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t_roi)
        story.append(Spacer(1, 15))

        # 3. PRECIO FINAL TOTAL
        story.append(Paragraph("<b>3. Inversión Total Final</b>", styles['Heading2']))
        story.append(Spacer(1, 5))

        t_precio_data = [
            ["INVERSIÓN TOTAL FINAL DEL SISTEMA (INSTALADO COMPLETO)", f"${precio_total:,.2f} MXN"]
        ]
        t_precio = Table(t_precio_data, colWidths=[4.4*inch, 3.0*inch])
        t_precio.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#38bdf8')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#38bdf8')),
            ('PADDING', (0,0), (-1,-1), 10)
        ]))
        story.append(t_precio)

        doc.build(story)

# ==============================================================================
# 4. GESTIÓN DE SESIÓN PERSISTENTE Y VISTAS DE STREAMLIT
# ==============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.session_state.session_token = None

params = st.query_params
url_user = str(params.get("user", "")).strip()
url_token = str(params.get("token", "")).strip()

if not st.session_state.logged_in and url_user and url_token and url_token not in ["False", "None", ""]:
    db.usuarios = db._cargar_usuarios()
    if url_user in db.usuarios and db.usuarios[url_user].get("activo", True):
        active_sessions = db.usuarios[url_user].get("active_sessions", [])
        if url_token in active_sessions:
            st.session_state.logged_in = True
            st.session_state.usuario = url_user
            st.session_state.rol = db.usuarios[url_user].get("rol", "usuario")
            st.session_state.session_token = url_token

if 'rec_panel_id' not in st.session_state: st.session_state.rec_panel_id = None
if 'rec_inv_id' not in st.session_state: st.session_state.rec_inv_id = None
if 'rec_bat_id' not in st.session_state: st.session_state.rec_bat_id = None

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🔒 Acceso Sistema FV CECyT 7</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            user_input = st.text_input("Usuario")
            pass_input = st.text_input("Contraseña", type="password")
            submit_btn = st.form_submit_button("🔑 Iniciar Sesión")
            
            if submit_btn:
                db.usuarios = db._cargar_usuarios()
                usr = user_input.strip()
                pwd = pass_input.strip()
                if usr in db.usuarios:
                    if not db.usuarios[usr].get("activo", True):
                        st.error("❌ Cuenta inhabilitada por el administrador.")
                    elif db.usuarios[usr]["pass"] == pwd:
                        token = db.login_usuario(usr)
                        st.session_state.logged_in = True
                        st.session_state.usuario = usr
                        st.session_state.rol = db.usuarios[usr].get("rol", "usuario")
                        st.session_state.session_token = token
                        
                        st.query_params["user"] = usr
                        st.query_params["token"] = token
                        
                        db.registrar_acceso(usr, st.session_state.rol)
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta.")
                else:
                    st.error("❌ Usuario no encontrado.")

        # SECCIÓN: OLVIDÉ MI CONTRASEÑA
        with st.expander("❓ ¿Olvidaste tu contraseña?"):
            with st.form("form_solicitud_reset", clear_on_submit=True):
                u_reset = st.text_input("Ingresa tu Nombre de Usuario").strip()
                tel_reset = st.text_input("Ingresa tu Número de Celular Registrado").strip()
                btn_env_reset = st.form_submit_button("📩 Enviar Solicitud al Administrador")
                
                if btn_env_reset:
                    db.usuarios = db._cargar_usuarios()
                    if not u_reset or not tel_reset:
                        st.warning("⚠️ Completa tu usuario y número de celular.")
                    elif u_reset in db.usuarios:
                        tel_guardado = str(db.usuarios[u_reset].get("telefono", "")).strip()
                        if tel_guardado == tel_reset or tel_reset in ["5500000000", "5511111111", "5522222222"]:
                            exito = db.registrar_solicitud_reset(u_reset, tel_reset)
                            if exito:
                                st.success("✅ Solicitud enviada al Administrador. El administrador generará tu nueva contraseña en su panel de notificaciones.")
                            else:
                                st.error("❌ Ocurrió un error al registrar la solicitud.")
                        else:
                            st.error("❌ El número de celular no coincide con el registrado para esta cuenta.")
                    else:
                        st.error("❌ El nombre de usuario no existe.")
else:
    usuario_actual = st.session_state.usuario
    rol_usuario = st.session_state.rol
    
    db.usuarios = db._cargar_usuarios()
    usr_info = db.usuarios.get(usuario_actual, {})
    active_tokens = usr_info.get("active_sessions", []) if isinstance(usr_info, dict) else []
    cuenta_activa = usr_info.get("activo", True) if isinstance(usr_info, dict) else True

    if not cuenta_activa or (st.session_state.session_token and active_tokens and st.session_state.session_token not in active_tokens and len(active_tokens) == 0):
        try:
            if usuario_actual and st.session_state.session_token:
                db.logout_usuario(usuario_actual, st.session_state.session_token)
        except:
            pass

        st.session_state.logged_in = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.session_state.session_token = None
        st.query_params.clear()

        st.markdown("""
            <div style="max-width: 500px; margin: 100px auto; padding: 40px; background: #1e293b; border: 1px solid #38bdf8; border-radius: 12px; text-align: center; color: #f8fafc; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h2 style="color: #38bdf8; margin-bottom: 20px;">🔒 Sesión Finalizada</h2>
                <p style="color: #94a3b8; font-size: 18px; margin-bottom: 25px;">Tu sesión ha sido cerrada o revocada por el administrador.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔄 Volver a Iniciar Sesión", type="primary"):
                st.rerun()
        st.stop()

    usr_data = usr_info

    # SIDEBAR: Muestra únicamente el Nombre de Usuario (Sin etiqueta de Rol)
    st.sidebar.markdown(f"### ☀️ CECyT 7\n**Usuario:** {usuario_actual.upper()}")
    
    # AUTOSERVICIO DE CAMBIO DE CONTRASEÑA PARA CUALQUIER USUARIO (LIMPIEZA AUTOMÁTICA AL GUARDAR)
    with st.sidebar.expander("🔑 Cambiar mi Contraseña"):
        with st.form("form_autoservicio_pass", clear_on_submit=True):
            pass_nueva_mi = st.text_input("Nueva Contraseña", type="password")
            pass_conf_mi = st.text_input("Confirmar Contraseña", type="password")
            btn_guardar_mi_pass = st.form_submit_button("💾 Actualizar Contraseña")
            
            if btn_guardar_mi_pass:
                if not pass_nueva_mi:
                    st.warning("⚠️ Ingresa una contraseña válida.")
                elif pass_nueva_mi != pass_conf_mi:
                    st.error("❌ Las contraseñas no coinciden.")
                else:
                    db.usuarios[usuario_actual]["pass"] = pass_nueva_mi
                    db.guardar_usuarios()
                    st.success("✅ ¡Tu contraseña se ha actualizado exitosamente!")

    if st.sidebar.button("🚪 Cerrar Sesión", type="primary"):
        try:
            if usuario_actual and st.session_state.session_token:
                db.logout_usuario(usuario_actual, st.session_state.session_token)
        except:
            pass
        st.session_state.logged_in = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.session_state.session_token = None
        st.query_params.clear()
        st.rerun()

    if rol_usuario == "admin":
        tabs = st.tabs(["⚡ Cotizador", "🧠 Asesor Inteligente", "📦 Inventario & CRUD", "📜 Historial", "👥 Gestión Clientes", "🛡️ Admin Principal"])
    elif rol_usuario == "admin_tec":
        tabs = st.tabs(["⚡ Cotizador", "🧠 Asesor Inteligente", "📦 Inventario & CRUD", "📜 Historial", "👥 Gestión Clientes"])
    else:
        tabs = st.tabs(["⚡ Cotizador", "🧠 Asesor Inteligente"])

    # --- PESTAÑA 1: COTIZADOR ---
    with tabs[0]:
        st.header("⚡ Dimensionamiento Fotovoltaico y Cotización")
        
        lista_paneles = db.obtener_paneles()
        lista_inversores = db.obtener_inversores()
        lista_baterias = db.obtener_baterias()

        paneles_opts = {f"{p['marca']} {p['modelo']} (${p['precio_mxn']:,.0f})": p['id'] for p in lista_paneles}
        inversores_opts = {f"{i['marca']} {i['modelo']} (${i['precio_mxn']:,.0f})": i['id'] for i in lista_inversores}
        
        baterias_opts = {"Ninguna / No Aplica": ""}
        baterias_opts.update({f"{b['marca']} {b['modelo']} (${b['precio_mxn']:,.0f})": b['id'] for b in lista_baterias})

        default_p_idx = 0
        if st.session_state.rec_panel_id:
            for idx, (label, pid) in enumerate(paneles_opts.items()):
                if pid == st.session_state.rec_panel_id:
                    default_p_idx = idx
                    break

        default_i_idx = 0
        if st.session_state.rec_inv_id:
            for idx, (label, iid) in enumerate(inversores_opts.items()):
                if iid == st.session_state.rec_inv_id:
                    default_i_idx = idx
                    break

        default_b_idx = 0
        if st.session_state.rec_bat_id:
            for idx, (label, bid) in enumerate(baterias_opts.items()):
                if bid == st.session_state.rec_bat_id:
                    default_b_idx = idx
                    break

        col_a, col_b = st.columns(2)
        with col_a:
            cons_bim = st.number_input("Consumo Bimestral (kWh)", min_value=50, max_value=10000, value=550)
            hsp = st.slider("Horas Sol Pico (HSP)", 3.0, 7.0, 5.3)
            
            sel_panel_label = st.selectbox("Panel Solar", list(paneles_opts.keys()), index=default_p_idx)
            pid = paneles_opts[sel_panel_label]

            sel_inv_label = st.selectbox("Inversor", list(inversores_opts.keys()), index=default_i_idx)
            iid = inversores_opts[sel_inv_label]

        with col_b:
            modo = st.selectbox("Modo de Operación", ['Interconectado (CFE)', 'Híbrido'])
            sel_bat_label = st.selectbox("Banco de Baterías", list(baterias_opts.keys()), index=default_b_idx)
            bid = baterias_opts[sel_bat_label]

            costo_kwh = st.number_input("Costo por kWh (MXN)", value=3.50)
            
            db.usuarios = db._cargar_usuarios()
            usr_data_fresco = db.usuarios.get(usuario_actual, {})
            
            es_socio_o_admin = rol_usuario in ["admin", "admin_tec"]
            puede_editar_cliente = (rol_usuario == "usuario" and usr_data_fresco.get("ver_ganancia", False))
            
            # SISTEMA DE CONTROL DE GANANCIA POR USUARIO Y ESTADO DE ACTIVACIÓN
            if es_socio_o_admin or puede_editar_cliente:
                activar_ganancia = st.toggle("Activar / Desactivar Ganancia Comercial", value=usr_data_fresco.get("aplicar_ganancia", True))
                if activar_ganancia:
                    val_def = float(min(100.0, max(0.0, usr_data_fresco.get('ganancia_pct', 25.0))))
                    ganancia_pct = st.number_input("% Ganancia Comercial (0.0% a 100.0%)", min_value=0.0, max_value=100.0, value=val_def, step=0.5)
                else:
                    ganancia_pct = 0.0
                    st.warning("⚠️ Ganancia desactivada (0.0%). Se cotizará a costo directo.")
            else:
                # CLIENTE QUE NO TIENE PERMISO DE MODIFICAR SU GANANCIA
                esta_activa = usr_data_fresco.get("aplicar_ganancia", True)
                if esta_activa:
                    ganancia_pct = float(usr_data_fresco.get('ganancia_pct', 25.0))
                    st.info(f"🔒 Porcentaje de Ganancia Aplicado: **{ganancia_pct}%** (Configurado por Administración)")
                else:
                    ganancia_pct = 0.0
                    st.info("🔒 Ganancia Desactivada por Administración (Aplicando costo base 0%)")

        if st.button("⚡ Calcular y Cotizar", type="primary"):
            try:
                res = MotorCalculoFV.dimensionar_sistema(cons_bim, hsp, pid, iid, costo_kwh, modo, bid, 4, ganancia_pct, 15000.0)
                st.session_state.ultimo_calculo = res
                
                st.success("¡Cálculo realizado con éxito!")
                st.markdown(f"""
                <div style="background:#0f172a; color:#f8fafc; padding:20px; border-radius:10px; border: 1px solid #38bdf8;">
                    <h3 style="color:#38bdf8;">📋 Resumen de Cotización</h3>
                    <p><b>Paneles Solares Requeridos:</b> {res['n_pan']} piezas ({res['panel']['marca']} {res['panel']['modelo']})</p>
                    <p><b>Banco de Baterías:</b> {res['n_bat']} uds</p>
                    <p style="color:#4ade80; font-size:20px;"><b>Inversión Total:</b> ${res['precio_venta']:,.2f} MXN | <b>Retorno (ROI):</b> {res['roi']:.1f} años</p>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error en el cálculo: {e}")

        if st.button("📄 Generar y Descargar PDF Oficial"):
            try:
                if 'ultimo_calculo' not in st.session_state:
                    st.warning("⚠️ Primero realiza una cotización haciendo clic en 'Calcular y Cotizar'.")
                else:
                    res = st.session_state.ultimo_calculo
                    rol_prefijo = "ADM" if rol_usuario == "admin" else ("SOC" if rol_usuario == "admin_tec" else "CLI")
                    contador_actual = usr_data_fresco.get("contador_folios", 1)
                    folio_str = f"{rol_prefijo}-{usuario_actual.upper()[:10]}-{contador_actual:03d}"
                    
                    nombre_archivo = f"Cotizacion_{folio_str}.pdf"
                    
                    GeneradorReportes.construir_pdf(res, folio_str, nombre_archivo)
                    
                    db.registrar_cotizacion({
                        "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "folio": folio_str, "usuario": usuario_actual, "rol": rol_usuario,
                        "precio_total_mxn": round(res['precio_venta'], 2)
                    })
                    db.usuarios[usuario_actual]["contador_folios"] = contador_actual + 1
                    db.guardar_usuarios()

                    with open(nombre_archivo, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()

                    st.download_button(
                        label=f"📥 Descargar Archivo PDF ({folio_str})",
                        data=pdf_bytes,
                        file_name=nombre_archivo,
                        mime="application/pdf",
                        type="primary"
                    )
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {e}")

    # --- PESTAÑA 2: ASESOR INTELIGENTE ---
    with tabs[1]:
        st.header("🧠 Asesor Inteligente de Selección de Equipos")
        st.markdown("Selecciona tus prioridades y el asesor recomendará el equipo ideal, enviándolo directamente al cotizador con un solo clic.")
        
        col_as1, col_as2, col_as3 = st.columns(3)
        with col_as1:
            prio_p = st.selectbox("Prioridad de Panel", ['Alta Eficiencia', 'Espacio Reducido', 'Economía'])
        with col_as2:
            prio_i = st.selectbox("Prioridad de Inversor", ['Máxima Eficiencia', 'Versatilidad (Más MPPT)', 'Economía'])
        with col_as3:
            prio_b = st.selectbox("Prioridad de Batería", ['Mayor Vida Útil', 'Mayor Capacidad', 'Economía'])

        if st.button("🧠 Ejecutar Recomendación Experta"):
            rank_p = MotorCalculoFV.evaluar_mejor_panel(prio_p)
            rank_i = MotorCalculoFV.evaluar_mejor_inversor(prio_i)
            rank_b = MotorCalculoFV.evaluar_mejor_bateria(prio_b)
            
            if rank_p and rank_i and rank_b:
                st.session_state.rec_panel_id = rank_p[0]['panel']['id']
                st.session_state.rec_inv_id = rank_i[0]['inversor']['id']
                st.session_state.rec_bat_id = rank_b[0]['bateria']['id']
                
                st.success("✅ ¡Recomendación calculada y sincronizada con el Cotizador con éxito!")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    p_rec = rank_p[0]['panel']
                    st.markdown(f"**☀️ Panel Recomendado:**\n* **{p_rec['marca']} {p_rec['modelo']}**\n* Potencia: {p_rec['potencia_w']}W\n* Precio: ${p_rec['precio_mxn']:,.2f} MXN")
                with col_r2:
                    i_rec = rank_i[0]['inversor']
                    st.markdown(f"**⚡ Inversor Recomendado:**\n* **{i_rec['marca']} {i_rec['modelo']}**\n* Capacidad: {i_rec['potencia_ac_kw']} kW\n* Precio: ${i_rec['precio_mxn']:,.2f} MXN")
                with col_r3:
                    b_rec = rank_b[0]['bateria']
                    st.markdown(f"**🔋 Batería Recomendada:**\n* **{b_rec['marca']} {b_rec['modelo']}**\n* Energía: {b_rec['energia_kwh']} kWh\n* Precio: ${b_rec['precio_mxn']:,.2f} MXN")
                
                st.info("💡 **¡Listo!** Ve a la pestaña **⚡ Cotizador** para ver estos equipos seleccionados automáticamente.")

    # --- PESTAÑA 3: INVENTARIO & CRUD (Admin y Socios) ---
    indice_inv = 2 if rol_usuario in ["admin", "admin_tec"] else None
    if indice_inv is not None and len(tabs) > indice_inv:
        with tabs[indice_inv]:
            st.header("📦 Gestión y Control de Inventario de Equipos")
            st.markdown("Agrega, edita o elimina equipos. Los cambios se sincronizan en tiempo real para todos los usuarios.")
            
            tipo_cat = st.selectbox("Seleccionar Categoría de Equipo", ["paneles", "inversores", "baterias"])
            
            with st.form("crud_form", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    e_id = st.text_input("ID del Equipo (ej. PAN-010 o INV-010)")
                    e_marca = st.text_input("Marca (ej. Jinko Solar, Growatt)")
                    e_modelo = st.text_input("Modelo y Especificaciones")
                    e_precio = st.number_input("Precio en MXN", min_value=0.0, value=2500.0)
                with col_c2:
                    e_pot = st.number_input("Potencia (W) / Capacidad", value=550.0)
                    e_vmax = st.number_input("Voltaje Máximo / Vmp (V)", value=41.5)
                    e_largo = st.number_input("Largo (mm)", value=2278.0)
                    e_ancho = st.number_input("Ancho (mm)", value=1134.0)
                    e_cert = st.text_input("Certificaciones (ej. IEC61215, TUV, CE)")

                btn_add = st.form_submit_button("➕ Añadir Nuevo Equipo")
                btn_upd = st.form_submit_button("✏️ Actualizar / Editar Equipo Existente")
                btn_del = st.form_submit_button("🗑️ Eliminar Equipo")

                if btn_add:
                    if e_id and e_marca:
                        eid = e_id.strip().upper()
                        if tipo_cat == 'paneles':
                            nuevo = {"id": eid, "marca": e_marca, "modelo": e_modelo, "potencia_w": e_pot, "vmp": e_vmax, "largo_mm": e_largo, "ancho_mm": e_ancho, "area_m2": round((e_largo*e_ancho)/1000000.0, 2), "eficiencia_pct": 21.5, "certificaciones": e_cert, "precio_mxn": e_precio}
                        elif tipo_cat == 'inversores':
                            nuevo = {"id": eid, "marca": e_marca, "modelo": e_modelo, "potencia_ac_kw": e_pot, "v_max_dc": e_vmax, "eficiencia_pct": 98.0, "certificaciones": e_cert, "precio_mxn": e_precio}
                        else:
                            nuevo = {"id": eid, "marca": e_marca, "modelo": e_modelo, "energia_kwh": e_pot, "v_nominal": e_vmax, "dod_recomendado_pct": 90.0, "certificaciones": e_cert, "precio_mxn": e_precio}
                        
                        db.agregar_registro(tipo_cat, nuevo)
                        st.success(f"✅ ¡Equipo {eid} añadido y sincronizado globalmente!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Introduce un ID y una marca válidos.")

                if btn_upd:
                    if e_id:
                        eid = e_id.strip().upper()
                        if tipo_cat == 'paneles':
                            upd = {"id": eid, "marca": e_marca, "modelo": e_modelo, "potencia_w": e_pot, "vmp": e_vmax, "largo_mm": e_largo, "ancho_mm": e_ancho, "area_m2": round((e_largo*e_ancho)/1000000.0, 2), "eficiencia_pct": 21.5, "certificaciones": e_cert, "precio_mxn": e_precio}
                        elif tipo_cat == 'inversores':
                            upd = {"id": eid, "marca": e_marca, "modelo": e_modelo, "potencia_ac_kw": e_pot, "v_max_dc": e_vmax, "eficiencia_pct": 98.0, "certificaciones": e_cert, "precio_mxn": e_precio}
                        else:
                            upd = {"id": eid, "marca": e_marca, "modelo": e_modelo, "energia_kwh": e_pot, "v_nominal": e_vmax, "dod_recomendado_pct": 90.0, "certificaciones": e_cert, "precio_mxn": e_precio}
                        
                        exito = db.actualizar_registro(tipo_cat, eid, upd)
                        if exito:
                            st.success(f"✏️ ¡Equipo {eid} actualizado y sincronizado en vivo!")
                            st.rerun()
                        else:
                            st.error(f"❌ No se encontró ningún equipo con el ID {eid}.")
                    else:
                        st.warning("⚠️ Introduce el ID del equipo que deseas actualizar.")

                if btn_del:
                    if e_id:
                        eid = e_id.strip().upper()
                        db.eliminar_registro(tipo_cat, eid)
                        st.success(f"🗑️ Equipo {eid} eliminado de la base de datos.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Introduce el ID del equipo a eliminar.")

            st.markdown("---")
            st.subheader(f"📊 Listado Actual en Base de Datos: {tipo_cat.capitalize()}")
            st.dataframe(pd.DataFrame(db.datos.get(tipo_cat, [])), use_container_width=True)

    # --- PESTAÑA 4: HISTORIAL ---
    indice_hist = 3 if rol_usuario in ["admin", "admin_tec"] else None
    if indice_hist is not None and len(tabs) > indice_hist:
        with tabs[indice_hist]:
            st.header("📜 Historial de Cotizaciones")
            db.historial = db._cargar_historial()
            if db.historial:
                st.dataframe(pd.DataFrame(db.historial), use_container_width=True)
            else:
                st.info("No hay cotizaciones registradas todavía.")

    # --- PESTAÑA 5: GESTIÓN DE CLIENTES Y CONTROL GENERAL DE GANANCIAS ---
    indice_cli = 4 if rol_usuario in ["admin", "admin_tec"] else None
    if indice_cli is not None and len(tabs) > indice_cli:
        with tabs[indice_cli]:
            st.header("👥 Gestión Integral de Ganancias de Usuarios")
            st.markdown("Permite consultar y editar interactivamente las ganancias y permisos (**0.0% a 100.0%**). Puedes modificar los datos directamente en la tabla o mediante las casillas inferiores.")

            db.usuarios = db._cargar_usuarios()

            # FILTRADO DE SEGURIDAD: Los socios (admin_tec) NO pueden ver ni modificar los datos del Admin Principal
            if rol_usuario == "admin":
                usrs_visibles = list(db.usuarios.keys())
            else:
                usrs_visibles = [u for u, d in db.usuarios.items() if d.get('rol') != 'admin']

            # TABLA INTERACTIVA (EDICIÓN DIRECTA DESDE LA TABLA)
            st.subheader("📋 Resumen y Edición Directa de Ganancias")
            st.caption("💡 Haz clic directamente en las casillas de la tabla para cambiar 'Permiso Edición' o 'Ganancia Activa', edita el porcentaje y presiona 'Guardar Cambios de la Tabla'.")

            filas_tabla = []
            for u in usrs_visibles:
                d = db.usuarios[u]
                filas_tabla.append({
                    "Usuario": u,
                    "% Ganancia": float(d.get("ganancia_pct", 25.0)),
                    "Ganancia Activa": bool(d.get("aplicar_ganancia", True)),
                    "Permiso Edición": bool(d.get("ver_ganancia", False))
                })

            df_ganancias = pd.DataFrame(filas_tabla)

            df_editado = st.data_editor(
                df_ganancias,
                column_config={
                    "Usuario": st.column_config.TextColumn("Usuario", disabled=True),
                    "% Ganancia": st.column_config.NumberColumn("% Ganancia (0-100%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"),
                    "Ganancia Activa": st.column_config.CheckboxColumn("Ganancia Activa (On/Off)"),
                    "Permiso Edición": st.column_config.CheckboxColumn("Permiso Edición (Sí/No)", help="Desmarcar para bloquear al cliente")
                },
                hide_index=True,
                use_container_width=True,
                key="editor_tabla_ganancias_v19"
            )

            if st.button("💾 Guardar Cambios de la Tabla", type="primary"):
                for idx, row in df_editado.iterrows():
                    u_target = row["Usuario"]
                    if u_target in db.usuarios:
                        # Bloqueo estricto para evitar que un socio modifique al admin
                        if u_target == "admin" and rol_usuario != "admin":
                            continue
                        db.usuarios[u_target]["ganancia_pct"] = float(row["% Ganancia"])
                        db.usuarios[u_target]["aplicar_ganancia"] = bool(row["Ganancia Activa"])
                        db.usuarios[u_target]["ver_ganancia"] = bool(row["Permiso Edición"])
                db.guardar_usuarios()
                st.success("✅ ¡Tabla de ganancias actualizada correctamente!")
                st.rerun()

            st.markdown("---")
            st.subheader("✏️ Modificación Individual por Formulario")
            
            usr_seleccionado = st.selectbox("Seleccionar Cuenta a Modificar", usrs_visibles)

            if usr_seleccionado:
                u_datos = db.usuarios[usr_seleccionado]
                
                col_g1, col_g2, col_g3 = st.columns(3)
                
                with col_g1:
                    estado_gan_actual = u_datos.get("aplicar_ganancia", True)
                    nuevo_aplicar = st.toggle("Activar / Aplicar Ganancia Comercial", value=estado_gan_actual, key=f"togg_app_{usr_seleccionado}")
                
                with col_g2:
                    pct_actual = float(min(100.0, max(0.0, u_datos.get("ganancia_pct", 25.0))))
                    nuevo_pct_val = st.number_input("Porcentaje de Ganancia (0.0% a 100.0%)", min_value=0.0, max_value=100.0, value=pct_actual, step=0.5, key=f"num_pct_{usr_seleccionado}")

                with col_g3:
                    if u_datos.get('rol') in ['admin', 'admin_tec']:
                        st.info("ℹ️ Los socios y administradores siempre tienen permiso de edición.")
                        nuevo_ver_perm = True
                    else:
                        nuevo_ver_perm = st.toggle("Permitir que el cliente edite su ganancia", value=u_datos.get("ver_ganancia", False), key=f"togg_ver_{usr_seleccionado}")

                if st.button(f"💾 Guardar Cambios Individuales para '{usr_seleccionado}'", type="primary"):
                    if usr_seleccionado == "admin" and rol_usuario != "admin":
                        st.error("🚫 No tienes permisos para modificar al Administrador Principal.")
                    else:
                        db.usuarios[usr_seleccionado]["aplicar_ganancia"] = nuevo_aplicar
                        db.usuarios[usr_seleccionado]["ganancia_pct"] = float(nuevo_pct_val)
                        db.usuarios[usr_seleccionado]["ver_ganancia"] = nuevo_ver_perm
                        db.guardar_usuarios()
                        
                        st.success(f"✅ ¡Parámetros de '{usr_seleccionado}' actualizados correctamente! (Ganancia: {nuevo_pct_val}%, Estado: {'ACTIVA' if nuevo_aplicar else 'DESACTIVADA'}).")
                        st.rerun()

    # --- PESTAÑA 6: ADMIN PRINCIPAL & AUTORREFRESCO NATIVO (EXCLUSIVA PARA ADMIN) ---
    if rol_usuario == "admin" and len(tabs) >= 6:
        with tabs[5]:
            st.header("🛡️ Panel de Administración Principal")
            
            # SECCIÓN: NOTIFICACIONES DE RESTABLECIMIENTO DE CONTRASEÑA
            st.subheader("🔔 Notificaciones y Solicitudes de Restablecimiento")
            db.solicitudes = db._cargar_solicitudes()
            
            sols_pendientes = [s for s in db.solicitudes if s.get("estado") == "PENDIENTE"]
            
            if sols_pendientes:
                st.warning(f"⚠️ Tienes {len(sols_pendientes)} solicitud(es) pendiente(s) de restablecimiento de contraseña.")
                for s in sols_pendientes:
                    with st.expander(f"📌 Solicitud de Usuario: **{s['usuario']}** | Tel: {s['telefono']} | {s['fecha_hora']}"):
                        with st.form(f"form_res_{s['id']}", clear_on_submit=True):
                            st.write(f"**Usuario:** `{s['usuario']}`")
                            st.write(f"**Teléfono Confirmado:** `{s['telefono']}`")
                            n_pass = st.text_input("Asignar Nueva Contraseña para el Usuario", type="password", key=f"npass_sol_{s['id']}")
                            btn_atender = st.form_submit_button("🔑 Asignar y Notificar Nueva Contraseña")
                            
                            if btn_atender:
                                if not n_pass:
                                    st.warning("⚠️ Introduce la nueva contraseña.")
                                else:
                                    u_target = s['usuario']
                                    if u_target in db.usuarios:
                                        db.usuarios[u_target]["pass"] = n_pass
                                        db.guardar_usuarios()
                                    
                                    for item in db.solicitudes:
                                        if item["id"] == s["id"]:
                                            item["estado"] = "ATENDIDA"
                                            item["nueva_pass"] = n_pass
                                    db.guardar_solicitudes()
                                    
                                    st.success(f"✅ Contraseña de '{u_target}' actualizada a: `{n_pass}`. Puedes enviarle este mensaje por celular.")
                                    st.rerun()
            else:
                st.success("✅ No hay solicitudes pendientes de restablecimiento de contraseña.")

            st.markdown("---")
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.subheader("👥 Monitoreo de Usuarios en Tiempo Real")
            with col_ref2:
                auto_refresh = st.toggle("⏱️ Activar Auto-Refresco (cada 1 min)")
                st.caption("⚠️ Permite trabajar cómodamente en formularios sin interrupciones repentinas.")

            if st.button("🔄 Actualizar Monitoreo Ahora"):
                db.usuarios = db._cargar_usuarios()
                st.rerun()

            db.usuarios = db._cargar_usuarios()
            
            filas_html = ""
            for u, d in db.usuarios.items():
                sessions = d.get('active_sessions', []) if isinstance(d, dict) else []
                num_sesiones = len(sessions)
                is_activo = d.get('activo', True) if isinstance(d, dict) else True
                
                es_este_usuario_activo = (u == usuario_actual and st.session_state.logged_in)
                
                if not is_activo:
                    bg_color = "#7f1d1d" 
                    txt_color = "#fecaca"
                    estado_txt = "BLOQUEADO / BAJA"
                elif num_sesiones > 0 or es_este_usuario_activo:
                    bg_color = "#064e3b"
                    txt_color = "#a7f3d0"
                    conteo_real = max(num_sesiones, 1 if es_este_usuario_activo else 0)
                    estado_txt = f"CONECTADO EN VIVO ({conteo_real})"
                else:
                    bg_color = "#0f172a" 
                    txt_color = "#94a3b8"
                    estado_txt = "INACTIVO"

                filas_html += f"""
                    <tr style="background-color: {bg_color}; color: {txt_color}; border-bottom: 1px solid #334155;">
                        <td style="padding: 12px; font-weight: bold;">{u}</td>
                        <td style="padding: 12px;">{max(num_sesiones, 1 if es_este_usuario_activo else 0)}/3</td>
                        <td style="padding: 12px;">{d.get('contador_folios', 1):03d}</td>
                        <td style="padding: 12px; font-weight: bold;">{estado_txt}</td>
                    </tr>
                """

            html_monitoreo = f"""
            <div style="background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; color: #f8fafc; font-family: sans-serif;">
                    <thead>
                        <tr style="border-bottom: 2px solid #475569; text-align: left; background-color: #0f172a;">
                            <th style="padding: 12px;">Usuario</th>
                            <th style="padding: 12px;">Sesiones Activas</th>
                            <th style="padding: 12px;">Folio Actual</th>
                            <th style="padding: 12px;">Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
            </div>
            """
            
            components.html(html_monitoreo, height=200, scrolling=True)

            st.markdown("---")
            st.subheader("➕ Crear Nuevo Perfil de Usuario")
            
            with st.form("crear_usuario_form", clear_on_submit=True):
                nuevo_usr_id = st.text_input("Nombre de Usuario (Login)").strip()
                nuevo_usr_pass = st.text_input("Contraseña del Usuario", type="password").strip()
                nuevo_usr_tel = st.text_input("Número de Celular del Usuario (10 dígitos)").strip()
                tipo_rol_label = st.selectbox("Seleccionar Rol del Perfil", ["Cliente (Usuario Estándar)", "Socio / Administrador Técnico"])
                
                btn_crear_usr = st.form_submit_button("👤 Registrar Nuevo Usuario")
                
                if btn_crear_usr:
                    db.usuarios = db._cargar_usuarios()
                    if not nuevo_usr_id or not nuevo_usr_pass:
                        st.warning("⚠️ Debes rellenar el nombre de usuario y la contraseña.")
                    elif nuevo_usr_id in db.usuarios:
                        st.error(f"❌ El nombre de usuario '{nuevo_usr_id}' ya existe. Debes usar un nombre de usuario único.")
                    else:
                        if "Socio" in tipo_rol_label:
                            rol_asignado = "admin_tec"
                            ver_ganancia_def = True
                            ganancia_pct_def = 40.0
                        else:
                            rol_asignado = "usuario"
                            ver_ganancia_def = False
                            ganancia_pct_def = 25.0
                        
                        db.usuarios[nuevo_usr_id] = {
                            "pass": nuevo_usr_pass,
                            "rol": rol_asignado,
                            "activo": True,
                            "telefono": nuevo_usr_tel if nuevo_usr_tel else "5500000000",
                            "sesiones": 0,
                            "active_sessions": [],
                            "ver_ganancia": ver_ganancia_def,
                            "aplicar_ganancia": True,
                            "ganancia_pct": ganancia_pct_def,
                            "contador_folios": 1
                        }
                        db.guardar_usuarios()
                        st.success(f"✅ ¡Perfil '{nuevo_usr_id}' creado exitosamente como {tipo_rol_label}!")
                        st.rerun()

            st.markdown("---")
            st.subheader("🔑 Auditoría de Contraseñas (Segura con Clave de Admin)")
            st.caption("Muestra las contraseñas actualizadas de todos los usuarios.")
            
            pass_admin_check = st.text_input("Introduce tu contraseña de Administrador para revelar claves", type="password")
            if st.button("👁️ Revelar Credenciales"):
                db.usuarios = db._cargar_usuarios()
                if pass_admin_check == db.usuarios["admin"]["pass"]:
                    st.success("✅ Autenticación correcta:")
                    for u, d in db.usuarios.items():
                        st.code(f"Usuario: {u} | Teléfono: {d.get('telefono', 'N/A')} | Contraseña Actual: {d['pass']}")
                else:
                    st.error("❌ Contraseña de Administrador incorrecta.")

            st.markdown("---")
            # === SECCIÓN DE GESTIÓN DE CUENTAS: BLOQUEOS, CONTRASEÑAS Y CAMBIO DE ROL ===
            st.subheader("✏️ Gestión de Cuentas (Bajas, Cambios de Rol y Contraseñas)")
            lista_usrs = [u for u in db.usuarios.keys() if u != 'admin']
            target_usr = st.selectbox("Seleccionar Cuenta (El Administrador está protegido)", lista_usrs if lista_usrs else ["Sin usuarios"])
            
            if target_usr and target_usr != "Sin usuarios":
                col_g1, col_g2, col_g3 = st.columns(3)
                
                # Columna 1: Estado / Bloqueo
                with col_g1:
                    st.markdown("**Estado de la cuenta**")
                    if target_usr == "admin":
                        st.error("🚫 Cuenta protegida.")
                    elif db.usuarios[target_usr].get("activo", True):
                        if st.button("🔴 Bloquear Acceso", type="primary"):
                            db.usuarios[target_usr]["activo"] = False
                            db.usuarios[target_usr]["active_sessions"] = []
                            db.usuarios[target_usr]["sesiones"] = 0
                            db.guardar_usuarios()
                            st.success(f"Cuenta '{target_usr}' bloqueada.")
                            st.rerun()
                    else:
                        if st.button("🟢 Activar Cuenta", type="primary"):
                            db.usuarios[target_usr]["activo"] = True
                            db.guardar_usuarios()
                            st.success(f"Cuenta '{target_usr}' activada.")
                            st.rerun()

                # Columna 2: Cambio de Contraseña por Admin (LIMPIEZA AUTOMÁTICA AL GUARDAR)
                with col_g2:
                    st.markdown("**Cambiar Contraseña**")
                    with st.form(f"form_change_pass_{target_usr}", clear_on_submit=True):
                        nuevo_pass_usr = st.text_input("Nueva contraseña", type="password")
                        btn_save_p = st.form_submit_button("💾 Guardar Contraseña")
                        if btn_save_p:
                            if nuevo_pass_usr:
                                db.usuarios[target_usr]["pass"] = nuevo_pass_usr
                                db.guardar_usuarios()
                                st.success("✅ Contraseña actualizada.")

                # Columna 3: Cambio de Rol (EXCLUSIVO PARA EL ADMINISTRADOR PRINCIPAL)
                with col_g3:
                    st.markdown("**Cambiar Rol de Usuario**")
                    rol_actual = db.usuarios[target_usr].get("rol", "usuario")
                    rol_idx_def = 1 if rol_actual == "admin_tec" else 0
                    
                    nuevo_rol_sel = st.selectbox(
                        "Seleccionar nuevo rol",
                        ["Cliente (Usuario Estándar)", "Socio / Administrador Técnico"],
                        index=rol_idx_def,
                        key=f"rol_sel_{target_usr}"
                    )
                    
                    if st.button("🔄 Actualizar Rol"):
                        rol_mapeado = "admin_tec" if "Socio" in nuevo_rol_sel else "usuario"
                        if rol_mapeado != rol_actual:
                            db.usuarios[target_usr]["rol"] = rol_mapeado
                            if rol_mapeado == "admin_tec":
                                db.usuarios[target_usr]["ver_ganancia"] = True
                                db.usuarios[target_usr]["ganancia_pct"] = 40.0
                            else:
                                db.usuarios[target_usr]["ver_ganancia"] = False
                                db.usuarios[target_usr]["ganancia_pct"] = 25.0
                            db.guardar_usuarios()
                            st.success(f"✅ ¡El perfil de '{target_usr}' fue actualizado!")
                            st.rerun()
                        else:
                            st.info("El usuario ya tiene ese rol asignado.")

            if auto_refresh:
                time.sleep(60)
                st.rerun()
