import pandas as pd

# =========================================================
# 1. CARREGAR DADOS ORIGINAIS (mesma fonte usada na carga inicial)
# =========================================================
comp = pd.read_excel('/mnt/user-data/uploads/inventario_2025_Prisional_GERAL_-_SEAP_e_HM1.xlsx', sheet_name='INVENTÁRIO COMPUTADORES ')
imp = pd.read_excel('/mnt/user-data/uploads/inventario_2025_Prisional_GERAL_-_SEAP_e_HM1.xlsx', sheet_name='INVENTÁRIO IMPRESSORAS')
locados = pd.read_excel('/mnt/user-data/uploads/inventario_2025_Prisional_LOCADOS_HM1_-_qtd_e_local_PC_e_Monitores.xlsx', sheet_name='INVENTÁRIO COMPUTADORES ')

def limpar_patrimonio(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    texto = str(v).strip()
    if texto.endswith('.0'):
        texto = texto[:-2]
    return texto

def esc(v):
    if v is None:
        return 'NULL'
    return "'" + str(v).replace("'", "''") + "'"

# =========================================================
# 2. MAPA patrimonio -> categoria ('alugado' / 'proprio') p/ COMPUTADORES
# =========================================================
MAPA_CATEGORIA = {'HM1': 'alugado', 'SEAP': 'proprio'}

comp['patrimonio_limpo'] = comp['PATRIMÔNIO'].apply(limpar_patrimonio)
comp_categoria = {}
for _, row in comp.iterrows():
    pat = row['patrimonio_limpo']
    obs = row.get('OBSERVAÇÕES')
    if pat and pd.notna(obs) and obs in MAPA_CATEGORIA:
        comp_categoria[pat] = MAPA_CATEGORIA[obs]

# patrimônio dos monitores (coluna MONITOR na planilha LOCADOS) -> sempre 'alugado'
locados['monitor_limpo'] = locados['MONITOR'].apply(limpar_patrimonio)
monitores_patrimonios = set(locados['monitor_limpo'].dropna())

sql = []
sql.append("-- Migração: adiciona coluna categoria (alugado/proprio) na tabela inventario")
sql.append("alter table inventario add column if not exists categoria text;")
sql.append("")
sql.append(f"-- ===== Computadores: {len(comp_categoria)} com categoria conhecida =====")
for pat, cat in comp_categoria.items():
    sql.append(
        f"UPDATE inventario SET categoria = {esc(cat)} WHERE patrimonio = {esc(pat)} AND tipo = 'computador';"
    )

sql.append("")
sql.append(f"-- ===== Monitores: todos marcados como alugado ({len(monitores_patrimonios)} itens) =====")
sql.append("UPDATE inventario SET categoria = 'alugado' WHERE tipo = 'monitor';")

sql.append("")
sql.append("-- ===== Impressoras: todas alugadas (100% LOCADO na planilha) =====")
sql.append("UPDATE inventario SET categoria = 'alugado' WHERE tipo = 'impressora';")

with open('/home/claude/migracao_categoria.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql) + '\n')

print(f"Computadores com categoria conhecida: {len(comp_categoria)}")
print(f"  - alugado (HM1): {sum(1 for c in comp_categoria.values() if c == 'alugado')}")
print(f"  - proprio (SEAP): {sum(1 for c in comp_categoria.values() if c == 'proprio')}")
print(f"Computadores sem categoria na planilha original: {len(comp) - len(comp_categoria)}")
print(f"Monitores marcados como alugado: {len(monitores_patrimonios)}")
print("Arquivo gerado: migracao_categoria.sql")
