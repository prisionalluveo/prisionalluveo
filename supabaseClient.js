// supabaseClient.js
// Preencher com os dados do SEU projeto Supabase (Settings > API):
const SUPABASE_URL = 'https://ppvfemzrrkvaijcoeufs.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_WJkb0gtUoj_Uy_e4-TGBmQ_mcNc1E-W'

const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Unidades usadas em todo o sistema (Inventário, Plantão, Escala, Ordens, Projetos)
const UNIDADES = ['Grande Rio', 'ADM 1', 'ADM 2', 'ADM 3 Gericinó']

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

async function sair() {
  await supabaseClient.auth.signOut()
  window.location.href = 'login.html'
}
