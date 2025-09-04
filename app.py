# app_final.py
import streamlit as st
import re
import docx
import io

# ==============================================================================
# 1. LÓGICA E FUNÇÕES (sem alterações nesta seção)
# ==============================================================================

# --- Dicionários e Mapas ---
MAPA_NOTAS = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    "E#": 5, "B#": 0, "Fb": 4, "Cb": 11
}
MAPA_VALORES_NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
EXPLICACAO_NOTAS_TEORICAS_ENTRADA = {
    "E#": "Mi sustenido (E#) é enarmônico a Fá (F).",
    "B#": "Si sustenido (B#) é enarmônico a Dó (C).",
    "Fb": "Fá bemol (Fb) é enarmônico a Mi (E).",
    "Cb": "Dó bemol (Cb) é enarmônico a Si (B)."
}

# --- Funções para a "Transposição de Sequência" ---
def transpor_acordes_sequencia(acordes_originais, acao, intervalo):
    intervalo_semitons = int(intervalo * 2)
    acordes_transpostos = []
    explicacoes_entrada = set()
    
    for acorde_original in acordes_originais:
        match = re.match(r"([A-G][b#]?[b#]?)(.*)", acorde_original, re.IGNORECASE)
        if not match:
            acordes_transpostos.append(f"{acorde_original}?")
            continue
        
        nota_fundamental_str, qualidade_acorde = match.groups()
        nota_fundamental_key = ""
        for key in MAPA_NOTAS:
            if key.lower() == nota_fundamental_str.lower():
                nota_fundamental_key = key
                break
        if not nota_fundamental_key:
            acordes_transpostos.append(f"{acorde_original}?")
            continue
        
        if nota_fundamental_key in EXPLICACAO_NOTAS_TEORICAS_ENTRADA:
            explicacoes_entrada.add(f"Nota original '{nota_fundamental_key}': {EXPLICACAO_NOTAS_TEORICAS_ENTRADA[nota_fundamental_key]}")

        valor_nota_original = MAPA_NOTAS[nota_fundamental_key]
        semitons_ajuste = intervalo_semitons if acao == 'Aumentar' else -intervalo_semitons
        
        novo_valor_nota = (valor_nota_original + semitons_ajuste + 12) % 12
        nova_nota_fundamental = MAPA_VALORES_NOTAS[novo_valor_nota]
        
        if '/' in qualidade_acorde:
            partes = qualidade_acorde.split('/')
            qualidade = partes[0]
            baixo_str = partes[1]
            
            baixo_key = ""
            for key in MAPA_NOTAS:
                if key.lower() == baixo_str.lower():
                    baixo_key = key
                    break
            
            if baixo_key:
                valor_baixo_original = MAPA_NOTAS[baixo_key]
                novo_valor_baixo = (valor_baixo_original + semitons_ajuste + 12) % 12
                novo_baixo = MAPA_VALORES_NOTAS[novo_valor_baixo]
                acorde_transposto_final = f"{nova_nota_fundamental}{qualidade}/{novo_baixo}"
            else:
                acorde_transposto_final = f"{nova_nota_fundamental}{qualidade_acorde}"
        else:
            acorde_transposto_final = f"{nova_nota_fundamental}{qualidade_acorde}"
            
        acordes_transpostos.append(acorde_transposto_final)

    return acordes_transpostos, list(explicacoes_entrada)

