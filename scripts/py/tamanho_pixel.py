import matplotlib.pyplot as plt
from PIL import Image
import math

def medir_pixel_interativo(caminho_imagem):
    # Carregar imagem
    img = Image.open(caminho_imagem)
    
    # Plotar imagem
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(img)
    plt.title("Clique no INÍCIO e no FIM do objeto de referência")
    
    # Permitir que o usuário clique em 2 pontos
    # ginput(2) espera 2 cliques e retorna uma lista de tuplas [(x1, y1), (x2, y2)]
    pontos = plt.ginput(2)
    plt.close() # Fecha a janela após os cliques
    
    if len(pontos) < 2:
        print("Você não selecionou os dois pontos.")
        return

    p1, p2 = pontos
    print(f"Ponto 1: {p1}, Ponto 2: {p2}")

    # Calcular distância em pixels (Pitágoras)
    dist_pixels = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    print(f"Distância na imagem: {dist_pixels:.2f} pixels")

    # Pedir o tamanho real ao usuário
    try:
        tamanho_real = float(input("Qual o tamanho real desse objeto (ex: digite 30 para 30cm)? "))
        unidade = input("Qual a unidade de medida (cm, mm, m)? ")
    except ValueError:
        print("Valor inválido inserido.")
        return

    # Cálculo Final
    tamanho_pixel = tamanho_real / dist_pixels

    print("\n--- RESULTADO ---")
    print(f"Fator de Escala: 1 pixel = {tamanho_pixel:.5f} {unidade}")
    print("-" * 20)
    
    return tamanho_pixel

# Para usar, apenas chame a função com o nome da sua foto:
medir_pixel_interativo("foto_1_atual.png")