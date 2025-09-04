# app_final.py
import streamlit as st
import re
import docx
import io

# ==============================================================================
# 1. LÓGICA E FUNÇÕES (UNIÃO DOS DOIS ARQUIVOS)
# ==============================================================================

# --- Dicionários e Mapas (comuns a ambas as funcionalidades) ---
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
# (O dicionário EXPLICACAO_ENARMONICA_SAIDA não estava sendo usado na sua última versão,
# mas posso adicioná-lo de volta se você quiser as explicações de notas como C##)

# --- Funções para a "Transposição de Sequência" (do seu app.py) ---
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
        
        # Lógica para transpor a nota do baixo (ex: G/B)
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
                acorde_transposto_final = f"{nova_nota_fundamental}{qualidade_acorde}" # Baixo não reconhecido
        else:
            acorde_transposto_final = f"{nova_nota_fundamental}{qualidade_acorde}"
            
        acordes_transpostos.append(acorde_transposto_final)

    # (A variável expl_out não estava sendo usada, então simplifiquei o retorno)
    return acordes_transpostos, list(explicacoes_entrada)

# --- Funções para a "Transposição de Cifra Completa" (do app_cifras.py) ---
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

def processar_cifra(texto_cifra, acao, intervalo):
    semitons = int(intervalo * 2)
    if acao == 'Diminuir':
        semitons = -semitons

    # Expressão regular para encontrar acordes
    padrao_acorde = r'\b([A-G][b#]?)([^A-G\s,.\n]*)?(/[A-G][b#]?)?\b'
    
    def replacer(match):
        acorde_completo = match.group(0)
        nota_fundamental_str = match.group(1)
        qualidade = match.group(2) or ""
        baixo = match.group(3) or ""
        
        # Transpõe a nota fundamental
        nova_nota_fundamental = transpor_nota_individual(nota_fundamental_str, semitons)
        
        # Transpõe o baixo, se existir
        novo_baixo = ""
        if baixo:
            nota_baixo_str = baixo.replace('/', '')
            novo_baixo = "/" + transpor_nota_individual(nota_baixo_str, semitons)
            
        return f"{nova_nota_fundamental}{qualidade}{novo_baixo}"

    return re.sub(padrao_acorde, replacer, texto_cifra)

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
# 2. INTERFACE GRÁFICA COM STREAMLIT (UNIFICADA COM ABAS)
# ==============================================================================

st.set_page_config(page_title="Transpositor de Acordes", page_icon="🎵", layout="centered")

st.title("🎵 Transpositor Universal de Acordes")
st.markdown("Uma ferramenta completa para transpor tanto sequências simples de acordes quanto cifras de músicas inteiras.")

# --- CONTROLES DE TRANSPOSIÇÃO (COMUNS A AMBAS AS ABAS) ---
st.header("1. Escolha a transposição")
col1, col2 = st.columns(2)
with col1:
    acao = st.radio("Ação:", ('Aumentar', 'Diminuir'), horizontal=True)
with col2:
    intervalo = st.number_input("Intervalo (em tons):", 0.5, 12.0, 1.0, 0.5, help="0.5 = meio tom, 1 = um tom...")

st.header("2. Insira os acordes ou a cifra")

# --- ABAS PARA CADA FUNCIONALIDADE ---
tab_sequencia, tab_cifra = st.tabs(["Transpor Sequência", "Transpor Cifra Completa"])

# --- ABA 1: TRANSPOR SEQUÊNCIA DE ACORDES ---
with tab_sequencia:
    st.markdown("Use esta aba para transpor uma lista simples de acordes separados por espaço.")
    sequencia_input = st.text_input("Sequência de acordes:", placeholder="Ex: G D/F# Em C")

    if st.button("Transpor Sequência!", type="primary", use_container_width=True):
        if not sequencia_input:
            st.warning("Por favor, insira uma sequência de acordes.")
        else:
            acordes_originais = sequencia_input.strip().split()
            acordes_transpostos, expl_in = transpor_acordes_sequencia(acordes_originais, acao, intervalo)

            st.subheader("🎸 Resultado da Sequência")
            
            # Layout visual em colunas
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
            
            # Bloco para copiar
            st.subheader("📝 Copie os acordes aqui")
            originais_str = ' '.join(acordes_originais)
            transpostos_str = ' '.join(acordes_transpostos)
            texto_para_copiar = f"Originais:   {originais_str}\nTranspostos: {transpostos_str}"
            st.code(texto_para_copiar, language="text")

            # Informações adicionais
            if expl_in:
                with st.expander("ℹ️ Informações Adicionais"):
                    st.markdown("**Notas na sua sequência original:**")
                    for e in expl_in:
                        st.info(e)

# --- ABA 2: TRANSPOR CIFRA COMPLETA ---
with tab_cifra:
    st.markdown("Use esta aba para colar o texto de uma cifra completa ou enviar um arquivo (.txt, .docx).")
    
    # Sub-abas para os métodos de entrada
    input_tab1, input_tab2 = st.tabs(["📄 Colar Texto", "📁 Enviar Arquivo"])
    texto_cifra = ""
    with input_tab1:
        texto_cifra_area = st.text_area("Cole a cifra completa aqui:", height=300)
        if texto_cifra_area:
            texto_cifra = texto_cifra_area
    with input_tab2:
        uploaded_file = st.file_uploader("Escolha um arquivo", type=['txt', 'docx'])
        if uploaded_file:
            texto_cifra = ler_arquivo(uploaded_file)
            if texto_cifra:
                st.success("Arquivo carregado!")
    
    if st.button("Transpor Cifra Inteira!", type="primary", use_container_width=True):
        if not texto_cifra:
            st.warning("Por favor, cole um texto ou envie um arquivo com a cifra.")
        else:
            cifra_transposta = processar_cifra(texto_cifra, acao, intervalo)
            st.subheader("🎸 Cifra Transposta")
            st.code(cifra_transposta, language='text')

# --- Rodapé (seu copyright) ---
st.markdown("---")
st.markdown("Desenvolvido para a Glória de Deus.\nCopyright © Rafael Panfil")