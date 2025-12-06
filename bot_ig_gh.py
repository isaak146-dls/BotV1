import instaloader
import json
import os
import requests
import random
import time
from datetime import datetime

# --- CONFIGURACIÓN ---
LISTA_USUARIOS = ["m0ritaav", "fresaskoncremq", "yazminsitq", "exorcismxq", "jerezanotravis"] 
WEBHOOK_URL = "https://discord.com/api/webhooks/1446185382793183416/hiIK0y8-YEqVIXeAUV1jxRagEwFb_jBIqd1wfUl_ZguoYtKg51wTCZyI5I0oCNC7dxtF" # <--- ¡RECUERDA PONER TU URL!

def guardar_base_datos(base_datos):
    with open("historial_multi.json", "w") as f:
        json.dump(base_datos, f)

def cargar_base_datos():
    if not os.path.exists("historial_multi.json"):
        return {}
    with open("historial_multi.json", "r") as f:
        return json.load(f)

def enviar_discord(mensaje, color=None):
    if "PEGA_AQUI" in WEBHOOK_URL or "TU_WEBHOOK" in WEBHOOK_URL: return
    
    # Si no se especifica color, usar gris (sin cambios) o rojo (cambios)
    # Aquí usamos un embed simple para que se vea más ordenado
    data = {
        "username": "IG Monitor",
        "content": mensaje
    }
    try: requests.post(WEBHOOK_URL, json=data)
    except: pass

# --- INICIO ---
print("--- Ejecución Iniciada ---")
L = instaloader.Instaloader()
base_datos = cargar_base_datos()

hora_actual = datetime.now().strftime("%H:%M")

for usuario in LISTA_USUARIOS:
    try:
        # Pausa aleatoria
        time.sleep(random.randint(5, 10)) 
        
        print(f"Revisando a: {usuario}...")
        profile = instaloader.Profile.from_username(L.context, usuario)
        nuevos = {"seguidores": profile.followers, "seguidos": profile.followees}
        
        msg = ""
        
        if usuario not in base_datos:
            base_datos[usuario] = nuevos
            msg = f"🆕 **{usuario}** agregado a la base de datos.\n📊 Seguidores: {nuevos['seguidores']} | Seguidos: {nuevos['seguidos']}"
        else:
            viejos = base_datos[usuario]
            cambios_detectados = False
            
            detalles_cambio = ""
            
            # Calcular diferencias
            diff_followers = nuevos['seguidores'] - viejos['seguidores']
            if diff_followers != 0:
                detalles_cambio += f"📈 **Seguidores:** {viejos['seguidores']} ➡ {nuevos['seguidores']} ({diff_followers:+})\n"
                cambios_detectados = True
                
            diff_followees = nuevos['seguidos'] - viejos['seguidos']
            if diff_followees != 0:
                detalles_cambio += f"👀 **Seguidos:** {viejos['seguidos']} ➡ {nuevos['seguidos']} ({diff_followees:+})\n"
                cambios_detectados = True
            
            # Construir el mensaje final
            if cambios_detectados:
                msg = f"🚨 **CAMBIOS EN {usuario}** ({hora_actual}):\n{detalles_cambio}"
                # Actualizamos la DB solo si hubo cambios
                base_datos[usuario] = nuevos
            else:
                # Mensaje de "Sin cambios"
                msg = f"✅ **{usuario}**: Sin novedades.\n(Seguidores: {nuevos['seguidores']} | Seguidos: {nuevos['seguidos']})"
        
        # Enviamos el mensaje SIEMPRE
        enviar_discord(msg)
                
    except Exception as e:
        error_msg = f"⚠️ **Error revisando {usuario}**: {str(e)}"
        print(error_msg)
        enviar_discord(error_msg)

guardar_base_datos(base_datos)

print("--- Fin de la ejecución ---")

