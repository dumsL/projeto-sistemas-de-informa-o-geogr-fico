import folium
import pandas as pd
import geopandas as gpd
from folium import plugins
from folium.plugins import MarkerCluster
import os

# ============================================
# 1. CONFIGURAÇÃO
# ============================================

print("=" * 80)
print("ANÁLISE ESPACIAL - ENCHENTES RIO GRANDE DO SUL - MAIO 2024")
print("=" * 80)

# Define o diretório base - CORRIGIDO PARA WINDOWS
DIRETORIO_BASE = r"C:\Users\Sabrina\Desktop\mapa rs\\"

# Arquivos
guaiba_path = DIRETORIO_BASE + "cheias_rhguaiba_2024_db_v5.gpkg"
patos_path = DIRETORIO_BASE + "sig_inundacao.gpkg"
abrigos_csv = DIRETORIO_BASE + "rs_crise_abrigos_24052024_20h.csv"

# Verificar se os arquivos existem
print("\n🔍 Verificando arquivos...")
print(f"Guaíba: {os.path.exists(guaiba_path)} - {guaiba_path}")
print(f"Patos: {os.path.exists(patos_path)} - {patos_path}")
print(f"Abrigos: {os.path.exists(abrigos_csv)} - {abrigos_csv}")

if not all([os.path.exists(guaiba_path), os.path.exists(patos_path), os.path.exists(abrigos_csv)]):
    print("\n⚠️ ERRO: Alguns arquivos não foram encontrados!")
    print("Verifique se os arquivos estão no diretório correto.")
    exit()

# ============================================
# 2. CARREGAR TODOS OS MUNICÍPIOS DO RS
# ============================================

print("\n📍 Carregando TODOS os municípios do Rio Grande do Sul...")
municipios_gdf = gpd.read_file(patos_path, layer="rs_municipios_2022")
print(f"✓ {len(municipios_gdf)} municípios do RS carregados")

# ============================================
# 3. CARREGAR BAIRROS DE PORTO ALEGRE
# ============================================

print("\n🏘️ Carregando bairros de Porto Alegre...")
bairros_gdf = gpd.read_file(guaiba_path, layer="poa_admin_bairros")
bairros_gdf = bairros_gdf.to_crs("EPSG:4326")
print(f"✓ {len(bairros_gdf)} bairros carregados")

# ============================================
# 4. CARREGAR ÁREAS DE INUNDAÇÃO
# ============================================

print("\n🌊 Carregando áreas de inundação...")

camadas_inundacao = [
    ("poa_inundacao_2024_530cm", "Porto Alegre 2024"),
    ("rhguaiba_sentinel2_agua_obs_06052024", "Região Guaíba"),
    ("rhguaiba-taquari_planet-skysat_inundacao_obs_06052024", "Bacia Taquari"),
]

areas_inundacao = []

for camada, nome in camadas_inundacao:
    try:
        gdf = gpd.read_file(guaiba_path, layer=camada)
        gdf = gdf.to_crs("EPSG:4326")
        areas_inundacao.append(gdf)
        print(f"  ✓ {nome}: {len(gdf)} polígonos")
    except Exception as e:
        print(f"  ⚠️ {nome}: {e}")

try:
    gdf_patos = gpd.read_file(patos_path, layer="cota273")
    areas_inundacao.append(gdf_patos)
    print(f"  ✓ Lagoa dos Patos: {len(gdf_patos)} polígonos")
except Exception as e:
    print(f"  ⚠️ Lagoa dos Patos: {e}")

print("\n🔄 Unindo áreas de inundação...")
inundacao_completa = gpd.GeoDataFrame(
    pd.concat(areas_inundacao, ignore_index=True),
    crs="EPSG:4326"
)
print(f"✓ Total de polígonos de inundação: {len(inundacao_completa)}")

# ============================================
# 5. CARREGAR DADOS DE ABRIGOS
# ============================================

