# app.py
import streamlit as st
import re

# ==============================================================================
# 1. LÓGICA CENTRAL DO SEU SCRIPT ORIGINAL
# (Copiei os dicionários e a lógica de transposição para cá)
# ==============================================================================

# Mapeamento das notas com seus valores em semitons
MAPA_NOTAS = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    "E#": 5, "B#": 0, "Fb": 4, "Cb": 11
}

# Mapeamento inverso para converter de volta para notas (preferindo sustenidos)
MAPA_VALORES_NOTAS = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
]

# Mapas para explicações de enarmonia
EXPLICACAO_ENARMONICA_SAIDA = {
    "C##": {"soacomo": "D", "detalhe": "Dó dobrado sustenido soa como Ré"},
    "D##": {"soacomo": "E", "detalhe": "Ré dobrado sustenido soa como Mi"},
    "E##": {"soacomo": "F#", "detalhe": "Mi dobrado sustenido soa como Fá sustenido"},
    "F##": {"soacomo": "G", "detalhe": "Fá dobrado sustenido soa como Sol"},
    "G##": {"soacomo": "A", "detalhe": "Sol dobrado sustenido soa como Lá"},
    "A##": {"soacomo": "B", "detalhe": "Lá dobrado sustenido soa como Si"},
    "B##": {"soacomo": "C#", "detalhe": "Si dobrado sustenido soa como Dó sustenido"},
    "Cbb": {"soacomo": "Bb", "detalhe": "Dó dobrado bemol soa como Si bemol"},
    "Dbb": {"soacomo": "C", "detalhe": "Ré dobrado bemol soa como Dó"},
    "Ebb": {"soacomo": "D", "detalhe": "Mi dobrado bemol soa como Ré"},
    "Fbb": {"soacomo": "Eb", "detalhe": "Fá dobrado bemol soa como Mi bemol"},
    "Gbb": {"soacomo": "F", "detalhe": "Sol dobrado bemol soa como Fá"},
    "Abb": {"soacomo": "G", "detalhe": "Lá dobrado bemol soa como Sol"},
    "Bbb": {"soacomo": "A", "detalhe": "Si dobrado bemol soa como Lá"}
}

EXPLICACAO_NOTAS_TEORICAS_ENTRADA = {
    "E#": "Mi sustenido (E#) é enarmônico a Fá (F).",
    "B#": "Si sustenido (B#) é enarmônico a Dó (C).",
    "Fb": "Fá bemol (Fb) é enarmônico a Mi (E).",
    "Cb": "Dó bemol (Cb) é enarmônico a Si (B)."
}

def transpor_acordes(acordes_originais, acao, intervalo):
    """
    Função principal que recebe uma lista de acordes e os parâmetros de transposição,
    retornando os acordes transpostos e informações adicionais.
    """
    intervalo_semitons = int(intervalo * 2)
    acordes_transpostos = []
    explicacoes_entrada = set()
    explicacoes_saida = set()

    for acorde_original in acordes_originais:
        # Regex para separar a nota fundamental (ex: C#, Gb, F) do resto do acorde (ex: m7, dim, /G)
        match = re.match(r"([A-G][b#]?[b#]?)(.*)", acorde_original, re.IGNORECASE)

        if not match:
            acordes_transpostos.append(f"{acorde_original}?") # Marca acordes não reconhecidos
            continue

        nota_fundamental_str, qualidade_acorde = match.groups()
        
        # Encontra a capitalização correta da nota no mapa
        nota_fundamental_key = ""
        for key in MAPA_NOTAS:
            if key.lower() == nota_fundamental_str.lower():
                nota_fundamental_key = key
                break
        
        if not nota_fundamental_key:
            acordes_transpostos.append(f"{acorde_original}?")
            continue
            
        # Adiciona explicação de notas teóricas na entrada, se houver
        if nota_fundamental_key in EXPLICACAO_NOTAS_TEORICAS_ENTRADA:
            explicacoes_entrada.add(f"Nota original '{nota_fundamental_key}': {EXPLICACAO_NOTAS_TEORICAS_ENTRADA[nota_fundamental_key]}")

        # O cálculo da transposição
        valor_nota_original = MAPA_NOTAS[nota_fundamental_key]

        if acao == 'Aumentar':
            novo_valor_nota = (valor_nota_original + intervalo_semitons) % 12
        else: # Diminuir
            novo_valor_nota = (valor_nota_original - intervalo_semitons + 12) % 12
        
        nova_nota_fundamental = MAPA_VALORES_NOTAS[novo_valor_nota]
        
        # Lógica para casos especiais de enarmonia na saída
        # (Seu código original tinha algumas dessas, aqui está uma forma mais genérica)
        # Esta parte pode ser expandida se necessário.
        
        acorde_transposto_final = f"{nova_nota_fundamental}{qualidade_acorde}"
        acordes_transpostos.append(acorde_transposto_final)

        # Adiciona explicação de notas teóricas na saída, se houver
        if nova_nota_fundamental in EXPLICACAO_ENARMONICA_SAIDA:
             info = EXPLICACAO_ENARMONICA_SAIDA[nova_nota_fundamental]
             explicacoes_saida.add(f"Nota transposta '{nova_nota_fundamental}': {info['detalhe']}. Ela soa como {info['soacomo']}.")

    return acordes_transpostos, list(explicacoes_entrada), list(explicacoes_saida)


