import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import numpy as np
import math

def calcular_distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def shoelace_area(points):
    """
    Calcula a área de um polígono baseado nas coordenadas (Shoelace Formula).
    Retorna a área em 'unidades quadradas' (pixels² neste contexto).
    """
    x = points[:, 0]
    y = points[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

def main_analise_area(caminho_imagem):
    # 1. Carregar imagem
    try:
        img = Image.open(caminho_imagem)
    except FileNotFoundError:
        print("Erro: Imagem não encontrada.")
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    
    print("\n--- PASSO 1: CALIBRAÇÃO ---")
    print("Clique nos 2 pontos do objeto de referência na imagem.")
    plt.title("CALIBRAÇÃO: Clique no Início e no Fim da referência")
    
    # Captura 2 pontos para calibração
    pontos_calib = plt.ginput(2)
    
    if len(pontos_calib) < 2:
        print("Calibração cancelada.")
        return

    # Desenha a linha de referência para visualização
    p1, p2 = pontos_calib
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=2)
    plt.draw() # Atualiza a tela

    dist_px = calcular_distancia(p1, p2)
    print(f"Distância em pixels: {dist_px:.2f}")

    # Input do usuário e normalização para Metros
    try:
        tamanho_ref = float(input("Qual o tamanho real do objeto? "))
        unidade = input("Qual a unidade (cm ou m)? ").lower().strip()
        
        # Converter tudo para METROS para facilitar o cálculo de m²
        if unidade == 'cm':
            tamanho_metros = tamanho_ref / 100.0
        else:
            tamanho_metros = tamanho_ref
            
    except ValueError:
        print("Valor inválido.")
        return

    # Fator de Escala (Metros por Pixel)
    metros_por_pixel = tamanho_metros / dist_px
    print(f"Fator de escala definido: {metros_por_pixel:.6f} m/px")

    # --- PASSO 2: DELIMITAÇÃO DA ÁREA ---
    print("\n--- PASSO 2: DELIMITAÇÃO DE ÁREA ---")
    print("Clique nos pontos para contornar a área desejada.")
    print("-> Pressione ENTER (ou botão do meio do mouse) para finalizar.")
    plt.title(f"ÁREA: Clique nos pontos do polígono (ENTER para fechar) | Escala: {metros_por_pixel:.4f} m/px")
    
    # timeout=-1 remove o limite de tempo, n=-1 permite infinitos cliques
    pontos_area = plt.ginput(n=-1, timeout=-1) 
    
    if len(pontos_area) < 3:
        print("É necessário pelo menos 3 pontos para formar uma área.")
        return

    # Converter para numpy array para facilitar cálculo
    pontos_np = np.array(pontos_area)

    # 2.1 Calcular área em PIXELS QUADRADOS
    area_px = shoelace_area(pontos_np)
    
    # 2.2 Converter para METROS QUADRADOS
    # Área Real = Área Pixels * (EscalaX * EscalaY) -> como é quadrado, Escala^2
    area_m2 = area_px * (metros_por_pixel ** 2)

    print("\n" + "="*30)
    print(f"Área em Pixels: {area_px:.2f} px²")
    print(f"ÁREA REAL CALCULADA: {area_m2:.4f} m²")
    print("="*30)

    # --- Visualização Final ---
    # Desenhar o polígono preenchido
    poly = Polygon(pontos_area, closed=True, facecolor='cyan', alpha=0.3, edgecolor='blue', linewidth=2)
    ax.add_patch(poly)
    
    # Adicionar texto no centroide aproximado
    centro_x = np.mean(pontos_np[:,0])
    centro_y = np.mean(pontos_np[:,1])
    ax.text(centro_x, centro_y, f"{area_m2:.2f} m²", color='white', fontsize=12, fontweight='bold', ha='center',
            bbox=dict(facecolor='black', alpha=0.7))

    plt.title(f"Resultado: {area_m2:.2f} m²")
    plt.show()

# --- Execução ---
main_analise_area("foto_1.png")