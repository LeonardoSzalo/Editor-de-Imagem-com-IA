# Editor de Imagem com IA: Remoção de Objetos e Clareamento

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-1.10%2B-orange.svg)

Um editor de imagem interativo desenvolvido em Python com OpenCV, que utiliza o poder da Inteligência Artificial para remover objetos e imperfeições de fotos, além de oferecer uma ferramenta de pincel para clareamento de áreas específicas, como dentes.

## Demonstração

<img width="1200" height="1200" alt="Design sem nome" src="https://github.com/user-attachments/assets/5fb55a2b-dbed-4398-9a79-b1975d64aa08" />



## Funcionalidades Principais

* **Removedor de Imperfeições (IA):** Utiliza o modelo de *inpainting* **LaMa (Large Mask Inpainting)** para remover objetos ou defeitos indesejados da imagem. Basta selecionar a área com um círculo e a IA reconstrói o fundo de forma inteligente.
* **Pincel de Clareamento:** Um modo de edição manual que permite "pintar" sobre uma área da imagem (como dentes amarelados) para aplicar um efeito de clareamento e redução de tons amarelos. A intensidade do efeito aumenta conforme a área é pintada.
* **Interface Interativa:** Controle total através do mouse e de atalhos do teclado, com janelas separadas para a imagem original e a imagem corrigida.
* **Recursos de Edição:** Salve as alterações, desfaça a última ação (`Ctrl+Z`), resete a imagem para o estado original e alterne facilmente entre os modos de edição.

## Tecnologias Utilizadas

* **Python:** Linguagem principal do projeto.
* **OpenCV (`opencv-python`):** Para manipulação de imagens, criação da interface gráfica e processamento em tempo real.
* **PyTorch:** Framework de deep learning utilizado para executar o modelo de IA.
* **NumPy:** Para operações numéricas e manipulação de arrays de imagem.
* **LaMa Cleaner:** Biblioteca que implementa o modelo de inpainting para a remoção de objetos.

## Instalação e Execução

Siga os passos abaixo para executar o projeto em sua máquina local.

**1. Pré-requisitos:**
* Python 3.8 ou superior.
* `pip` (gerenciador de pacotes do Python).

**2. Clone o Repositório:**
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

**3. Crie um Ambiente Virtual (Recomendado):**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**4. Instale as Dependências:**
```bash
pip install -r requirements.txt
```
*Observação: Na primeira vez que você executar o script, a biblioteca `lama-cleaner` fará o download do modelo de IA. Isso pode levar alguns minutos e requer uma conexão com a internet.*

**5. Configure a Imagem:**
Abra o arquivo `editor.py` e altere a variável `caminho_imagem` para o caminho da imagem que você deseja editar:
```python
# --- Programa Principal ---
caminho_imagem = "caminho/para/sua/imagem.jpg"
```

**6. Execute o Script:**
```bash
python editor.py
```

## Como Usar

Após iniciar o programa, duas janelas serão abertas: a original (à esquerda) e a corrigida (à direita). A janela da esquerda é onde você interage.

### Controles Gerais
* **`t`**: Alterna entre os modos **Removedor** e **Clareamento**.
* **`s`**: Salva a imagem editada no mesmo diretório da original, com o sufixo `_corrigido_IA`.
* **`z`**: Desfaz a última alteração aplicada (funciona tanto para a remoção quanto para o clareamento).
* **`r`**: Reseta a imagem, descartando todas as alterações.
* **`q`**: Fecha o programa.

### Modo Removedor (Padrão)
1.  **Clique e arraste** o mouse sobre a área que deseja remover.
2.  Um círculo verde indicará a seleção.
3.  **Solte o botão do mouse**. A IA processará a imagem e removerá o objeto selecionado.

### Modo Clareamento
1.  Pressione **`t`** para entrar no modo de clareamento.
2.  **Clique e arraste** o mouse sobre a área que deseja clarear (ex: dentes). Uma sobreposição verde indicará a área pintada.
3.  **Controle o Pincel:**
    * **`[`**: Diminui o tamanho do pincel.
    * **`]`**: Aumenta o tamanho do pincel.
4.  **Aplique e Limpe:**
    * **`a`**: Aplica o efeito de clareamento na área pintada.
    * **`c`**: Limpa a seleção (a pintura verde) sem aplicar o efeito.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