# ==============================================================================
# 2. INTERFACE GRÁFICA COM STREAMLIT
# ==============================================================================

# Configuração da página
st.set_page_config(page_title="Transpositor de Acordes", page_icon="🎵", layout="centered")

# Título e descrição
st.title("🎵 Transpositor de Acordes")
st.markdown("Uma ferramenta simples para transpor tonalidades de acordes. Insira os acordes, escolha se quer aumentar ou diminuir o tom e em quantos tons será essa alteração.")

# --- Inputs do Usuário ---
st.header("1. Insira os acordes")
sequencia_input = st.text_input(
    "Separe os acordes por espaço:",
    placeholder="Ex: G D Em C"
)

st.header("2. Escolha a transposição")
col1, col2 = st.columns(2)

with col1:
    acao = st.radio(
        "Ação:",
        ('Aumentar', 'Diminuir'),
        horizontal=True,
    )

with col2:
    intervalo = st.number_input(
        "Intervalo (em tons):",
        min_value=0.5,
        max_value=12.0,
        value=1.0, # Valor padrão de 1 tom
        step=0.5,
        help="0.5 = meio tom, 1 = um tom, 1.5 = um tom e meio, etc."
    )

# --- Botão de Ação ---
if st.button("Transpor Acordes!", type="primary", use_container_width=True):
    if not sequencia_input:
        st.warning("Por favor, insira uma sequência de acordes para transpor.")
    else:
        acordes_originais = sequencia_input.strip().split()
        
        # Chama a função de lógica
        acordes_transpostos, expl_in, expl_out = transpor_acordes(acordes_originais, acao, intervalo)

        # --- Exibição dos Resultados ---
        st.header("🎸 Resultado")
        
        # Cria colunas para um visual lado a lado
        num_acordes = len(acordes_originais)
        # O parâmetro 'gap' ajuda a dar um pouco mais de espaço
        cols = st.columns(num_acordes, gap="small") 

        for i in range(num_acordes):
            with cols[i]:
                # Usando st.markdown com HTML para um layout customizado, compacto e centralizado.
        # Isso evita o problema de corte de texto do st.metric.
                st.markdown(f"""
                <div style="text-align: center; border: 1px solid #333; border-radius: 5px; padding: 5px;">
                    <span style="font-size: 0.9em; opacity: 0.7;">{acordes_originais[i]}</span>
                    <br>
                    <strong style="font-size: 1.5em; color: #FF4B4B;">{acordes_transpostos[i]}</strong>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---") # Esta é a linha divisória após os resultados visuais
        
        # --- NOVO BLOCO PARA COPIAR E COLAR ---
        st.subheader("📝 Copie os acordes aqui")

        # Junta as listas de acordes em strings separadas por espaço
        originais_str = ' '.join(acordes_originais)
        transpostos_str = ' '.join(acordes_transpostos)

        # Formata o texto final com as duas linhas
        texto_para_copiar = f"Originais:   {originais_str}\nTranspostos: {transpostos_str}"

        # Exibe o texto em um bloco de código com botão de cópia
        st.code(texto_para_copiar, language="text")

        # --- Exibição das Informações Adicionais ---
        if expl_in or expl_out:
            with st.expander("ℹ️ Informações Adicionais (Notas Enarmônicas)"):
                if expl_in:
                    st.markdown("**Notas na sua sequência original:**")
                    for e in expl_in:
                        st.info(e)
                if expl_out:
                    st.markdown("**Notas no resultado da transposição:**")
                    for e in expl_out:
                        st.success(e)

# --- Rodapé ---
st.markdown("---")

st.markdown("Desenvolvido para a Glória de Deus.\n\nCopyright © Rafael Panfil")
