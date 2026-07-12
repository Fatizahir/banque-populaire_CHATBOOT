import streamlit as st
import requests
import pypdf
from PIL import Image
import io

# 1. Configuration visuelle Banque Populaire
st.set_page_config(page_title="BP Assistant - Banque Populaire", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #005aa7; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Assistant Virtuel — Banque Populaire")
st.caption("Votre conseiller IA pour vos simulations de crédit et l'analyse de vos justificatifs.")

# 2. Récupération sécurisée de la clé API
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Clé API Gemini", type="password")

if not api_key:
    st.info("Veuillez configurer votre clé API Gemini dans les Secrets de Streamlit.", icon="🔑")
    st.stop()

# 3. Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre conseiller virtuel Banque Populaire. Comment puis-je vous accompagner aujourd'hui ?"}
    ]

# 4. Gestion des documents dans la barre latérale
st.sidebar.header("📁 Espace Documents")
uploaded_file = st.sidebar.file_uploader("Déposez un justificatif (PDF, Image)", type=["pdf", "png", "jpg", "jpeg"])

context_document = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            context_document = f"\n[Document client joint : {text[:1500]}]"
            st.sidebar.success("✅ PDF chargé avec succès !")
        except:
            st.sidebar.error("Erreur de lecture du PDF.")
    else:
        st.sidebar.image(Image.open(uploaded_file), caption="Aperçu", use_container_width=True)
        context_document = "\n[L'utilisateur a joint une image/photo comme justificatif.]"

# 5. Affichage du Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. Traitement des messages via Requête HTTP Directe (Évite les bugs de module)
if user_query := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # Préparation du prompt pour Gemini
    system_instruction = "Tu es un conseiller client expert de la Banque Populaire. Courtois et professionnel. Réponds en français."
    full_prompt = f"{system_instruction} {context_document} \n\nClient: {user_query}"

    with st.chat_message("assistant"):
        with st.spinner("Votre conseiller répond..."):
            try:
                # Appel direct à l'API Google sans passer par le module problématique
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                # Extraction du texte de la réponse
                answer = response_data['candidates'][0]['content']['parts'][0]['text']
                
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("Une erreur de communication est survenue. Vérifiez la validité de votre clé API dans les Secrets.")
