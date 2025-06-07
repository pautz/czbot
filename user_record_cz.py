import pyautogui
import keyboard
import time
import json
import xml.etree.ElementTree as ET
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key

eventos = []
tempo_anterior = None

def normalizar_botao(botao):
    return {"Button.left": "left", "Button.right": "right", "Button.middle": "middle"}.get(botao, "left")

def normalizar_tecla(tecla):
    if isinstance(tecla, Key):  
        return tecla.name
    return tecla.char if hasattr(tecla, "char") else str(tecla)

def on_click(x, y, button, pressed):
    global tempo_anterior
    if pressed:
        tempo_atual = time.time()
        intervalo = tempo_atual - tempo_anterior if tempo_anterior else 0
        tempo_anterior = tempo_atual
        eventos.append({"tipo": "mouse", "x": x, "y": y, "botao": normalizar_botao(str(button)), "intervalo": intervalo})

def on_press(key):
    global tempo_anterior
    tempo_atual = time.time()
    intervalo = tempo_atual - tempo_anterior if tempo_anterior else 0
    tempo_anterior = tempo_atual
    eventos.append({"tipo": "teclado", "tecla": normalizar_tecla(key), "intervalo": intervalo})

def salvar_em_json(nome_arquivo):
    with open(f"{nome_arquivo}.json", "w") as arquivo:
        json.dump(eventos, arquivo)

def salvar_em_xml(nome_arquivo):
    root = ET.Element("eventos")
    for evento in eventos:
        e = ET.SubElement(root, "evento", tipo=evento["tipo"])
        ET.SubElement(e, "intervalo").text = str(evento["intervalo"])
        if evento["tipo"] == "mouse":
            ET.SubElement(e, "x").text = str(evento["x"])
            ET.SubElement(e, "y").text = str(evento["y"])
            ET.SubElement(e, "botao").text = evento["botao"]
        elif evento["tipo"] == "teclado":
            ET.SubElement(e, "tecla").text = evento["tecla"]
    
    tree = ET.ElementTree(root)
    tree.write(f"{nome_arquivo}.xml")

def carregar_de_xml(nome_arquivo):
    try:
        tree = ET.parse(nome_arquivo)
        root = tree.getroot()
        eventos.clear()
        for e in root.findall("evento"):
            evento = {"tipo": e.get("tipo"), "intervalo": float(e.find("intervalo").text)}
            if evento["tipo"] == "mouse":
                evento.update({"x": int(e.find("x").text), "y": int(e.find("y").text), "botao": e.find("botao").text})
            elif evento["tipo"] == "teclado":
                evento.update({"tecla": e.find("tecla").text})
            eventos.append(evento)
    except FileNotFoundError:
        print("❌ Arquivo XML não encontrado!")

def gravar_eventos(nome_arquivo):
    global eventos, tempo_anterior
    eventos = []
    tempo_anterior = time.time()
    
    print("🔴 Pressione 'End' para começar a gravação.")
    while not keyboard.is_pressed("end"):
        time.sleep(0.01)

    print("🔴 Gravando... Pressione 'Delete' para parar.")
    with MouseListener(on_click=on_click) as mouse_listener, KeyboardListener(on_press=on_press):
        while not keyboard.is_pressed("delete"):
            time.sleep(0.01)

    print("⏹ Gravação finalizada.")
    salvar_em_json(nome_arquivo)
    salvar_em_xml(nome_arquivo)

def reproduzir_eventos(nome_arquivo):
    carregar_de_xml(f"{nome_arquivo}.xml")

    print("▶️ Executando movimentos... Pressione 'Delete' para parar.")
    while not keyboard.is_pressed("delete"):  
        for evento in eventos:
            time.sleep(evento["intervalo"])  

            if evento["tipo"] == "teclado":
                if evento["tecla"]:
                    keyboard.press_and_release(evento["tecla"])
            elif evento["tipo"] == "mouse":
                pyautogui.click(evento["x"], evento["y"], button=evento["botao"])  

    print("⏹ Reprodução interrompida.")

def menu():
    escolha = input("📁 Deseja 1️⃣ Importar XML ou 2️⃣ Gravar uma nova sequência? (1/2): ")
    if escolha == "1":
        nome_arquivo = input("🗂 Digite o nome do arquivo XML para importar: ")
        reproduzir_eventos(nome_arquivo)
    elif escolha == "2":
        nome_arquivo = input("💾 Digite o nome para salvar: ")
        gravar_eventos(nome_arquivo)
    else:
        print("❌ Escolha inválida, tente novamente.")
        menu()

menu()
