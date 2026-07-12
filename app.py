import streamlit as st
import requests

st.set_page_config(page_title="BP Assistant - Banque Populaire", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .stButton>button { background-color: #005aa7; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Assistant Virtuel — Banque Populaire")
st.caption("Votre conseiller IA pour vos simulations de crédit et l'analyse de vos justificatifs.")

# Récupération de la clé depuis les Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.info("Veuillez configurer votre clé API Gemini dans les Secrets de Streamlit.", icon="🔑")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre conseiller virtuel Banque Populaire. Comment puis-je vous accompagner aujourd'hui ?"}
    ]

st.sidebar.header("📁 Espace Documents")
uploaded_file = st.sidebar.file_uploader("Déposez un justificatif (PDF, Image)", type=["pdf", "png", "jpg", "jpeg"])

context_document = ""
if uploaded_file is not None:
    context_document = f"\n[Note : L'utilisateur a joint un document nommé {uploaded_file.name}]"
    st.sidebar.success("✅ Document pris en compte avec succès !")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_query := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    system_instruction = "Tu es un conseiller client expert de la Banque Populaire. Courtois, chaleureux et professionnel. Réponds en français."
    full_prompt = f"{system_instruction} {context_document} \n\nClient: {user_query}"

    with st.chat_message("assistant"):
        with st.spinner("Votre conseiller répond..."):
            try:
                # VERSION MISE À JOUR : Utilisation de gemini-2.5-flash sur l'API v1beta
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    answer = response_data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_msg = response_data.get('error', {}).get('message', 'Erreur de configuration')
                    answer = f"Désolé, impossible de répondre (Détail : {error_msg})"
                
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("Une erreur technique est survenue.")
