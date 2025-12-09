import instaloader
import json
import os
import requests
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
LISTA_USUARIOS = ["m0ritaav", "fresaskoncremq", "yazminsitq", "exorcismxq", "jerezanotravis"] 
WEBHOOK_URL = "https://discord.com/api/webhooks/1446185382793183416/hiIK0y8-YEqVIXeAUV1jxRagEwFb_jBIqd1wfUl_ZguoYtKg51wTCZyI5I0oCNC7dxtF"

def guardar_base_datos(base_datos):
    with open("historial_multi.json", "w") as f:
        json.dump(base_datos, f)

def cargar_base_datos():
    if not os.path.exists("historial_multi.json"):
        return {}
    with open("historial_multi.json", "r") as f:
        return json.load(f)

def enviar_discord(mensaje):
    if "PEGA_AQUI" in WEBHOOK_URL: return
    # Cortamos el mensaje si es muy largo (límite de Discord 2000 caracteres)
    if len(mensaje) > 1900: mensaje = mensaje[:1900] + "... (mensaje cortado)"
    
    data = {"username": "IG Monitor", "content": mensaje}
    try: requests.post(WEBHOOK_URL, json=data)
    except: pass

def obtener_hora_mexico():
    utc_now = datetime.utcnow()
    mexico_time = utc_now - timedelta(hours=6)
    return mexico_time.strftime("%I:%M %p")

# --- INICIO ---
print("--- Ejecución Iniciada ---")
L = instaloader.Instaloader()
base_datos = cargar_base_datos()
hora_mx = obtener_hora_mexico()

# Listas para acumular los eventos
reporte_cambios = []
reporte_errores = []

for usuario in LISTA_USUARIOS:
    try:
        time.sleep(random.randint(5, 10)) 
        
        profile = instaloader.Profile.from_username(L.context, usuario)
        nuevos = {"seguidores": profile.followers, "seguidos": profile.followees}
        
        if usuario not in base_datos:
            base_datos[usuario] = nuevos
            reporte_cambios.append(f"🆕 **{usuario}**: Agregado a DB (Seguidores: {nuevos['seguidores']})")
        else:
            viejos = base_datos[usuario]
            cambios_txt = ""
            
            diff_followers = nuevos['seguidores'] - viejos['seguidores']
            if diff_followers != 0:
                cambios_txt += f"Seguidores: {viejos['seguidores']} ➡ {nuevos['seguidores']} ({diff_followers:+}) "
                
            diff_followees = nuevos['seguidos'] - viejos['seguidos']
            if diff_followees != 0:
                cambios_txt += f"Seguidos: {viejos['seguidos']} ➡ {nuevos['seguidos']} ({diff_followees:+})"
            
            if cambios_txt:
                reporte_cambios.append(f"🚨 **{usuario}**: {cambios_txt}")
                base_datos[usuario] = nuevos
                
    except Exception as e:
        # Acumulamos el error en lugar de enviarlo ya
        error_limpio = str(e).split('\n')[0] # Tomamos solo la primera línea del error
        reporte_errores.append(f"⚠️ **{usuario}**: {error_limpio}")

guardar_base_datos(base_datos)

# --- GENERAR MENSAJE FINAL ---
mensaje_final = ""

# 1. Si hubo cambios, los agregamos
if reporte_cambios:
    mensaje_final += "**📊 NOVEDADES DETECTADAS:**\n" + "\n".join(reporte_cambios) + "\n\n"

# 2. Si hubo errores, los agregamos
if reporte_errores:
    mensaje_final += "**🛠️ ERRORES EN EL REPORTE:**\n" + "\n".join(reporte_errores) + "\n\n"

# 3. Decidir qué enviar
if mensaje_final:
    # Si la variable tiene texto, es que pasó algo (bueno o malo)
    cabecera = f"📢 **Reporte de Actividad** ({hora_mx})\n\n"
    enviar_discord(cabecera + mensaje_final)
else:
    # Si la variable está vacía, es que no hubo ni cambios ni errores
    enviar_discord(f"✅ **Chequeo Completo ({hora_mx}):** Sin novedades ni errores en las {len(LISTA_USUARIOS)} cuentas.")

print("--- Fin de la ejecución ---")