# --- Funções para a "Transposição de Cifra Completa" ---
def ler_arquivo(arquivo):
    if arquivo.name.endswith('.docx'):
        try:
            doc = docx.Document(io.BytesIO(arquivo.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Erro ao ler o arquivo .docx: {e}")
            return None
    else:
        try:
            return arquivo.read().decode("utf-8")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo de texto: {e}")
            return None

def is_chord_line(line):
    line = line.strip()
    if not line:
        return False
    chord_pattern = re.compile(r'^[A-G][b#]?(m|M|dim|aug|sus|add|maj|º|°|/|[-+])?(\d+)?(\(?[^)\s]*\)?)?(/[A-G][b#]?)?$')
    line_for_analysis = line.replace('/:', '').replace('|', '').strip()
    words = line_for_analysis.split()
    if not words:
        return False
    chord_count = 0
    for word in words:
        if chord_pattern.match(word):
            chord_count += 1
    return (chord_count / len(words)) >= 0.75

def processar_cifra(texto_cifra, acao, intervalo):
    semitons = int(intervalo * 2)
    if acao == 'Diminuir':
        semitons = -semitons

    padrao_acorde_busca = r'\b([A-G][b#]?)([^A-G\s,.\n]*)?(/[A-G][b#]?)?\b'
    def replacer(match):
        acorde_completo = match.group(0)
        nota_fundamental_str = match.group(1)
        qualidade = match.group(2) or ""
        baixo = match.group(3) or ""
        nova_nota_fundamental = transpor_nota_individual(nota_fundamental_str, semitons)
        novo_baixo = ""
        if baixo:
            nota_baixo_str = baixo.replace('/', '')
            novo_baixo = "/" + transpor_nota_individual(nota_baixo_str, semitons)
        return f"{nova_nota_fundamental}{qualidade}{novo_baixo}"

    linhas_finais = []
    for linha in texto_cifra.split('\n'):
        if is_chord_line(linha):
            linha_transposta = re.sub(padrao_acorde_busca, replacer, linha)
            linhas_finais.append(linha_transposta)
        else:
            linhas_finais.append(linha)
    return "\n".join(linhas_finais)

def transpor_nota_individual(nota_str, semitons):
    nota_key = ""
    for key in MAPA_NOTAS:
        if key.lower() == nota_str.lower():
            nota_key = key
            break
    if not nota_key:
        return nota_str
    valor_original = MAPA_NOTAS[nota_key]
    novo_valor = (valor_original + semitons + 12) % 12
    return MAPA_VALORES_NOTAS[novo_valor]

# ==============================================================================
# 2. INTERFACE GRÁFICA COM STREAMLIT (COM BOTÃO DE DOWNLOAD)
# ==============================================================================

st.set_page_config(page_title="Transpositor de Acordes", page_icon="🎵", layout="centered")
st.title("🎵 Transpositor Universal de Acordes")
st.markdown("Uma ferramenta completa para transpor tanto sequências simples de acordes quanto cifras de músicas inteiras.")

# --- Inicializa o session_state para guardar o resultado da cifra ---
if 'cifra_transposta' not in st.session_state:
    st.session_state.cifra_transposta = ""
if 'nome_arquivo' not in st.session_state:
    st.session_state.nome_arquivo = "cifra_transposta.txt"

# --- CONTROLES DE TRANSPOSIÇÃO ---
st.header("1. Escolha a transposição")
col1, col2 = st.columns(2)
with col1:
    acao = st.radio("Ação:", ('Aumentar', 'Diminuir'), horizontal=True)
with col2:
    intervalo = st.number_input("Intervalo (em tons):", 0.5, 12.0, 1.0, 0.5, help="0.5 = meio tom, 1 = um tom...")

st.header("2. Insira os acordes ou a cifra")
tab_sequencia, tab_cifra = st.tabs(["Transpor Sequência", "Transpor Cifra Completa"])

# --- ABA 1: TRANSPOR SEQUÊNCIA DE ACORDES ---
with tab_sequencia:
    # (Esta aba permanece sem alterações)
    st.markdown("Use esta aba para transpor uma lista simples de acordes separados por espaço.")
    sequencia_input = st.text_input("Sequência de acordes:", placeholder="Ex: G D/F# Em C")

    if st.button("Transpor Sequência!", type="primary", use_container_width=True):
        if not sequencia_input:
            st.warning("Por favor, insira uma sequência de acordes.")
        else:
            acordes_originais = sequencia_input.strip().split()
            acordes_transpostos, expl_in = transpor_acordes_sequencia(acordes_originais, acao, intervalo)
            st.subheader("🎸 Resultado da Sequência")
            cols = st.columns(len(acordes_originais), gap="small")
            for i, col in enumerate(cols):
                with col:
                    st.markdown(f"""
                    <div style="text-align: center; border: 1px solid #333; border-radius: 5px; padding: 5px;">
                        <span style="font-size: 0.9em; opacity: 0.7;">{acordes_originais[i]}</span><br>
                        <strong style="font-size: 1.5em; color: #FF4B4B;">{acordes_transpostos[i]}</strong>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("📝 Copie os acordes aqui")
            originais_str = ' '.join(acordes_originais)
            transpostos_str = ' '.join(acordes_transpostos)
            texto_para_copiar = f"Originais:   {originais_str}\nTranspostos: {transpostos_str}"
            st.code(texto_para_copiar, language="text")
            if expl_in:
                with st.expander("ℹ️ Informações Adicionais"):
                    st.markdown("**Notas na sua sequência original:**")
                    for e in expl_in:
                        st.info(e)

# --- ABA 2: TRANSPOR CIFRA COMPLETA (COM LÓGICA DE DOWNLOAD) ---
with tab_cifra:
    st.markdown("Use esta aba para colar o texto de uma cifra completa ou enviar um arquivo (.txt, .docx).")
    
    input_tab1, input_tab2 = st.tabs(["📄 Colar Texto", "📁 Enviar Arquivo"])
    texto_cifra = ""
    nome_original = ""
    with input_tab1:
        texto_cifra_area = st.text_area("Cole a cifra completa aqui:", height=300, key="texto_area")
        if texto_cifra_area:
            texto_cifra = texto_cifra_area
            nome_original = "cifra_colada"
    with input_tab2:
        uploaded_file = st.file_uploader("Escolha um arquivo", type=['txt', 'docx'], key="uploader")
        if uploaded_file:
            texto_cifra = ler_arquivo(uploaded_file)
            nome_original = uploaded_file.name.split('.')[0]
            if texto_cifra:
                st.success("Arquivo carregado!")
    
    if st.button("Transpor Cifra Inteira!", type="primary", use_container_width=True, key="transpor_cifra"):
        if not texto_cifra:
            st.warning("Por favor, cole um texto ou envie um arquivo com a cifra.")
        else:
            # Salva o resultado no session_state para que ele persista
            st.session_state.cifra_transposta = processar_cifra(texto_cifra, acao, intervalo)
            st.session_state.nome_arquivo = f"{nome_original}_transposta.txt"

    # --- ÁREA DE RESULTADO E DOWNLOAD ---
    # Esta seção agora fica fora do "if button" e lê o resultado do session_state.
    # Isso garante que o resultado e o botão de download permaneçam na tela.
    if st.session_state.cifra_transposta:
        st.subheader("🎸 Cifra Transposta")
        st.code(st.session_state.cifra_transposta, language='text')
        
        # O botão de download
        st.download_button(
            label="📥 Baixar Cifra Transposta (.txt)",
            data=st.session_state.cifra_transposta.encode('utf-8'),
            file_name=st.session_state.nome_arquivo,
            mime='text/plain',
            use_container_width=True
        )

# --- Rodapé ---
st.markdown("---")
st.markdown("Desenvolvido para a Glória de Deus.\nCopyright © Rafael Panfil")