print("\n🏠 Carregando dados de abrigos...")
try:
    df_abrigos = pd.read_csv(
        abrigos_csv,
        sep=';',
        encoding='utf-8',
        on_bad_lines='skip'
    )

    # Limpar dados
    df_abrigos.columns = df_abrigos.columns.str.upper()
    df_abrigos['LATITUDE'] = pd.to_numeric(df_abrigos['LATITUDE'], errors='coerce')
    df_abrigos['LONGITUDE'] = pd.to_numeric(df_abrigos['LONGITUDE'], errors='coerce')

    if 'PESSOAS ABRIGADAS' in df_abrigos.columns:
        df_abrigos['PESSOAS ABRIGADAS'] = pd.to_numeric(
            df_abrigos['PESSOAS ABRIGADAS'], errors='coerce'
        ).fillna(0).astype(int)
    else:
        df_abrigos['PESSOAS ABRIGADAS'] = 0

    if 'ACEITA PETS' in df_abrigos.columns:
        df_abrigos['ACEITA PETS'] = df_abrigos['ACEITA PETS'].fillna('NÃO').astype(str)
    else:
        df_abrigos['ACEITA PETS'] = 'NÃO'

    df_abrigos.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

    # Separar abrigos ativos
    df_abrigos_ativos = df_abrigos[df_abrigos['PESSOAS ABRIGADAS'] > 0].copy()

    print(f"✓ {len(df_abrigos)} abrigos carregados")
    print(f"✓ {len(df_abrigos_ativos)} abrigos ativos (com pessoas)")

except Exception as e:
    print(f"⚠️ Erro ao carregar abrigos: {e}")
    df_abrigos = pd.DataFrame()
    df_abrigos_ativos = pd.DataFrame()

# ============================================
# 6. ANÁLISE ESPACIAL - MUNICÍPIOS AFETADOS
# ============================================

print("\n📊 Analisando interseção com municípios...")

# Converter para sistema de coordenadas projetado (UTM 22S para RS)
municipios_gdf_proj = municipios_gdf.to_crs("EPSG:31982")
inundacao_completa_proj = inundacao_completa.to_crs("EPSG:31982")

municipios_afetados = []

for idx, municipio in municipios_gdf.iterrows():
    try:
        municipio_proj = municipios_gdf_proj.iloc[idx]

        intersecao = inundacao_completa_proj.geometry.intersects(municipio_proj.geometry)

        if intersecao.any():
            area_muni = municipio_proj.geometry.area
            area_inundada = inundacao_completa_proj[intersecao].geometry.intersection(
                municipio_proj.geometry
            ).area.sum()

            percentual = (area_inundada / area_muni * 100) if area_muni > 0 else 0
            centroid = municipio.geometry.centroid

            municipios_afetados.append({
                'nome': municipio['nm_mun'],
                'cd_mun': municipio['cd_mun'],
                'area_km2': municipio['area_km2'],
                'percentual_afetado': percentual,
                'geometry': municipio.geometry,
                'lat': centroid.y,
                'lon': centroid.x,
                'afetado': True
            })

            if percentual > 10:
                print(f"  🔴 {municipio['nm_mun']}: {percentual:.1f}% afetado")
    except Exception as e:
        pass

print(f"\n✓ Total de municípios afetados: {len(municipios_afetados)}")

# ============================================
# 6.5 IDENTIFICAR TOP 10 MUNICÍPIOS
# ============================================

municipios_ordenados = sorted(municipios_afetados, key=lambda x: x['percentual_afetado'], reverse=True)
top10_municipios = municipios_ordenados[:10]

print("\n🏆 TOP 10 MUNICÍPIOS MAIS AFETADOS:")
for i, muni in enumerate(top10_municipios, 1):
    print(f"  {i:2d}. {muni['nome']:20s} - {muni['percentual_afetado']:6.2f}%")

# ============================================
# 7. CRIAR MAPA
# ============================================

print("\n🗺️  Gerando mapa interativo...")

m = folium.Map(
    location=[-30.0, -51.2],
    zoom_start=8,
    tiles='OpenStreetMap'
)

# Adicionar tile satélite
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satélite',
    overlay=False,
    control=True
).add_to(m)

# ============================================
# 8. ADICIONAR ÁREAS DE INUNDAÇÃO
# ============================================

fg_inundacao = folium.FeatureGroup(name="🌊 Áreas Inundadas", show=True)

for idx, row in inundacao_completa.iterrows():
    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=lambda x: {
            'fillColor': '#2166ac',
            'color': '#08519c',
            'weight': 1,
            'fillOpacity': 0.6
        },
        tooltip="Área inundada - Maio 2024"
    ).add_to(fg_inundacao)

fg_inundacao.add_to(m)

# ============================================
# 9. MUNICÍPIOS - SOMENTE CONTORNOS
# ============================================

fg_municipios_contorno = folium.FeatureGroup(name="🗺️ Contornos dos Municípios", show=False)


def cor_por_percentual(percentual):
    if percentual > 50:
        return '#8b0000'
    elif percentual > 20:
        return '#ff4500'
    elif percentual > 5:
        return '#ffa500'
    else:
        return '#ffd700'


