import cv2
import numpy as np
import torch
from lama_cleaner.model.lama import LaMa
from lama_cleaner.schema import Config
import os
from collections import deque

# --- Constantes e Variáveis globais ---
NOME_JANELA_ORIGINAL = "Editor de Imagem - Original"
NOME_JANELA_CORRIGIDA = "Editor de Imagem - Corrigida"
pontos_selecao = []
desenhando = False
img_em_edicao = None
img_original_full_res = None
img_original_display = None
fator_escala = 1.0
DIMENSAO_MAX_TELA = 900
historico_imagens = deque(maxlen=10)
modo_atual = "removedor"
mascara_clareamento = None
tamanho_pincel = 20
INTENSIDADE_PINCEL = 15

# --- Inicialização do Modelo de IA ---
print("Carregando o modelo de Inteligência Artificial...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")
try:
    model = LaMa(device=device)
    print("Modelo carregado com sucesso!")
except Exception as e:
    print(f"ERRO ao carregar o modelo: {e}"); exit()
config = Config(ldm_steps=25, hd_strategy="Crop", hd_strategy_crop_margin=196, hd_strategy_crop_trigger_size=800, hd_strategy_resize_limit=2048)

def redimensionar_para_exibicao(imagem):
    global fator_escala
    if imagem is None: return None
    altura, largura = imagem.shape[:2]
    if max(altura, largura) <= DIMENSAO_MAX_TELA:
        fator_escala = 1.0
        return imagem
    if altura > largura: fator_escala = DIMENSAO_MAX_TELA / altura
    else: fator_escala = DIMENSAO_MAX_TELA / largura
    nova_largura = int(largura * fator_escala); nova_altura = int(altura * fator_escala)
    return cv2.resize(imagem, (nova_largura, nova_altura), interpolation=cv2.INTER_AREA)

def aplicar_clareamento(imagem, mascara):
    BRILHO_MAXIMO = 1.20
    REDUCAO_AMARELO_MAXIMA = 20
    mascara_normalizada = mascara.astype(float) / 255.0
    imagem_lab = cv2.cvtColor(imagem, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(imagem_lab)
    fator_brilho_mapa = 1.0 + (BRILHO_MAXIMO - 1.0) * mascara_normalizada
    fator_amarelo_mapa = REDUCAO_AMARELO_MAXIMA * mascara_normalizada
    l_clareado = cv2.convertScaleAbs(l, alpha=1.0) * fator_brilho_mapa
    b_sem_amarelo = b - fator_amarelo_mapa
    l_clareado = np.clip(l_clareado, 0, 255).astype("uint8")
    b_sem_amarelo = np.clip(b_sem_amarelo, 0, 255).astype("uint8")
    imagem_lab_clareada = cv2.merge([l_clareado, a, b_sem_amarelo])
    
    # --- LINHA CORRIGIDA AQUI ---
    imagem_bgr_clareada = cv2.cvtColor(imagem_lab_clareada, cv2.COLOR_LAB2BGR)
    
    mascara_3_canais = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)
    imagem_final = np.where(mascara_3_canais > 0, imagem_bgr_clareada, imagem)
    return imagem_final

def callback_mouse(evento, x, y, flags, param):
    global pontos_selecao, desenhando, img_em_edicao, img_original_display, modo_atual, mascara_clareamento

    if modo_atual == "removedor":
        if evento == cv2.EVENT_LBUTTONDOWN:
            pontos_selecao = [(x, y)]; desenhando = True
        elif evento == cv2.EVENT_MOUSEMOVE and desenhando:
            clone = img_original_display.copy()
            ponto_atual = (x, y); ponto_inicial = pontos_selecao[0]
            centro = (int((ponto_inicial[0] + ponto_atual[0]) / 2), int((ponto_inicial[1] + ponto_atual[1]) / 2))
            raio = int(((ponto_atual[0] - ponto_inicial[0])**2 + (ponto_atual[1] - ponto_inicial[1])**2)**0.5 / 2)
            overlay = clone.copy(); cv2.circle(overlay, centro, raio, (0, 255, 0), -1)
            cv2.addWeighted(overlay, 0.3, clone, 0.7, 0, clone); cv2.circle(clone, centro, raio, (0, 255, 0), 1)
            cv2.imshow(NOME_JANELA_ORIGINAL, clone)
        elif evento == cv2.EVENT_LBUTTONUP and desenhando:
            desenhando = False; pontos_selecao.append((x, y))
            ponto1_orig = (int(pontos_selecao[0][0] / fator_escala), int(pontos_selecao[0][1] / fator_escala))
            ponto2_orig = (int(pontos_selecao[1][0] / fator_escala), int(pontos_selecao[1][1] / fator_escala))
            raio_orig = int(((ponto2_orig[0] - ponto1_orig[0])**2 + (ponto2_orig[1] - ponto1_orig[1])**2)**0.5 / 2)
            if raio_orig == 0: return
            centro_orig = (int((ponto1_orig[0] + ponto2_orig[0]) / 2), int((ponto1_orig[1] + ponto2_orig[1]) / 2))
            mascara_temp = np.zeros(img_original_full_res.shape[:2], dtype="uint8")
            cv2.circle(mascara_temp, centro_orig, raio_orig, 255, -1)
            print("Processando com IA..."); historico_imagens.append(img_em_edicao.copy())
            img_para_ia_rgb = cv2.cvtColor(img_em_edicao, cv2.COLOR_BGR2RGB)
            img_corrigida_bgr = model(img_para_ia_rgb, mascara_temp, config)
            img_em_edicao = img_corrigida_bgr; print("Correção aplicada!")
    
    elif modo_atual == "clareamento":
        if evento == cv2.EVENT_LBUTTONDOWN: desenhando = True
        elif evento == cv2.EVENT_LBUTTONUP: desenhando = False
        if desenhando:
            x_orig = int(x / fator_escala); y_orig = int(y / fator_escala)
            cv2.circle(mascara_clareamento, (x_orig, y_orig), tamanho_pincel, (INTENSIDADE_PINCEL), -1, cv2.LINE_AA)

