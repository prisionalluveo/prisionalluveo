// supabaseClient.js
// Preencher com os dados do SEU projeto Supabase (Settings > API):
const SUPABASE_URL = 'https://ppvfemzrrkvaijcoeufs.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_WJkb0gtUoj_Uy_e4-TGBmQ_mcNc1E-W'

const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Unidades usadas em todo o sistema (Inventário, Plantão, Escala, Ordens, Projetos)
const UNIDADES = [
  'Instituto Penal Santo Expedito',
  'Penitenciária Talavera Bruce',
  'Instituto Penal Vicente Piragibe',
  'Presidio elizabeth de sa rego',
  'Cadeia Pública Pedro Melo da Silva',
  'Cadeia Pública Joaquim Ferreira de Souza',
  'Instituto Penal Benjamin de Moraes Filho',
  'Cadeia Pública Jorge Santana',
  'Instituto Penal Placido Sá Carvalho',
  'Presídio Alfredo Tranjan',
  'Penitenciária Bandeira Stampa',
  'Penitenciária Industrial Esmeraldino Bandeira',
  'Presídio Gabriel Ferreira Castilho',
  'Presídio Jonas Lopes de Carvalho',
  'Cadeia Pública Inspetor José Antônio da Costa Barros',
  'Penitenciária Laércio da Costa Pelegrino',
  'Presídio Lemos de Brito',
  'Presídio Pedrolino Werling de Oliveira',
  'Penitenciária Muniz Sodré',
  'Presídio Nelson Hungria',
  'Cadeia Pública Paulo Roberto Rocha (Regime Fechado)',
  'Penitenciária Dr. Serrano Neves',
  'Presídio Evaristo de Moraes',
  'Instituto Penal Candido Mendes',
  'Casa do Albergado Crispim Ventino',
  'Presídio José Frederico Marques',
  'Instituto Penal Oscar Stevenson - feminina',
  'Presídio Ary Franco',
]

// Protege uma página: se não estiver logado, manda pro login.
// Chamar no topo de toda página que não seja login.html
async function exigirLogin() {
  const { data: { session } } = await supabaseClient.auth.getSession()
  if (!session) {
    window.location.href = 'login.html'
    return null
  }
  return session
}

// Busca o perfil (nome + papel) do usuário logado
async function obterPerfil(sessao) {
  const { data } = await supabaseClient
    .from('perfis')
    .select('nome, papel')
    .eq('id', sessao.user.id)
    .maybeSingle()
  return data || { nome: sessao.user.email, papel: 'tecnico' }
}

// Esconde da navegação os itens marcados com class="somente-admin"
// quando o usuário logado não for admin
async function aplicarPermissoesNav(sessao) {
  const perfil = await obterPerfil(sessao)
  if (perfil.papel !== 'admin') {
    document.querySelectorAll('.somente-admin').forEach(el => el.remove())
  }
  return perfil
}

// Protege uma página inteira pra só admin acessar (redireciona quem não é)
async function exigirAdmin(sessao) {
  const perfil = await obterPerfil(sessao)
  if (perfil.papel !== 'admin') {
    alert('Só administradores podem acessar essa página.')
    window.location.href = 'index.html'
    return null
  }
  return perfil
}

async function sair() {
  await supabaseClient.auth.signOut()
  window.location.href = 'login.html'
}