for muni in municipios_afetados:
    folium.GeoJson(
        muni['geometry'].__geo_interface__,
        style_function=lambda x, p=muni['percentual_afetado']: {
            'fillColor': cor_por_percentual(p),
            'color': '#333',
            'weight': 2,
            'fillOpacity': 0.3
        },
        tooltip=f"<b>{muni['nome']}</b><br>{muni['percentual_afetado']:.1f}% afetado"
    ).add_to(fg_municipios_contorno)

fg_municipios_contorno.add_to(m)

# ============================================
# 10. MUNICÍPIOS - MARCADORES COM INFO
# ============================================

fg_municipios_markers = folium.FeatureGroup(name="📍 Info dos Municípios Afetados", show=True)

for muni in municipios_afetados:
    popup_html = f"""
    <div style='width: 220px; font-family: Arial;'>
        <h4 style='margin: 0 0 10px 0; color: #333;'>{muni['nome']}</h4>
        <p style='margin: 5px 0;'><b>Área total:</b> {muni['area_km2']:.1f} km²</p>
        <p style='margin: 5px 0;'><b>Área afetada:</b> {muni['percentual_afetado']:.1f}%</p>
        <p style='margin: 5px 0;'><b>Código IBGE:</b> {muni['cd_mun']}</p>
    </div>
    """

    if muni['percentual_afetado'] > 50:
        cor = 'darkred'
        icon = 'exclamation-triangle'
    elif muni['percentual_afetado'] > 20:
        cor = 'red'
        icon = 'warning'
    elif muni['percentual_afetado'] > 5:
        cor = 'orange'
        icon = 'info-circle'
    else:
        cor = 'beige'
        icon = 'info'

    folium.Marker(
        location=[muni['lat'], muni['lon']],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"<b>{muni['nome']}</b><br>{muni['percentual_afetado']:.1f}% afetado",
        icon=folium.Icon(color=cor, icon=icon, prefix='fa')
    ).add_to(fg_municipios_markers)

fg_municipios_markers.add_to(m)

# ============================================
# 10.5 NOVA CAMADA: TOP 10 MUNICÍPIOS
# ============================================

fg_top10 = folium.FeatureGroup(name="Ranking 10 Municípios Mais Afetados", show=False)

for i, muni in enumerate(top10_municipios, 1):
    popup_html = f"""
    <div style='width: 260px; font-family: Arial;'>
        <h3 style='margin: 0 0 10px 0; color: #8b0000; border-bottom: 2px solid #8b0000; padding-bottom: 5px;'>
             #{i} - {muni['nome']}
        </h3>
        <p style='margin: 8px 0; font-size: 14px;'><b>🎯 Ranking:</b> {i}º lugar</p>
        <p style='margin: 8px 0; font-size: 14px;'><b>📊 Área afetada:</b> {muni['percentual_afetado']:.2f}%</p>
        <p style='margin: 8px 0; font-size: 14px;'><b>📏 Área total:</b> {muni['area_km2']:.1f} km²</p>
        <p style='margin: 8px 0; font-size: 14px;'><b>🔢 Código IBGE:</b> {muni['cd_mun']}</p>
        <hr style="margin: 8px 0;">
        <p style='margin: 5px 0; font-size: 11px; color: #666;'>
            ⚠️ Este município está entre os 10 mais afetados pelas enchentes
        </p>
    </div>
    """

    # Marcador especial para TOP 10 - estrela dourada
    folium.Marker(
        location=[muni['lat'], muni['lon']],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"<b> #{i} - {muni['nome']}</b><br>{muni['percentual_afetado']:.2f}% afetado",
        icon=folium.Icon(
            color='red',
            icon='star',
            prefix='fa',
            icon_color='gold'
        )
    ).add_to(fg_top10)

    # Adicionar também um círculo destacado
    folium.CircleMarker(
        location=[muni['lat'], muni['lon']],
        radius=15,
        color='#8b0000',
        fillColor='#ff0000',
        fillOpacity=0.3,
        weight=3,
        popup=f"Ranking {i}: {muni['nome']}"
    ).add_to(fg_top10)

fg_top10.add_to(m)

# ============================================
# 11. ABRIGOS ATIVOS COM PESSOAS
# ============================================

