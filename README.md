# Mapeamento de Enchentes no Rio Grande do Sul — 2024

Projeto desenvolvido na disciplina de **Sistemas de Informação Geográfica (SIG)**, com o objetivo de realizar uma análise espacial das áreas afetadas pelas enchentes ocorridas no Rio Grande do Sul em 2024.

A aplicação utiliza dados geoespaciais, informações de abrigos e técnicas de análise espacial para identificar municípios afetados, calcular o percentual de área inundada e disponibilizar os resultados em um **mapa interativo**.

## Sobre o projeto

Entre abril e maio de 2024, o Rio Grande do Sul enfrentou um dos maiores eventos de enchentes registrados no estado. Diante da grande extensão territorial afetada, o projeto busca utilizar geotecnologias e dados espaciais para representar e analisar os impactos do desastre.

O trabalho integra dados de diferentes fontes e transforma essas informações em uma visualização geográfica interativa.

## Objetivos

### Objetivo geral

Desenvolver um mapa interativo e dinâmico para visualização e análise das áreas afetadas pelas enchentes no Rio Grande do Sul durante o ano de 2024.

### Objetivos específicos

* Coletar e tratar dados geoespaciais relacionados às enchentes;
* Identificar os municípios afetados;
* Calcular o percentual de área afetada em cada município;
* Identificar os municípios com maior percentual de área inundada;
* Integrar dados de sensoriamento remoto e bases geográficas;
* Mapear abrigos utilizados durante a crise;
* Disponibilizar as informações em um mapa interativo.

## Metodologia

O fluxo de análise foi dividido em quatro etapas principais:

1. **Carregamento e integração dos dados**

   * Importação das bases geoespaciais;
   * Carregamento dos municípios do Rio Grande do Sul;
   * Importação das áreas de inundação;
   * Carregamento dos dados de abrigos.

2. **Análise espacial**

   * Conversão dos dados para um sistema de coordenadas projetado;
   * Interseção entre as áreas inundadas e os municípios;
   * Cálculo da área afetada em cada município.

3. **Classificação por impacto**

   Os municípios são classificados de acordo com o percentual de sua área afetada:

   | Classificação | Percentual afetado |
   | ------------- | -----------------: |
   | Crítico       |              > 50% |
   | Alto          |          20% – 50% |
   | Médio         |           5% – 20% |
   | Baixo         |               < 5% |

4. **Visualização**

   * Criação de mapa interativo;
   * Áreas inundadas;
   * Municípios afetados;
   * Marcadores com informações dos municípios;
   * Ranking dos 10 municípios mais afetados;
   * Abrigos ativos;
   * Quantidade de pessoas abrigadas;
   * Informações sobre aceitação de pets.

## Tecnologias utilizadas

* **Python**
* **GeoPandas** — manipulação e análise de dados geoespaciais
* **Pandas** — processamento de dados tabulares
* **Folium** — criação do mapa interativo
* **MarkerCluster** — agrupamento de marcadores
* **OpenStreetMap** — mapa base
* **Esri World Imagery** — camada de imagens de satélite
* **GeoPackage (GPKG)** — armazenamento dos dados geoespaciais
* **CSV** — dados dos abrigos
* **HTML** — resultado final interativo

## Estrutura do projeto

```text
├── codigo final.py
├── mapa_enchentes_rs_2024_final.html
└── README.md
```

> As bases geoespaciais utilizadas no processamento não estão incluídas neste repositório devido ao tamanho dos arquivos. Elas devem ser obtidas a partir das fontes indicadas na seção de dados.

## Dados utilizados

### Região do Lago Guaíba

Base de dados das cheias na Região Hidrográfica do Lago Guaíba em maio de 2024, disponibilizada no Zenodo.

Os dados incluem informações obtidas por sensoriamento remoto, modelos digitais de terreno e elevação e dados coletados em campo.

### Lagoa dos Patos

Base de dados da inundação na Região da Lagoa dos Patos em maio de 2024, disponibilizada no OSF.

### Dados de abrigos

Foram utilizados dados de localização e situação dos abrigos, incluindo:

* Latitude e longitude;
* Cidade;
* Endereço;
* Quantidade de pessoas abrigadas;
* Aceitação de pets;
* Última atualização.

## Resultado

O resultado principal do projeto é um **mapa interativo em HTML**, permitindo ativar e desativar diferentes camadas de informação.

O mapa apresenta:

* Áreas inundadas;
* Municípios afetados;
* Percentual de área afetada;
* Ranking dos 10 municípios mais afetados;
* Abrigos ativos;
* Quantidade de pessoas em cada abrigo;
* Abrigos que aceitam pets;
* Visualização em mapa convencional ou satélite;
* Controle de camadas;
* Mini mapa;
* Ferramenta de medição;
* Modo tela cheia.

### Estatísticas do mapa

De acordo com a aplicação desenvolvida:

* **113 municípios afetados**
* **303 abrigos ativos**
* **59.382 pessoas abrigadas**
* **616 abrigos sem pessoas registrados**

## Como executar

### 1. Instalar as bibliotecas

```bash
pip install folium pandas geopandas
```

### 2. Baixar as bases de dados

Obtenha os arquivos geoespaciais e o arquivo CSV utilizados no projeto e coloque-os em um diretório local.

O código utiliza os seguintes arquivos:

```text
cheias_rhguaiba_2024_db_v5.gpkg
sig_inundacao.gpkg
rs_crise_abrigos_24052024_20h.csv
```

### 3. Configurar o diretório

No arquivo `codigo final.py`, altere a variável:

```python
DIRETORIO_BASE = r"C:\Users\Sabrina\Desktop\mapa rs\\"
```

para o caminho onde os arquivos foram armazenados no seu computador.

### 4. Executar o código

```bash
python "codigo final.py"
```

Após a execução, será gerado o arquivo:

```text
mapa_enchentes_rs_2024_final.html
```

O arquivo HTML pode ser aberto diretamente em um navegador.

## Mapa interativo

O projeto já possui uma versão final do mapa em HTML:

**[Abrir mapa interativo](file:///C:/Users/DELL/Downloads/projeto%20sig/mapa_enchentes_rs_2024_final.html)**

## Fontes

* IBGE — Malhas Territoriais.
* Possantti, I.; Müller, J.; Ruhoff, A. (2024). *Cheias no Rio Grande do Sul — Base de dados e informações geográficas na Região Hidrográfica do Lago Guaíba e na Lagoa dos Patos em 2024*. UFRGS.
* Possantti, I. (2024). *Banco de dados das cheias na Região Hidrográfica do Lago Guaíba em Maio de 2024*. Zenodo. DOI: [10.5281/zenodo.11185049](https://doi.org/10.5281/zenodo.11185049).
* da Silva, T. S. et al. (2024). *Base de dados da inundação na Região da Lagoa dos Patos em Maio de 2024*. OSF. DOI: [10.17605/OSF.IO/9WR5C](https://doi.org/10.17605/OSF.IO/9WR5C).

## Autores

**Larissa, Sabrina e Ester**

Curso de **Sistemas de Informação — UDESC**

Projeto desenvolvido na disciplina de **Sistemas de Informação Geográfica (SIG)**.

Professor: **Luiz Cláudio Dalmolin**
