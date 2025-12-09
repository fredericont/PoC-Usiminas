import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from transformers import pipeline
from PIL import Image
import torch
import sys

class DeepVolumeEstimator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_cv2 = cv2.imread(image_path)
        self.img_rgb = cv2.cvtColor(self.img_cv2, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(self.img_rgb)
        self.depth_map = None
        self.mask = None
        self.pixel_scale_m = 0.05 # Caso não haja valor no input, será usado 0.05

        print("Carregando modelo Depth Anything V2... (pode demorar na 1ª vez)")
        # Verifica se tem GPU disponível
        device = 0 if torch.cuda.is_available() else -1
        print(f"Usando dispositivo: {'GPU' if device == 0 else 'CPU'}")
        
        try:
            # Carrega o pipeline de estimativa de profundidade
            self.pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=device)
        except Exception as e:
            print(f"\nErro ao carregar o modelo: {e}")
            print("Verifique sua conexão ou instalação do PyTorch/Transformers.")
            sys.exit(1)

    def gerar_mapa_profundidade(self):
        print("Gerando mapa de profundidade...")
        # A inferência retorna um dicionário com a chave 'depth'
        output = self.pipe(self.pil_image)
        depth_pil = output["depth"]
        
        # Converter para numpy array e normalizar para 0-1
        depth_np = np.array(depth_pil, dtype=np.float32)
        
        # Depth Anything retorna "inverse depth" (perto é claro/alto). 
        self.depth_map = 1.0 - (depth_np - depth_np.min()) / (depth_np.max() - depth_np.min())
        
        plt.figure(figsize=(10, 5))
        plt.imshow(self.depth_map, cmap='magma')
        plt.title("Mapa de Elevação Relativa")
        plt.colorbar(label="Altura Relativa (0=Chão, 1=Perto/Alto)")
        plt.show()

    def criar_mascara_pilha(self):
        print("\n--- DELIMITAÇÃO DA PILHA ---")
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(self.img_rgb)
        ax.set_title("Clique para contornar EXATAMENTE a base da pilha. ENTER para finalizar.")
        
        pontos = plt.ginput(n=-1, timeout=-1)
        plt.close()
        
        if len(pontos) < 3:
            print("Erro: Polígono inválido.")
            sys.exit(1)
            
        # Criar máscara binária a partir do polígono
        h, w = self.depth_map.shape
        mask_img = np.zeros((h, w), dtype=np.uint8)
        pts_np = np.array(pontos, dtype=np.int32)
        cv2.fillPoly(mask_img, [pts_np], 255)
        self.mask = mask_img > 0 # Booleano

        # Visualizar máscara aplicada ao depth map
        masked_depth = self.depth_map.copy()
        masked_depth[~self.mask] = 0
        plt.figure(figsize=(10, 5))
        plt.imshow(masked_depth, cmap='terrain')
        plt.title("Mapa de Elevação Isolado da Pilha")
        plt.show()

    def calcular_volume_calibrado(self):
        if self.depth_map is None or self.mask is None:
            print("Execute gerar_mapa_profundidade e criar_mascara_pilha primeiro.")
            return

        # 1. Isolar os valores de profundidade dentro da máscara
        pilha_depth_values = self.depth_map[self.mask]
        
        # 2. Encontrar o "chão" da pilha (valor mínimo dentro da área demarcada)
        base_level = pilha_depth_values.min()
        peak_level_relative = pilha_depth_values.max()

        # 3. Normalizar a pilha para que a base seja 0
        pilha_normalized = pilha_depth_values - base_level
        peak_normalized = peak_level_relative - base_level
        
        print(f"\n--- CALIBRAÇÃO FÍSICA ---")
        print("A IA detectou o formato, mas não sabe o tamanho real.")
        try:
            # Input: Altura Real
            h_real_max = float(input(f"Qual a altura MÁXIMA aproximada dessa pilha no mundo real (em metros)? "))
            
            # Input: Escala do Pixel (GSD médio para a área da pilha)
            scale_input = float(input("Qual o tamanho médio do pixel nessa área (ex: digite 0.05 para 5cm/px)? "))
            self.pixel_scale_m = scale_input
            pixel_area_m2 = self.pixel_scale_m * self.pixel_scale_m
            
        except ValueError:
            print("Valores inválidos. Usando padrões (H=5m, GSD=0.05m). Resultado será impreciso.")
            h_real_max = 5.0
            pixel_area_m2 = 0.05 * 0.05

        # 4. Fator de conversão: (Altura Real Desejada) / (Altura Relativa da IA)
        height_scale_factor = h_real_max / peak_normalized
        
        # 5. Converter alturas relativas para metros reais
        pilha_heights_m = pilha_normalized * height_scale_factor

        # 6. Integração do Volume: Soma (Altura do Pixel * Área do Pixel)
        # Volume = Σ (h_i * GSD²)
        volume_m3 = np.sum(pilha_heights_m * pixel_area_m2)
        
        area_base_px = np.sum(self.mask)
        area_base_m2 = area_base_px * pixel_area_m2

        print("\n" + "="*40)
        print("RESULTADO DA ESTIMATIVA (Deep Learning)")
        print("="*40)
        print(f"Área da Base Projetada: {area_base_m2:.2f} m²")
        print(f"Altura Máxima Definida: {h_real_max:.2f} m")
        print(f"Altura Média da Pilha: {np.mean(pilha_heights_m):.2f} m")
        print("-" * 20)
        print(f"VOLUME TOTAL ESTIMADO: {volume_m3:.2f} m³")
        print(f"Massa Estimada (Densidade 2.98 t/m³): {volume_m3 * 2.98:.2f} toneladas")
        print("="*40)

if __name__ == "__main__":
    imagem_pilha = "foto_1_atual.png" 
    
    try:
        estimator = DeepVolumeEstimator(imagem_pilha)
        # Passo 1: Gerar o mapa de calor da profundidade
        estimator.gerar_mapa_profundidade()
        # Passo 2: Você desenha onde está a pilha
        estimator.criar_mascara_pilha()
        # Passo 3: Você informa a altura real e o GSD para calcular
        estimator.calcular_volume_calibrado()
        
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {imagem_pilha}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")