if len(df_abrigos_ativos) > 0:
    print(f"\n🏠 Adicionando {len(df_abrigos_ativos)} abrigos ativos ao mapa...")

    fg_abrigos_ativos = folium.FeatureGroup(name="🏠 Abrigos Ativos (com pessoas)", show=True)
    marker_cluster_ativos = MarkerCluster(name="Abrigos Ativos").add_to(fg_abrigos_ativos)

    for idx, row in df_abrigos_ativos.iterrows():
        nome_local = row.get('NAME', 'Abrigo Não Nomeado')
        aceita_pets = row['ACEITA PETS']
        pessoas = row['PESSOAS ABRIGADAS']

        html_popup = f"""
        <div style='width: 280px; font-family: Arial;'>
            <h4 style='margin: 0 0 10px 0; color: #2c5f2d;'>🏠 {nome_local}</h4>
            <p style='margin: 5px 0;'><b>📍 Cidade:</b> {row.get('CIDADE', 'Não Informada')}</p>
            <p style='margin: 5px 0;'><b>🏠 Endereço:</b> {row.get('ENDEREÇO', 'Não Informado')}</p>
            <p style='margin: 5px 0;'><b>👥 Pessoas:</b> {pessoas:,}</p>
            <p style='margin: 5px 0;'><b>🐕 Pets:</b> {'✅ SIM' if aceita_pets.upper().startswith('S') else '❌ NÃO'}</p>
            <hr style="margin: 8px 0;">
            <p style="font-size: 10px; color: #666;">🕒 {row.get('ÚLTIMA ATUALIZAÇÃO', 'Não Informada')}</p>
        </div>
        """

        if aceita_pets.upper().startswith('S'):
            color = "green"
            icon = "paw"
        else:
            color = "purple"
            icon = "home"

        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=f"<b>{nome_local}</b><br>👥 {pessoas} pessoas",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(marker_cluster_ativos)

    fg_abrigos_ativos.add_to(m)

# ============================================
# 12. ABRIGOS VAZIOS - REMOVIDO
# ============================================

if len(df_abrigos) > 0:
    df_abrigos_vazios = df_abrigos[df_abrigos['PESSOAS ABRIGADAS'] == 0].copy()
    print(f"\n⚪ {len(df_abrigos_vazios)} abrigos vazios identificados (não mostrados no mapa)")

# ============================================
# 13. RECURSOS EXTRAS
# ============================================

folium.LayerControl(position='topright', collapsed=False).add_to(m)

minimap = plugins.MiniMap(toggle_display=True)
m.add_child(minimap)

plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)
plugins.Fullscreen(position='topleft').add_to(m)

# ============================================
# 14. LEGENDA ATUALIZADA
# ============================================

total_pessoas_abrigadas = df_abrigos_ativos['PESSOAS ABRIGADAS'].sum() if len(df_abrigos_ativos) > 0 else 0
abrigos_vazios = len(df_abrigos) - len(df_abrigos_ativos) if len(df_abrigos) > 0 else 0

