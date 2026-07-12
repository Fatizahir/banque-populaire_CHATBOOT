import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

# 1. Configuration visuelle et Charte Graphique "Banque Populaire"
st.set_page_config(page_title="BP Assistant - Banque Populaire", page_icon="🏦", layout="wide")

# Personnalisation des couleurs (Bleu Banque Populaire)
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #005aa7; color: white; border-radius: 8px; }
    .stChatInput>div { border-color: #005aa7 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Assistant Virtuel — Banque Populaire")
st.caption("Votre conseiller IA pour vos simulations de crédit, épargne et l'analyse de vos justificatifs.")

# 2. Récupération de la clé API Gemini depuis les Secrets Streamlit
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Option de secours visuelle si la clé n'est pas configurée dans les Secrets
    api_key = st.sidebar.text_input("Entrez votre clé API Gemini", type="password")

if not api_key:
    st.info("Veuillez configurer votre clé API Gemini dans les Secrets de Streamlit pour activer le chatbot.", icon="🔑")
    st.stop()

# Configuration globale de l'API Google
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Initialisation de l'historique de discussion
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["Bonjour ! Je suis votre conseiller virtuel Banque Populaire. Comment puis-je vous accompagner dans vos projets ou l'analyse de vos documents aujourd'hui ?"]}
    ]

# Consigne système pour donner le rôle de banquier à l'IA
system_instruction = (
    "Tu es un conseiller client expert, virtuel et officiel de la Banque Populaire. "
    "Tu t'exprimes de manière très courtoise, professionnelle, claire et chaleureuse. "
    "Tu aides les clients pour leurs comptes, crédits immobiliers/automobiles, épargne et démarches. "
    "Réponds impérativement en français."
)

# 4. Espace Documents (Barre latérale) - Fonctionnalité demandée
st.sidebar.header("📁 Espace Documents (Analyse)")
st.sidebar.write("Déposez un justificatif (Avis d'imposition, RIB, pièce d'identité...) pour l'analyser.")
uploaded_file = st.sidebar.file_uploader("Choisir un fichier...", type=["pdf", "png", "jpg", "jpeg"])

context_document = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        # Extraction du texte du PDF
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            context_document = f"\n[DOCUMENT CLIENT JOINT : {text[:2500]}]"
            st.sidebar.success("✅ Document PDF chargé avec succès !")
        except Exception as e:
            st.sidebar.error(f"Erreur lors de la lecture du PDF : {e}")
    else:
        # Affichage de l'image importée
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Aperçu du justificatif", use_container_width=True)
        context
