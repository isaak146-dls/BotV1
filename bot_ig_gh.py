import instaloader
import json
import os
import requests
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURACIÓN SEGURA ---

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

usuarios_env = os.getenv('LISTA_OBJETIVOS')
if usuarios_env:
    LISTA_USUARIOS = [u.strip() for u in usuarios_env.split(',') if u.strip()]
else:
    print("⚠️ Error: No se encontró la lista en los secretos (LISTA_OBJETIVOS).")
    LISTA_USUARIOS = []

def guardar_base_datos(base_datos):
    with open("historial_multi.json", "w") as f:
        json.dump(base_datos, f)

def cargar_base_datos():
    if not os.path.exists("historial_multi.json"):
        return {}
    with open("historial_multi.json", "r") as f:
        return json.load(f)

def enviar_discord(mensaje):
    if not WEBHOOK_URL: return
    if len(mensaje) > 1900: mensaje = mensaje[:1900] + "... (cortado)"
    
    data = {"username": "IG Monitor (Seguidores)", "content": mensaje}
    try: requests.post(WEBHOOK_URL, json=data)
    except: pass

def obtener_hora_mexico():
    utc_now = datetime.utcnow()
    mexico_time = utc_now - timedelta(hours=6)
    return mexico_time.strftime("%I:%M %p")

print("--- Ejecución Iniciada (Modo Seguro) ---")
L = instaloader.Instaloader()
base_datos = cargar_base_datos()
hora_mx = obtener_hora_mexico()

reporte_cambios = []
reporte_errores = []

for usuario in LISTA_USUARIOS:
    print(f"::add-mask::{usuario}") 
    # -----------------------------

    try:
        # Pausa aleatoria
        time.sleep(random.randint(5, 10)) 
        
        print(f"Revisando a: {usuario}") 
        
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
        # Limpiamos el mensaje de error
        error_msg = str(e).split('\n')[0]
        reporte_errores.append(f"⚠️ **{usuario}**: {error_msg}")

guardar_base_datos(base_datos)

# --- GENERAR MENSAJE FINAL ---
mensaje_final = ""

if reporte_cambios:
    mensaje_final += "**📊 CAMBIOS EN SEGUIDORES:**\n" + "\n".join(reporte_cambios) + "\n\n"

if reporte_errores:
    mensaje_final += "**🛠️ ERRORES (Instaloader):**\n" + "\n".join(reporte_errores) + "\n\n"

if mensaje_final:
    cabecera = f"📢 **Reporte de Seguidores** ({hora_mx})\n\n"
    enviar_discord(cabecera + mensaje_final)
else:
    enviar_discord(f"✅ **Seguidores OK ({hora_mx}):** Sin cambios en las {len(LISTA_USUARIOS)} cuentas.")

print("--- Fin de la ejecución ---")
