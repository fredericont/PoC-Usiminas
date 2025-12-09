# PoC - Monitoramento Volumétrico de Minério (Computer Vision)

Este repositório contém os códigos e notebooks desenvolvidos no âmbito da Prova de Conceito (PoC) realizada pela **Quality Digital** para a **Usiminas**.

## Objetivo do Projeto

Validar a viabilidade técnica da utilização de algoritmos de Visão Computacional e Inteligência Artificial para monitorar pilhas de minério em tempo real, utilizando a infraestrutura de câmeras de segurança (CCTV) já existentes. A solução visa automatizar a extração de métricas operacionais críticas, reduzindo a dependência de medições topográficas manuais frequentes.

## Funcionalidades Principais

A solução atual permite:

* **Estimativa Volumétrica:** Cálculo de volume ($m^3$) e massa (toneladas) a partir de uma única imagem 2D.
* **Segmentação Inteligente:** Delimitação da área da pilha utilizando o modelo **SAM (Segment Anything)**.
* **Mapa de Profundidade:** Geração de mapas 3D relativos utilizando Deep Learning para entender a topografia da pilha.
* **Calibração de Escala:** Definição da relação *metros/pixel* utilizando objetos de referência na cena.

## Tecnologias Utilizadas

* **Linguagem:** Python
* **Segmentação:** Segment Anything Model (SAM) - Meta AI
* **Profundidade (Depth):** Depth Anything V2 (Hugging Face)
* **Processamento de Imagem:** OpenCV e PIL
* **Cálculo e Visualização:** NumPy e Matplotlib