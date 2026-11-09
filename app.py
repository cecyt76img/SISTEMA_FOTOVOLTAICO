# ==============================================================================
# PROYECTO DE TITULACIÓN TÉCNICA - CECYT 7 "CUAUHTÉMOC" (IPN)
# Sistema Integral FV V16.1: Visualización Segura de Contraseñas y CRUD Total
# ==============================================================================

!pip install reportlab openpyxl pandas matplotlib ipywidgets -q

import os
import io
import json
import math
import base64
import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from datetime import datetime
from typing import List, Dict, Optional, Any
from IPython.display import display, HTML, clear_output
from google.colab import drive, files

# ReportLab - PDF y Vectorial
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# ==============================================================================
# 1. CONSTANTES GLOBALES Y GESTOR DE SISTEMA CON BIBLIOTECA AMPLIADA
# ==============================================================================
RESISTIVIDAD_COBRE_OHM_MM2_M = 0.0193
FACTOR_RENDIMIENTO_GLOBAL = 0.80       

class GestorSistemaFV:
    def __init__(self, ruta_dir: str):
        self.ruta_dir = ruta_dir
        self.ruta_equipos = os.path.join(ruta_dir, 'equipos_fv_v16.json')
        self.ruta_usuarios = os.path.join(ruta_dir, 'usuarios_sistema_v16.json')
        self.ruta_auditoria = os.path.join(ruta_dir, 'auditoria_accesos_v16.json')
        self.ruta_historial = os.path.join(ruta_dir, 'historial_cotizaciones_v16.json')
        
        self.datos = self._cargar_equipos()
        self.usuarios = self._cargar_usuarios()
        self.auditoria = self._cargar_auditoria()
        self.historial = self._cargar_historial()

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
            "admin": {"pass": "solar2026", "rol": "admin", "activo": True, "sesiones": 0, "ver_ganancia": True, "ganancia_pct": 40.0, "contador_folios": 1},
            "socio1": {"pass": "renovable2026", "rol": "admin_tec", "activo": True, "sesiones": 0, "ver_ganancia": True, "ganancia_pct": 40.0, "contador_folios": 1},
            "cliente": {"pass": "solar2026", "rol": "usuario", "activo": True, "sesiones": 0, "ver_ganancia": False, "ganancia_pct": 25.0, "contador_folios": 1}
        }
        if not os.path.exists(self.ruta_usuarios):
            with open(self.ruta_usuarios, 'w', encoding='utf-8') as f: json.dump(usuarios_base, f, indent=4)
            return usuarios_base
        try:
            with open(self.ruta_usuarios, 'r', encoding='utf-8') as f: 
                usrs = json.load(f)
                for u in usrs:
                    if "contador_folios" not in usrs[u]: usrs[u]["contador_folios"] = 1
                    if "activo" not in usrs[u]: usrs[u]["activo"] = True
                return usrs
        except: return usuarios_base

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

    def guardar_usuarios(self):
        with open(self.ruta_usuarios, 'w', encoding='utf-8') as f: json.dump(self.usuarios, f, indent=4)

    def guardar_equipos(self):
        with open(self.ruta_equipos, 'w', encoding='utf-8') as f: json.dump(self.datos, f, indent=4)

    def registrar_cotizacion(self, reg):
        self.historial.insert(0, reg)
        with open(self.ruta_historial, 'w', encoding='utf-8') as f: json.dump(self.historial, f, indent=4, ensure_ascii=False)

    def login_usuario(self, usr: str) -> bool:
        self.usuarios = self._cargar_usuarios()
        if not self.usuarios.get(usr, {}).get("activo", True): return False
        if self.usuarios[usr].get("sesiones", 0) >= 2: return False 
        self.usuarios[usr]["sesiones"] = self.usuarios[usr].get("sesiones", 0) + 1
        self.guardar_usuarios()
        return True

    def logout_usuario(self, usr: str):
        self.usuarios = self._cargar_usuarios()
        if usr in self.usuarios:
            self.usuarios[usr]["sesiones"] = max(0, self.usuarios[usr].get("sesiones", 1) - 1)
            self.guardar_usuarios()

    def registrar_acceso(self, usuario: str, rol: str):
        self.auditoria.insert(0, {"fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "usuario": usuario, "rol": rol})
        with open(self.ruta_auditoria, 'w', encoding='utf-8') as f: json.dump(self.auditoria, f, indent=4)

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

try:
    drive.mount('/content/drive', force_remount=False)
    dir_proyecto = '/content/drive/MyDrive/Proyecto_Tesis_CECyT7'
    os.makedirs(dir_proyecto, exist_ok=True)
    db = GestorSistemaFV(dir_proyecto)
except:
    db = GestorSistemaFV('.')

for u in db.usuarios: db.usuarios[u]["sesiones"] = 0
db.guardar_usuarios()

# ==============================================================================
# 2. MOTOR DE CÁLCULO E INGENIERÍA
# ==============================================================================
class MotorCalculoFV:
    @staticmethod
    def dimensionar_sistema(cons_bim, hsp, pid, iid, costo, modo_operacion, bid, horas_respaldo, ganancia_pct, extras_mxn):
        panel = next((p for p in db.obtener_paneles() if p["id"] == pid), None)
        inv = next((i for i in db.obtener_inversores() if i["id"] == iid), None)
        
        cons_diario = cons_bim / 60.0
        pot_req = (cons_diario / FACTOR_RENDIMIENTO_GLOBAL) / max(0.1, hsp)
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
        precio_venta = costo_directo * (1.0 + (max(0, ganancia_pct) / 100.0))
        ahorro_anual = pot_real * max(0.1, hsp) * FACTOR_RENDIMIENTO_GLOBAL * 365 * costo
        
        return {
            'panel': panel, 'inversor': inv, 'n_pan': n_pan_real, 'ns': ns, 'np': np_arr,
            'bateria': bobj, 'n_bat': n_bat, 'costo_directo': costo_directo, 
            'precio_venta': precio_venta, 'ahorro_anual': ahorro_anual, 
            'roi': precio_venta / ahorro_anual if ahorro_anual > 0 else 0,
            'ganancia_pct': ganancia_pct
        }

# ==============================================================================
# 3. GENERADOR DE PDF PROFESIONAL
# ==============================================================================
class GeneradorReportes:
    @staticmethod
    def construir_pdf(datos, folio_str, ruta_salida, mostrar_precios_internos):
        doc = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"MEMORIA TÉCNICA - CECyT 7 | Folio: {folio_str}", styles['Heading1']), Spacer(1, 10)]
        
        marca_bat = datos['bateria'].get('marca', 'N/A') if datos['bateria'] else 'N/A'
        precio_bat = datos['bateria'].get('precio_mxn', 0.0) if datos['bateria'] else 0.0
        precio_p = datos['panel'].get('precio_mxn', 0.0)
        precio_i = datos['inversor'].get('precio_mxn', 0.0)

        if mostrar_precios_internos:
            t_data = [
                ["Equipos (Piezas Totales)", "Especificación Técnica", "Costo Unitario Interno"],
                [f"Paneles ({datos['n_pan']} pzas)", f"{datos['panel'].get('marca', '')} {datos['panel'].get('potencia_w', 0)}W | Vmp: {datos['panel'].get('vmp', 0)}V", f"${precio_p:,.2f}"],
                ["Inversor", f"{datos['inversor'].get('marca', '')} {datos['inversor'].get('potencia_ac_kw', 0)}kW", f"${precio_i:,.2f}"],
                ["Banco Baterías", f"{datos['n_bat']} uds ({marca_bat})", f"${precio_bat:,.2f}"],
                ["PRECIO FINAL CLIENTE", f"Ahorro Anual: ${datos['ahorro_anual']:,.2f}", f"${datos['precio_venta']:,.2f}"]
            ]
        else:
            t_data = [
                ["Equipos Incluidos", "Especificación", "Cantidad Instalada"],
                ["Paneles Solares", f"{datos['panel'].get('marca', '')} {datos['panel'].get('potencia_w', 0)}W", f"{datos['n_pan']} uds"],
                ["Inversor Fotovoltaico", f"{datos['inversor'].get('marca', '')} {datos['inversor'].get('potencia_ac_kw', 0)}kW", "1 ud"],
                ["Banco Baterías", f"{marca_bat}", f"{datos['n_bat']} uds"],
                ["INVERSIÓN TOTAL", f"Ahorro Anual: ${datos['ahorro_anual']:,.2f}", f"${datos['precio_venta']:,.2f}"]
            ]

        t = Table(t_data, colWidths=[2.2*inch, 3.2*inch, 1.6*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
        story.append(t)
        doc.build(story)

# ==============================================================================
# 4. APLICACIÓN PRINCIPAL CON SEGURIDAD DE CREDENCIALES
# ==============================================================================
def construir_aplicacion_principal(contenedor_app, contenedor_login, rol_usuario, usuario_actual):
    db.usuarios = db._cargar_usuarios()
    
    if not db.usuarios.get(usuario_actual, {}).get("activo", True):
        with contenedor_app: clear_output()
        with contenedor_login:
            clear_output()
            display(HTML("<div style='background:#ef4444; color:white; padding:15px; border-radius:5px;'><b>❌ ACCESO REVOCADO:</b> Tu cuenta ha sido dada de baja por el Administrador.</div>"))
            display(box_login)
        return

    usr_data = db.usuarios.get(usuario_actual, {})
    style_lbl, layout_inp = {'description_width': '220px'}, widgets.Layout(width='450px')

    def get_opt_p(): return [(f"{p.get('marca','')} {p.get('modelo','')} (${p.get('precio_mxn',0):,.0f})", p['id']) for p in db.obtener_paneles()]
    def get_opt_i(): return [(f"{i.get('marca','')} {i.get('modelo','')} (${i.get('precio_mxn',0):,.0f})", i['id']) for i in db.obtener_inversores()]
    def get_opt_b(): 
        ops = [('Ninguna / No Aplica', '')]
        ops.extend([(f"{b.get('marca','')} {b.get('modelo','')} (${b.get('precio_mxn',0):,.0f})", b['id']) for b in db.obtener_baterias()])
        return ops

    w_consumo = widgets.BoundedIntText(value=550, min=50, max=10000, description='Consumo Bimestral (kWh):', style=style_lbl, layout=layout_inp)
    w_hsp = widgets.FloatSlider(value=5.3, min=3.0, max=7.0, description='HSP:', style=style_lbl, layout=layout_inp)
    w_panel = widgets.Dropdown(options=get_opt_p(), description='Panel:', style=style_lbl, layout=layout_inp)
    w_inversor = widgets.Dropdown(options=get_opt_i(), description='Inversor:', style=style_lbl, layout=layout_inp)
    w_modo = widgets.Dropdown(options=['Interconectado (CFE)', 'Híbrido'], value='Interconectado (CFE)', description='Modo:', style=style_lbl, layout=layout_inp)
    w_bat = widgets.Dropdown(options=get_opt_b(), description='Batería:', style=style_lbl, layout=layout_inp)
    w_costo = widgets.FloatText(value=3.50, description='Costo kWh:', style=style_lbl, layout=layout_inp)
    w_ganancia = widgets.FloatSlider(value=usr_data.get('ganancia_pct', 40.0), min=0.0, max=100.0, step=1.0, description='% Ganancia:', style=style_lbl, layout=widgets.Layout(width='450px'))
    
    out_res = widgets.Output()
    btn_calc = widgets.Button(description='⚡ Cotizar', button_style='primary')
    btn_pdf = widgets.Button(description='📄 Generar PDF', button_style='success')
    btn_logout = widgets.Button(description='🚪 Cerrar Sesión', button_style='danger')
    btn_sincronizar = widgets.Button(description='🔄 Actualizar y Sincronizar Todo', button_style='info')

    def sincronizar_todo_handler(b):
        w_panel.options = get_opt_p()
        w_inversor.options = get_opt_i()
        w_bat.options = get_opt_b()
        print("🔄 ¡Catálogos actualizados desde la base de datos central!")

    btn_sincronizar.on_click(sincronizar_todo_handler)

    controles_dim = [widgets.HBox([btn_sincronizar]), w_consumo, w_hsp, w_panel, w_inversor, w_modo, w_bat, w_costo]
    if rol_usuario != "usuario" or usr_data.get("ver_ganancia", False):
        controles_dim.append(w_ganancia)

    controles_dim.extend([widgets.HBox([btn_calc, btn_pdf]), out_res])
    tab_dim = widgets.VBox(controles_dim)

    def calc_handler(b):
        with out_res:
            clear_output()
            try:
                db.usuarios = db._cargar_usuarios()
                usr_actualizado = db.usuarios.get(usuario_actual, {})
                ganancia_a_usar = w_ganancia.value if (rol_usuario != "usuario" or usr_actualizado.get("ver_ganancia", False)) else usr_actualizado.get("ganancia_pct", 25.0)
                
                res = MotorCalculoFV.dimensionar_sistema(w_consumo.value, w_hsp.value, w_panel.value, w_inversor.value, w_costo.value, w_modo.value, w_bat.value, 4, ganancia_a_usar, 15000.0)
                
                display(HTML(f"""
                <div style="background:#0f172a; color:#f8fafc; padding:20px; border-radius:10px;">
                    <h3 style="color:#38bdf8;">📋 Resumen de Cotización</h3>
                    <p><b>Paneles:</b> {res['n_pan']} piezas ({res['panel']['marca']} {res['panel']['modelo']})</p>
                    <p><b>Inversor:</b> {res['inversor']['marca']} {res['inversor']['modelo']}</p>
                    <p style="color:#4ade80; font-size:18px;"><b>Inversión Total:</b> ${res['precio_venta']:,.2f} | <b>ROI:</b> {res['roi']:.1f} años</p>
                </div>
                """))
            except Exception as e: print(f"❌ Error: {e}")

    btn_calc.on_click(calc_handler)

    def pdf_handler(b):
        with out_res:
            clear_output()
            try:
                db.usuarios = db._cargar_usuarios()
                usr_actualizado = db.usuarios.get(usuario_actual, {})
                
                rol_prefijo = "ADM" if rol_usuario == "admin" else ("SOC" if rol_usuario == "admin_tec" else "CLI")
                contador_actual = usr_actualizado.get("contador_folios", 1)
                folio_str = f"{rol_prefijo}-{usuario_actual.upper()[:10]}-{contador_actual:03d}"
                
                ganancia_a_usar = w_ganancia.value if (rol_usuario != "usuario" or usr_actualizado.get("ver_ganancia", False)) else usr_actualizado.get("ganancia_pct", 25.0)
                mostrar_precios = True if (rol_usuario != "usuario" or usr_actualizado.get("ver_ganancia", False)) else False

                res = MotorCalculoFV.dimensionar_sistema(w_consumo.value, w_hsp.value, w_panel.value, w_inversor.value, w_costo.value, w_modo.value, w_bat.value, 4, ganancia_a_usar, 15000.0)
                nombre_archivo = f"/content/Cotizacion_{folio_str}.pdf"
                
                GeneradorReportes.construir_pdf(res, folio_str, nombre_archivo, mostrar_precios)
                
                if os.path.exists(nombre_archivo):
                    db.registrar_cotizacion({
                        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "folio": folio_str, "usuario": usuario_actual, "rol": rol_usuario,
                        "precio_total_mxn": round(res['precio_venta'], 2)
                    })
                    db.usuarios[usuario_actual]["contador_folios"] = contador_actual + 1
                    db.guardar_usuarios()

                    try: files.download(nombre_archivo)
                    except: pass

                    with open(nombre_archivo, "rb") as f: b64 = base64.b64encode(f.read()).decode()
                    display(HTML(f"""
                    <div style="background:#065f46; color:#ecfdf5; padding:15px; border-radius:8px; margin-top:15px;">
                        <h4>✅ PDF Generado - Folio: {folio_str}</h4>
                        <button onclick="
                            const link = document.createElement('a');
                            link.href = 'data:application/pdf;base64,{b64}';
                            link.download = 'Cotizacion_{folio_str}.pdf';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        " style="background:#10b981; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                           📥 Forzar Descarga PDF ({folio_str})
                        </button>
                    </div>
                    """))
            except Exception as e: print(f"❌ Error PDF: {e}")

    btn_pdf.on_click(pdf_handler)
    
    def logout_handler(b):
        db.logout_usuario(usuario_actual)
        with contenedor_app: clear_output()
        with contenedor_login: clear_output(); display(box_login)
    btn_logout.on_click(logout_handler)

    # --- PESTAÑA 2: INVENTARIO CON CRUD AVANZADO ---
    def crear_pestana_inventario():
        w_tipo = widgets.Dropdown(options=['paneles', 'inversores', 'baterias'], description='Categoría:', style=style_lbl, layout=layout_inp)
        w_id = widgets.Text(description='ID del Equipo:', placeholder='PAN-010', style=style_lbl, layout=layout_inp)
        w_marca = widgets.Text(description='Marca:', placeholder='Ej. Jinko Solar', style=style_lbl, layout=layout_inp)
        w_modelo = widgets.Text(description='Modelo:', placeholder='Ej. Tiger Neo', style=style_lbl, layout=layout_inp)
        w_pot = widgets.FloatText(description='Potencia (W) / kW:', value=550.0, style=style_lbl, layout=layout_inp)
        w_precio = widgets.FloatText(description='Precio (MXN):', value=2500.0, style=style_lbl, layout=layout_inp)
        w_largo = widgets.FloatText(description='Largo (mm):', value=2278.0, style=style_lbl, layout=layout_inp)
        w_ancho = widgets.FloatText(description='Ancho (mm):', value=1134.0, style=style_lbl, layout=layout_inp)
        w_vmax = widgets.FloatText(description='Voltaje Máx / Vmp (V):', value=41.5, style=style_lbl, layout=layout_inp)
        w_cert = widgets.Text(description='Certificaciones:', placeholder='IEC61215, TUV', style=style_lbl, layout=layout_inp)
        
        btn_crear = widgets.Button(description='➕ Añadir Nuevo', button_style='primary')
        btn_editar = widgets.Button(description='✏️ Actualizar / Editar', button_style='warning')
        btn_eliminar = widgets.Button(description='🗑️ Eliminar', button_style='danger')
        out_crud = widgets.Output()

        def ejecutar_crud(accion):
            with out_crud:
                clear_output()
                cat = w_tipo.value
                eid = w_id.value.strip().upper()
                if not eid:
                    print("⚠️ Debes proporcionar un ID de equipo válido (ej. PAN-010).")
                    return
                
                if accion == 'crear':
                    if cat == 'paneles':
                        nuevo = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "potencia_w": w_pot.value, "vmp": w_vmax.value, "largo_mm": w_largo.value, "ancho_mm": w_ancho.value, "area_m2": round((w_largo.value*w_ancho.value)/1000000.0, 2), "eficiencia_pct": 21.5, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    elif cat == 'inversores':
                        nuevo = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "potencia_ac_kw": w_pot.value/100.0 if w_pot.value>50 else w_pot.value, "v_max_dc": w_vmax.value, "eficiencia_pct": 98.0, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    else:
                        nuevo = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "energia_kwh": w_pot.value, "v_nominal": w_vmax.value, "dod_recomendado_pct": 90.0, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    
                    db.agregar_registro(cat, nuevo)
                    print(f"✅ ¡Equipo {eid} añadido exitosamente!")
                elif accion == 'editar':
                    if cat == 'paneles':
                        upd = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "potencia_w": w_pot.value, "vmp": w_vmax.value, "largo_mm": w_largo.value, "ancho_mm": w_ancho.value, "area_m2": round((w_largo.value*w_ancho.value)/1000000.0, 2), "eficiencia_pct": 21.5, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    elif cat == 'inversores':
                        upd = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "potencia_ac_kw": w_pot.value, "v_max_dc": w_vmax.value, "eficiencia_pct": 98.0, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    else:
                        upd = {"id": eid, "marca": w_marca.value, "modelo": w_modelo.value, "energia_kwh": w_pot.value, "v_nominal": w_vmax.value, "dod_recomendado_pct": 90.0, "certificaciones": w_cert.value, "precio_mxn": w_precio.value}
                    
                    exito = db.actualizar_registro(cat, eid, upd)
                    if exito: print(f"✏️ ¡Equipo {eid} actualizado correctamente!")
                    else: print(f"❌ No se encontró el ID {eid} para actualizar.")
                elif accion == 'eliminar':
                    db.eliminar_registro(cat, eid)
                    print(f"🗑️ Equipo {eid} eliminado.")
                
                w_panel.options = get_opt_p()
                w_inversor.options = get_opt_i()
                w_bat.options = get_opt_b()

        btn_crear.on_click(lambda b: ejecutar_crud('crear'))
        btn_editar.on_click(lambda b: ejecutar_crud('editar'))
        btn_eliminar.on_click(lambda b: ejecutar_crud('eliminar'))

        return widgets.VBox([
            widgets.HTML("<h3>📦 Biblioteca Ampliada y CRUD de Equipos</h3>"),
            w_tipo, w_id, w_marca, w_modelo, w_pot, w_precio, w_largo, w_ancho, w_vmax, w_cert,
            widgets.HBox([btn_crear, btn_editar, btn_eliminar]), out_crud
        ])

    # --- PESTAÑA 3: HISTORIAL ---
    out_hist = widgets.Output()
    def ref_h(b=None):
        with out_hist:
            clear_output()
            db.historial = db._cargar_historial()
            if db.historial: display(HTML(pd.DataFrame(db.historial).to_html(index=False)))
            else: print("Sin cotizaciones registradas.")
    ref_h()
    tab_hist = widgets.VBox([widgets.Button(description="🔄 Actualizar Historial", on_click=ref_h), out_hist])

    # --- PESTAÑA 4: ADMIN PRINCIPAL CON VISUALIZACIÓN SEGURA DE CONTRASEÑAS ---
    if rol_usuario == "admin":
        out_users = widgets.Output()
        
        def obtener_lista_usuarios():
            ops = [u for u in db.usuarios.keys() if u != 'admin']
            return ops if ops else ['(Sin usuarios)']

        drop_target_editar = widgets.Dropdown(options=obtener_lista_usuarios(), description='Modificar:', style=style_lbl, layout=layout_inp)

        def actualizar_tabla_admin():
            with out_users:
                clear_output()
                db.usuarios = db._cargar_usuarios()
                drop_target_editar.options = obtener_lista_usuarios()

                html_t = "<table style='width:100%; text-align:left; border-collapse:collapse;'>"
                html_t += "<tr style='border-bottom:1px solid #ccc; background:#f1f5f9;'><th>Usuario</th><th>Rol</th><th>Sesiones</th><th>Folio Actual</th><th>Estado Cuenta</th></tr>"
                for u, d in db.usuarios.items():
                    estado = "🟢 ACTIVO" if d.get("activo", True) else "🔴 BAJA / BLOQUEADO"
                    html_t += f"<tr style='height:35px; border-bottom:1px solid #eee;'><td>{u}</td><td>{d['rol']}</td><td>{d.get('sesiones',0)}/2</td><td>{d.get('contador_folios',1):03d}</td><td><b>{estado}</b></td></tr>"
                html_t += "</table>"
                display(HTML(html_t))

        # Sección de Visualización Segura de Contraseñas
        admin_pass_input = widgets.Password(value='', placeholder='Introduce tu contraseña de Admin', description='Contraseña Admin:', style=style_lbl, layout=layout_inp)
        btn_ver_passwords = widgets.Button(description='👁️ Revelar Contraseñas', button_style='info')
        out_passwords_seguro = widgets.Output()

        def revelar_passwords_handler(b):
            with out_passwords_seguro:
                clear_output()
                pwd_ingresada = admin_pass_input.value.strip()
                if pwd_ingresada == db.usuarios["admin"]["pass"]:
                    db.usuarios = db._cargar_usuarios()
                    html_p = "<div style='background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #cbd5e1; margin-top:10px;'>"
                    html_p += "<h4 style='color:#0f172a; margin-top:0;'>🔐 Credenciales de Usuarios Registrados:</h4>"
                    html_p += "<ul style='margin-bottom:0;'>"
                    for u, d in db.usuarios.items():
                        html_p += f"<li><b>{u}</b> (Rol: {d['rol']}) ➔ Contraseña: <code style='background:#e2e8f0; padding:2px 6px; border-radius:4px;'>{d['pass']}</code></li>"
                    html_p += "</ul></div>"
                    display(HTML(html_p))
                else:
                    print("❌ Contraseña de Administrador incorrecta. Acceso denegado.")

        btn_ver_passwords.on_click(revelar_passwords_handler)

        btn_deshabilitar = widgets.Button(description='🔴 Dar de Baja / Bloquear Acceso', button_style='danger')
        btn_habilitar = widgets.Button(description='🟢 Activar Cuenta', button_style='success')
        edit_usr_nuevo_pass = widgets.Text(description='Nueva Contraseña:', placeholder='password', style=style_lbl, layout=layout_inp)
        btn_guardar_pass = widgets.Button(description='💾 Cambiar Contraseña', button_style='warning')
        out_gestor_usr = widgets.Output()

        def deshabilitar_handler(b):
            with out_gestor_usr:
                clear_output()
                target = drop_target_editar.value
                if target and target != '(Sin usuarios)':
                    db.usuarios[target]["activo"] = False
                    db.usuarios[target]["sesiones"] = 0
                    db.guardar_usuarios()
                    actualizar_tabla_admin()
                    print(f"🔴 Cuenta '{target}' bloqueada instantáneamente.")

        def habilitar_handler(b):
            with out_gestor_usr:
                clear_output()
                target = drop_target_editar.value
                if target and target != '(Sin usuarios)':
                    db.usuarios[target]["activo"] = True
                    db.guardar_usuarios()
                    actualizar_tabla_admin()
                    print(f"🟢 Cuenta '{target}' activada.")

        def cambiar_pass_handler(b):
            with out_gestor_usr:
                clear_output()
                target = drop_target_editar.value
                n_pwd = edit_usr_nuevo_pass.value.strip()
                if target and target != '(Sin usuarios)' and n_pwd:
                    db.usuarios[target]["pass"] = n_pwd
                    db.guardar_usuarios()
                    print(f"✅ Contraseña de '{target}' actualizada con éxito.")

        btn_deshabilitar.on_click(deshabilitar_handler)
        btn_habilitar.on_click(habilitar_handler)
        btn_guardar_pass.on_click(cambiar_pass_handler)
        actualizar_tabla_admin()

        tab_admin = widgets.VBox([
            widgets.HTML("<h3>🛡️ Panel de Control y Auditoría de Credenciales</h3>"), out_users,
            widgets.HTML("<hr><h4>🔑 Auditoría de Contraseñas (Requiere Autenticación de Admin):</h4>"),
            admin_pass_input, btn_ver_passwords, out_passwords_seguro,
            widgets.HTML("<hr><h4>Gestionar Cuentas (Bajas, Activaciones y Contraseñas):</h4>"),
            drop_target_editar, widgets.HBox([btn_deshabilitar, btn_habilitar]), edit_usr_nuevo_pass, btn_guardar_pass, out_gestor_usr
        ])

    # Construcción de pestañas según rol
    if rol_usuario == "admin":
        tabs = widgets.Tab(children=[tab_dim, crear_pestana_inventario(), tab_hist, tab_admin])
        tabs.set_title(0, '⚡ Cotizador')
        tabs.set_title(1, '📦 Inventario & CRUD')
        tabs.set_title(2, '📜 Historial')
        tabs.set_title(3, '🛡️ Admin Principal')
    elif rol_usuario == "admin_tec":
        tabs = widgets.Tab(children=[tab_dim, crear_pestana_inventario(), tab_hist])
        tabs.set_title(0, '⚡ Cotizador')
        tabs.set_title(1, '📦 Inventario & CRUD')
        tabs.set_title(2, '📜 Historial')
    else:
        tabs = widgets.Tab(children=[tab_dim])
        tabs.set_title(0, '⚡ Cotizador Cliente')

    with contenedor_app:
        clear_output()
        display(widgets.VBox([widgets.HBox([widgets.HTML(f"<h2>☀️ CECyT 7 | {usuario_actual.upper()}</h2>"), btn_logout]), tabs]))

# ==============================================================================
# 5. MÓDULO DE LOGIN SEGURO
# ==============================================================================
w_user = widgets.Text(value='', placeholder='Escribe tu usuario', description='Usuario:')
w_pass = widgets.Password(value='', placeholder='Escribe tu contraseña', description='Contraseña:')
btn_login = widgets.Button(description='🔑 Iniciar Sesión', button_style='success')
out_login = widgets.Output()

app_container = widgets.Output()
login_container = widgets.Output()

def login_handler(b):
    with out_login:
        clear_output()
        usr = w_user.value.strip()
        pwd = w_pass.value.strip()
        
        db.usuarios = db._cargar_usuarios()
        if usr in db.usuarios:
            if not db.usuarios[usr].get("activo", True):
                print("❌ Acceso denegado: Esta cuenta ha sido inhabilitada.")
                return
            if db.usuarios[usr]["pass"] == pwd:
                if db.login_usuario(usr):
                    rol = db.usuarios[usr].get("rol", "usuario")
                    db.registrar_acceso(usr, rol)
                    with login_container: clear_output()
                    construir_aplicacion_principal(app_container, login_container, rol, usr)
                else: print("❌ Límite de sesiones alcanzado.")
            else: print("❌ Contraseña incorrecta.")
        else: print("❌ Usuario no encontrado.")

btn_login.on_click(login_handler)

box_login = widgets.VBox([
    widgets.HTML("<h3 style='color:#0284c7;'>🔒 Acceso Sistema FV CECyT 7</h3>"), 
    w_user, w_pass, btn_login, out_login
])

clear_output()
display(login_container, app_container)
with login_container: display(box_login)
