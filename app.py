import streamlit as st
from openai import OpenAI
from PIL import Image
import pypdf

# 1. Configuration de la page et design "Banque Populaire"
st.set_page_config(page_title="BP Assistant - Banque Populaire", page_icon="🏦", layout="wide")

# Personnalisation CSS pour coller à la charte graphique (Bleu et Cyan/Orange)
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #005aa7; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { border-color: #005aa7; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Assistant Virtuel — Banque Populaire")
st.caption("Votre conseiller IA disponible 24h/24 pour vos projets et l'analyse de vos pièces justificatives.")

# 2. Gestion de la clé API sécurisée (via Streamlit Secrets)
# En local, vous pouvez utiliser st.text_input pour tester, mais sur Streamlit.io, on utilise st.secrets
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Entrez votre clé API OpenAI", type="password")

if not api_key:
    st.info("Veuillez configurer votre clé API pour interagir avec le chatbot.", icon="🔑")
    st.stop()

client = OpenAI(api_key=api_key)

# 3. Initialisation de l'historique de discussion
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un conseiller client expert de la Banque Populaire. Tu es courtois, professionnel et tu aides les clients dans leurs démarches de crédit, épargne et gestion de compte."},
        {"role": "assistant", "content": "Bonjour ! Je suis votre assistant Banque Populaire. Comment puis-je vous aider aujourd'hui ? (Ex: Simuler un prêt, analyser un document...)"}
    ]

# 4. Fonctionnalité Bonus : Analyse de fichiers (Sidebar)
st.sidebar.header("📁 Espace Documents (Bonus)")
st.sidebar.write("Déposez une pièce justificative pour l'analyser (ex: avis d'imposition, pièce d'identité).")
uploaded_file = st.sidebar.file_uploader("Choisir un PDF ou une Image...", type=["pdf", "png", "jpg", "jpeg"])

context_document = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        # Extraction du texte du PDF
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in pdf_reader.pages])
        context_document = f"\n[Document client joint : {text[:1500]}]" # Limite pour le prompt
        st.sidebar.success("✅ PDF chargé et lu avec succès !")
    else:
        # Traitement Image
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Aperçu de la pièce jointe", use_container_width=True)
        # Note : Pour analyser l'image directement, on peut utiliser gpt-4o (Vision)
        context_document = "\n[L'utilisateur a joint une image/photo de son justificatif.]"
        st.sidebar.info("💡 Image prête. Vous pouvez demander au bot de l'analyser dans le chat.")

# 5. Affichage des messages de la discussion
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with chat_message(msg["role"]):
            st.write(msg["content"])

# helper pour l'affichage propre
def chat_message(role):
    return st.chat_message("user" if role == "user" else "assistant")

# 6. Interaction avec l'utilisateur
if user_query := st.chat_input("Posez votre question ici..."):
    # Afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # Préparation du prompt incluant le contexte du document si présent
    messages_for_api = list(st.session_state.messages)
    if context_document:
        messages_for_api.append({"role": "system", "content": f"Contexte additionnel issu du fichier importé par le client : {context_document}"})

    # Appel à l'API LLM
    with st.chat_message("assistant"):
        with st.spinner("En cours de traitement..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # Modèle rapide et économique
                    messages=messages_for_api
                )
                answer = response.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")