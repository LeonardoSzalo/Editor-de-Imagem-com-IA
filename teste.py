import cv2
import numpy as np
import torch
from lama_cleaner.model.lama import LaMa
from lama_cleaner.schema import Config

# --- CONFIGURAÇÃO ---
# Altere para o caminho da sua imagem
caminho_imagem = "C:\\Users\\leosz\\Downloads\\WhatsApp Image 2025-09-13 at 14.04.57.jpeg" 
device = "cpu" # Usando CPU para garantir consistência

# --- SCRIPT ---
print("Iniciando script de diagnóstico (versão corrigida)...")
print(f"Usando dispositivo: {device}")

# 1. Carregar modelo
try:
    model = LaMa(device=device)
    # CORREÇÃO APLICADA AQUI: Adicionando todos os parâmetros necessários ao Config
    config = Config(
        ldm_steps=25,
        hd_strategy="Crop",
        hd_strategy_crop_margin=196,
        hd_strategy_crop_trigger_size=800,
        hd_strategy_resize_limit=2048,
    )
    print("Modelo carregado.")
except Exception as e:
    print(f"Erro ao carregar modelo: {e}")
    exit()

# 2. Carregar imagem
img_bgr = cv2.imread(caminho_imagem)
if img_bgr is None:
    print("Erro ao carregar imagem.")
    exit()
print("Imagem carregada.")

# 3. Criar uma máscara de teste (um quadrado no centro)
h, w = img_bgr.shape[:2]
mask = np.zeros((h, w), dtype=np.uint8)
start_point = (w // 4, h // 8)
end_point = (w * 3 // 4, h * 7 // 8)
cv2.rectangle(mask, start_point, end_point, 255, -1)
print("Máscara de teste criada.")

# 4. Processar a imagem
print("Processando com o modelo LaMa...")
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
resultado_do_modelo = model(img_rgb, mask, config)
print("Processamento concluído.")

# 5. Salvar os resultados para análise
resultado_corrigido_para_bgr = cv2.cvtColor(resultado_do_modelo, cv2.COLOR_RGB2BGR)
cv2.imwrite("resultado_corrigido.jpg", resultado_corrigido_para_bgr)
cv2.imwrite("resultado_direto.jpg", resultado_do_modelo) 

print("\nDiagnóstico concluído!")
print("Dois arquivos foram salvos no mesmo diretório do script:")
print("1. 'resultado_corrigido.jpg'")
print("2. 'resultado_direto.jpg'")
print("Por favor, verifique os dois arquivos.")