# --- Programa Principal ---
caminho_imagem = "C:\\Users\\leosz\\Downloads\\WhatsApp Image 2025-09-16 at 18.46.43.jpeg"
img_original_full_res = cv2.imread(caminho_imagem)

if img_original_full_res is None:
    print(f"ERRO: Não foi possível carregar a imagem. Verifique o caminho: {caminho_imagem}")
else:
    img_original_display = redimensionar_para_exibicao(img_original_full_res)
    img_em_edicao = img_original_full_res.copy()
    mascara_clareamento = np.zeros(img_original_full_res.shape[:2], dtype="uint8")
    
    cv2.namedWindow(NOME_JANELA_ORIGINAL)
    cv2.setMouseCallback(NOME_JANELA_ORIGINAL, callback_mouse)
    cv2.namedWindow(NOME_JANELA_CORRIGIDA)

    print("\n--- INSTRUÇÕES ---")
    print("Use a tecla 't' para alternar entre os modos.")
    print("\nMODO REMOVEDOR (padrão):")
    print(" - Clique e arraste para remover imperfeições com IA.")
    print("\nMODO PINCEL (Clareamento):")
    print(" - Clique e arraste para PINTAR a área a ser clareada.")
    print(" - Quanto mais você pinta, mais forte o efeito.")
    print(" - Teclas '[' e ']': Diminui/Aumenta o tamanho do pincel.")
    print(" - Tecla 'a': APLICA o clareamento que você pintou.")
    print(" - Tecla 'c': LIMPA a sua pintura.")
    print("--------------------------------------------------")
    print(" 's' -> Salvar | 'r' -> Resetar | 'z' -> Desfazer | 'q' -> Sair")
    print("--------------------------------------------------\n")

    while True:
        display_frame = img_original_display.copy()
        if modo_atual == "clareamento":
            mascara_display = cv2.resize(mascara_clareamento, (display_frame.shape[1], display_frame.shape[0]))
            overlay = np.zeros_like(display_frame)
            overlay[mascara_display > 0] = (0, 255, 0)
            cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0, display_frame)

        cv2.imshow(NOME_JANELA_ORIGINAL, display_frame)
        cv2.imshow(NOME_JANELA_CORRIGIDA, redimensionar_para_exibicao(img_em_edicao))
        
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"): break
        elif tecla == ord("t"):
            modo_atual = "clareamento" if modo_atual == "removedor" else "removedor"
            desenhando = False
            novo_titulo = f"{NOME_JANELA_ORIGINAL} - Modo: {modo_atual.capitalize()}"
            cv2.setWindowTitle(NOME_JANELA_ORIGINAL, novo_titulo)
            print(f"Modo alterado para: {modo_atual}")
        elif tecla == ord("c"):
            if modo_atual == "clareamento":
                mascara_clareamento.fill(0); print("Máscara de clareamento limpa.")
        elif tecla == ord("a"):
             if modo_atual == "clareamento":
                print("Aplicando clareamento..."); historico_imagens.append(img_em_edicao.copy())
                img_em_edicao = aplicar_clareamento(img_em_edicao, mascara_clareamento)
                mascara_clareamento.fill(0)
                print("Clareamento aplicado!")
        elif tecla == ord("["):
            if modo_atual == "clareamento":
                tamanho_pincel = max(5, tamanho_pincel - 5); print(f"Tamanho do pincel: {tamanho_pincel}")
        elif tecla == ord("]"):
            if modo_atual == "clareamento":
                tamanho_pincel = min(100, tamanho_pincel + 5); print(f"Tamanho do pincel: {tamanho_pincel}")
        elif tecla == ord("r"):
            print("Resetando imagem..."); historico_imagens.clear(); mascara_clareamento.fill(0)
            img_em_edicao = img_original_full_res.copy()
        elif tecla == ord("s"):
            base, ext = os.path.splitext(caminho_imagem)
            nome_arquivo_saida = f"{base}_corrigido_IA{ext}"
            cv2.imwrite(nome_arquivo_saida, img_em_edicao); print(f"Imagem salva como '{nome_arquivo_saida}'!")
        elif tecla == ord("z"):
            if historico_imagens:
                img_em_edicao = historico_imagens.pop(); mascara_clareamento.fill(0)
                print("Última alteração desfeita!")
            else:
                print("Nada para desfazer.")
    cv2.destroyAllWindows()