legend_html = f'''
<div style="position: fixed;
            top: 10px; left: 60px; width: 320px; height: auto;
            background-color: white; border:2px solid #333; z-index:1000;
            font-size:12px; padding: 12px; border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
            max-height: 90vh; overflow-y: auto;">

    <p style="margin:0 0 8px 0; font-weight:bold; font-size:15px; border-bottom: 2px solid #333; padding-bottom: 5px;">
        📊 Enchentes RS - Maio 2024
    </p>

    <p style="margin:6px 0 3px 0; font-weight:bold; font-size: 11px;">Municípios Afetados:</p>
    <p style="margin:2px 0; font-size: 10px;"><span style="background:#8b0000; padding:1px 6px; color:white; border-radius:2px;">■</span> Crítico (&gt;50%)</p>
    <p style="margin:2px 0; font-size: 10px;"><span style="background:#ff4500; padding:1px 6px; color:white; border-radius:2px;">■</span> Alto (20-50%)</p>
    <p style="margin:2px 0; font-size: 10px;"><span style="background:#ffa500; padding:1px 6px; color:white; border-radius:2px;">■</span> Médio (5-20%)</p>
    <p style="margin:2px 0; font-size: 10px;"><span style="background:#ffd700; padding:1px 6px; color:black; border-radius:2px;">■</span> Baixo (&lt;5%)</p>

    <hr style="margin: 8px 0; border: 1px solid #ccc;">

    <p style="margin:6px 0 3px 0; font-weight:bold; font-size: 11px;">Ranking:</p>
    <p style="margin:2px 0; font-size: 10px;"><i class="fa fa-star" style="color:gold;"></i> Ranking 10 Mais Afetados</p>

    <hr style="margin: 8px 0; border: 1px solid #ccc;">

    <p style="margin:6px 0 3px 0; font-weight:bold; font-size: 11px;">Abrigos:</p>
    <p style="margin:2px 0; font-size: 10px;"><i class="fa fa-home" style="color:purple;"></i> Abrigo Ativo (sem pets)</p>
    <p style="margin:2px 0; font-size: 10px;"><i class="fa fa-paw" style="color:green;"></i> Abrigo Ativo (aceita pets)</p>

    <hr style="margin: 8px 0; border: 1px solid #ccc;">

    <p style="margin:6px 0 3px 0; font-weight:bold; font-size: 11px;">Estatísticas:</p>
    <p style="margin:2px 0; font-size: 10px;">🏛️ Municípios: <b>{len(municipios_afetados)}</b></p>
    <p style="margin:2px 0; font-size: 10px;">🏠 Abrigos ativos: <b>{len(df_abrigos_ativos)}</b></p>
    <p style="margin:2px 0; font-size: 10px;">👥 Pessoas: <b>{total_pessoas_abrigadas:,}</b></p>
    <p style="margin:2px 0; font-size: 10px; color:#666;">⚪ Abrigos vazios: {abrigos_vazios}</p>

    <hr style="margin: 8px 0; border: 1px solid #ccc;">

    <p style="margin:6px 0 3px 0; font-weight:bold; font-size: 10px;">📚 Referências: </p>

    <p style="margin:4px 0; font-size: 9px; line-height: 1.3; color:#444;">
        <b>Região Guaíba:</b><br>
        Possantti et al. (2024). Banco de dados das cheias na Região Hidrográfica do Lago Guaíba em Maio de 2024 [Data set]. Zenodo.
    </p>

    <p style="margin:4px 0; font-size: 9px; line-height: 1.3; color:#444;">
        <b>Lagoa dos Patos:</b><br>
        da Silva et al. (2024). Base de dados da inundação na Região da Lagoa dos Patos em maio de 2024 [Dataset] OSF.
    </p>

    <p style="margin:6px 0 0 0; font-size:8px; color:#999; border-top: 1px solid #ddd; padding-top: 5px;">
        💡 Use o controle de camadas para ativar/desativar visualizações
    </p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# ============================================
# 15. SALVAR MAPA
# ============================================

arquivo_saida = DIRETORIO_BASE + "mapa_enchentes_rs_2024_final.html"

print("\n" + "=" * 80)
print("💾 SALVANDO MAPA...")
print("=" * 80)

m.save(arquivo_saida)

print(f"✅ Mapa salvo com sucesso!")
print(f"📁 Arquivo: {arquivo_saida}")
print("\n" + "=" * 80)
print("✅ ANÁLISE CONCLUÍDA!")
print("=" * 80)
print(f"🏛️ Municípios afetados: {len(municipios_afetados)}")
print(f"🏠 Total de abrigos: {len(df_abrigos)}")
print(f"🏠 Abrigos ativos: {len(df_abrigos_ativos)}")
print(f"⚪ Abrigos vazios: {abrigos_vazios}")
print(f"👥 Total pessoas abrigadas: {total_pessoas_abrigadas:,}")
print(f"🌊 Polígonos de inundação: {len(inundacao_completa)}")
print("=" * 80)

# Mostrar ranking
if len(municipios_afetados) > 0:
    print("\n🔝 TOP 10 MUNICÍPIOS MAIS AFETADOS:")
    print("-" * 80)
    for i, muni in enumerate(top10_municipios, 1):
        print(f"{i:2d}. {muni['nome']:20s} - {muni['percentual_afetado']:6.2f}% afetado")

if len(df_abrigos_ativos) > 0:
    print("\n🏠 TOP 10 ABRIGOS COM MAIS PESSOAS:")
    print("-" * 80)
    top_abrigos = df_abrigos_ativos.nlargest(10, 'PESSOAS ABRIGADAS')
    for i, (idx, abrigo) in enumerate(top_abrigos.iterrows(), 1):
        nome = abrigo.get('NAME', 'Sem nome')[:30]
        cidade = abrigo.get('CIDADE', 'N/A')
        pessoas = abrigo['PESSOAS ABRIGADAS']
        print(f"{i:2d}. {nome:30s} ({cidade}) - {pessoas:,} pessoas")

print("\n" + "=" * 80)
print("🎉 Processo finalizado! Abra o arquivo HTML para visualizar o mapa.")
print("=" * 80)