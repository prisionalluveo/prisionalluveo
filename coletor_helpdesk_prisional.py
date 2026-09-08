#!/usr/bin/env python3
"""
coletor_helpdesk_prisional.py

Loga no HelpDesk (Tera) com o usuário do prisional (tecnico.prisional) e
envia os totais de chamados (aguardando, em atendimento, concluído
tecnicamente, concluído/avaliado) pra tabela chamados_resumo do Supabase.

Roda via GitHub Actions (agendado) — ver .github/workflows/coletor-chamados.yml
Não precisa de servidor nenhum.

Credenciais vêm de variáveis de ambiente (GitHub Secrets), nunca do código:
  TERA_USER, TERA_PASS, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""
import os
import sys
import requests
from datetime import datetime

BASE = 'https://sistemas.vivario.org.br/helpdesk'

TERA_USER = os.environ['TERA_USER']
TERA_PASS = os.environ['TERA_PASS']
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_ROLE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

# As mesmas 4 filas usadas no Andaraí. Se o login do prisional usar outra
# pasta (sys_ti em vez de sys_adm, por exemplo), o script tenta as duas
# automaticamente — ver tentar_pastas() abaixo.
FILAS = {
    'aguardando': 'back_chamados_pausado_mod_serverside.php',
    'atendimento': 'back_chamados_atendimento_mod_serverside.php',
    'concluido_tec': 'back_chamados_concluido_tec_mod_serverside.php',
    'concluido_fim': 'back_chamados_concluido_fim_mod_serverside.php',
}
PASTAS_CANDIDATAS = ['ti/sys_adm', 'ti/sys_ti']

CAMPOS = ['area', 'id', 'unidade', 'data_abertura', 'datahora', 'problema',
          'descricao', 'contato', 'sla', 'responsavel', 'acoes']


def montar_params():
    params = {
        'draw': 1, 'start': 0, 'length': 1,
        'search[value]': '', 'search[regex]': 'false',
        'order[0][column]': 0, 'order[0][dir]': 'asc',
    }
    for i, campo in enumerate(CAMPOS):
        params[f'columns[{i}][data]'] = campo
        params[f'columns[{i}][name]'] = ''
        params[f'columns[{i}][searchable]'] = 'true'
        params[f'columns[{i}][orderable]'] = 'true'
        params[f'columns[{i}][search][value]'] = ''
        params[f'columns[{i}][search][regex]'] = 'false'
    return params


def tentar_pastas(sessao, nome_arquivo):
    """Tenta sys_adm primeiro, cai pra sys_ti se não achar dado nenhum."""
    for pasta in PASTAS_CANDIDATAS:
        url = f'{BASE}/{pasta}/{nome_arquivo}'
        try:
            resp = sessao.get(
                url, params=montar_params(), timeout=30,
                headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': f'{BASE}/ti/home.php'},
            )
            corpo = resp.json()
            if 'recordsTotal' in corpo:
                return corpo['recordsTotal'], pasta
        except Exception:
            continue
    return None, None


def enviar_para_supabase(totais):
    resp = requests.post(
        f'{SUPABASE_URL}/rest/v1/chamados_resumo',
        headers={
            'apikey': SUPABASE_SERVICE_ROLE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        },
        json=totais,
        timeout=15,
    )
    if resp.status_code >= 300:
        print(f'ERRO Supabase: {resp.status_code} {resp.text}')
        sys.exit(1)


def main():
    s = requests.Session()
    r = s.post(f'{BASE}/valida.php', data={'login': TERA_USER, 'pword': TERA_PASS},
               timeout=30, allow_redirects=True)
    if 'sign-in' in r.url:
        print(f'[{datetime.now():%d/%m/%Y %H:%M}] ERRO: login falhou (usuário/senha do tecnico.prisional)')
        sys.exit(1)
    s.get(f'{BASE}/ti/home.php', timeout=30)

    totais = {}
    pasta_usada = None
    for nome, arquivo in FILAS.items():
        total, pasta = tentar_pastas(s, arquivo)
        totais[nome] = total
        if pasta:
            pasta_usada = pasta
        if total is None:
            print(f'[{datetime.now():%d/%m/%Y %H:%M}] AVISO: não consegui ler a fila "{nome}"')

    if all(v is None for v in totais.values()):
        print(f'[{datetime.now():%d/%m/%Y %H:%M}] ERRO: nenhuma fila retornou dado — revisar login/pastas')
        sys.exit(1)

    enviar_para_supabase(totais)
    print(f'[{datetime.now():%d/%m/%Y %H:%M}] OK (pasta: {pasta_usada}) - {totais}')


if __name__ == '__main__':
    main()
