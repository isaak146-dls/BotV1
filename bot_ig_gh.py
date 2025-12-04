import instaloader
import json
import os
import requests
import random
import time

# --- CONFIGURACIÓN ---
LISTA_USUARIOS = ["m0ritaav", "fresaskoncremq", "yazminsitq", "exorcismxq", "__isaakm__"] 
WEBHOOK_URL = "https://discord.com/api/webhooks/1446185382793183416/hiIK0y8-YEqVIXeAUV1jxRagEwFb_jBIqd1wfUl_ZguoYtKg51wTCZyI5I0oCNC7dxtF" # <--- PON TU URL DISCORD

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
    data = {"content": mensaje, "username": "IG Bot Cloud"}
    try: requests.post(WEBHOOK_URL, json=data)
    except: pass

# --- INICIO (SIN BUCLE WHILE) ---
print("--- Ejecución en Nube Iniciada ---")
L = instaloader.Instaloader()
base_datos = cargar_base_datos()

for usuario in LISTA_USUARIOS:
    try:
        # Pausa aleatoria pequeña para simular humano
        time.sleep(random.randint(5, 10)) 
        
        profile = instaloader.Profile.from_username(L.context, usuario)
        nuevos = {"seguidores": profile.followers, "seguidos": profile.followees}
        
        if usuario not in base_datos:
            base_datos[usuario] = nuevos
            print(f"Nuevo: {usuario}")
        else:
            viejos = base_datos[usuario]
            cambio = False
            msg = f"📢 **{usuario}:**\n"
            
            diff = nuevos['seguidores'] - viejos['seguidores']
            if diff != 0:
                msg += f"Seguidores: {viejos['seguidores']} -> {nuevos['seguidores']} ({diff})\n"
                cambio = True
                
            diff_seg = nuevos['seguidos'] - viejos['seguidos']
            if diff_seg != 0:
                msg += f"Seguidos: {viejos['seguidos']} -> {nuevos['seguidos']}\n"
                cambio = True
            
            if cambio:
                enviar_discord(msg)
                base_datos[usuario] = nuevos
                
    except Exception as e:
        print(f"Error con {usuario}: {e}")

guardar_base_datos(base_datos)
print("--- Fin de la ejecución ---")