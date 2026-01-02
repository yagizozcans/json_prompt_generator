import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from models.rag_manager import RAGManager
from models.grok_engine import GrokEngine
from models.gemini_engine import GeminiEngine
from utils.helpers import extract_json, format_prompt_for_display
from utils.evaluation import evaluate_models

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="StableGen Assistant",
    page_icon="🎨",
    layout="wide"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_manager" not in st.session_state:
    with st.spinner("Veritabanı başlatılıyor..."):
        try:
            st.session_state.rag_manager = RAGManager()
        except Exception as e:
            st.error(f"RAG Modülü başlatılamadı: {e}")
            st.session_state.rag_manager = None

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Ayarlar")
    
    # API Key Management
    xai_key = os.getenv("XAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    user_xai_key = st.text_input("xAI API Key", value=xai_key if xai_key else "", type="password")
    user_google_key = st.text_input("Google API Key", value=google_key if google_key else "", type="password")
    
    st.info("API anahtarları .env dosyasından veya buradan girilebilir.")

    st.markdown("---")
    if st.button("Veritabanını Güncelle"):
        if st.session_state.rag_manager:
            with st.spinner("Veritabanı güncelleniyor..."):
                success = st.session_state.rag_manager.refresh_db()
                if success:
                    st.success("Veritabanı başarıyla güncellendi!")
                else:
                    st.error("Veritabanı güncellenirken hata oluştu.")
        else:
            st.error("RAG Yöneticisi başlatılamadı.")

# Main Interface Tabs
tab_chat, tab_perf = st.tabs(["💬 Chatbot", "📊 Performans Analizi"])

# --- TAB 1: CHAT INTERFACE ---
with tab_chat:
    st.title("🎨 StableGen Assistant")
    st.markdown("Stable Diffusion promptları oluşturun veya teknik terimleri öğrenin.")
    
    selected_model = st.radio(
        "Model Seçimi",
        ["xAI Grok-2", "Google Gemini 2.0 Flash"],
        horizontal=True
    )

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("is_json"):
                st.json(message["content"])
            else:
                st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Bir şeyler yazın... (Örn: 'Siberpunk İstanbul' veya 'CFG Scale nedir?')"):
        # Check API Keys
        if selected_model == "xAI Grok-2" and not user_xai_key:
            st.error("Lütfen xAI API Key giriniz.")
            st.stop()
        elif selected_model == "Google Gemini 2.0 Flash" and not user_google_key:
            st.error("Lütfen Google API Key giriniz.")
            st.stop()

        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt, "is_json": False})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner(f"{selected_model} ile cevap üretiliyor..."):
                # 1. RAG Retrieval
                context_examples = []
                if st.session_state.rag_manager:
                    context_examples = st.session_state.rag_manager.query_db(prompt)
                    with st.expander("RAG Context (Bulunan Benzer Örnekler)"):
                        for i, ex in enumerate(context_examples):
                            st.text(f"Example {i+1}:\n{ex}")
                
                # 2. LLM Generation
                response_content = ""
                try:
                    if selected_model == "xAI Grok-2":
                        engine = GrokEngine(api_key=user_xai_key)
                        response_content = engine.generate_response(prompt, context_examples)
                    else:
                        engine = GeminiEngine(api_key=user_google_key)
                        response_content = engine.generate_response(prompt, context_examples)
                    
                    # 3. Process Response (JSON vs Text)
                    json_data = extract_json(response_content)
                    
                    if json_data:
                        st.success("JSON Prompt Oluşturuldu!")
                        st.json(json_data)
                        st.session_state.messages.append({"role": "assistant", "content": json_data, "is_json": True})
                    else:
                        st.markdown(response_content)
                        st.session_state.messages.append({"role": "assistant", "content": response_content, "is_json": False})
                        
                except Exception as e:
                    st.error(f"Hata oluştu: {str(e)}")

# --- TAB 2: PERFORMANCE ANALYSIS ---
with tab_perf:
    st.title("📊 Model Performans Karşılaştırması")
    st.markdown("xAI Grok-2 ve Gemini 2.0 Flash modellerinin **Intent Classification** başarısını test edin.")
    
    st.info("Bu test, örnek sorular kullanarak modellerin 'JSON Üretme' ve 'Açıklama Yapma' niyetlerini ne kadar doğru ayırt ettiğini ölçer.")

    if st.button("🚀 Testi Başlat", type="primary"):
        progress_bar = st.progress(0)
        
        with st.spinner("Modeller test ediliyor... (Bu işlem biraz zaman alabilir)"):
            # Run Evaluation
            results_df, responses_log, test_data_used = evaluate_models(
                user_xai_key, 
                user_google_key, 
                progress_callback=lambda p: progress_bar.progress(p)
            )
        
        progress_bar.progress(100)
        st.success("Test Tamamlandı!")
        
        # Save results AND response logs to session state
        st.session_state.test_results = results_df
        st.session_state.test_logs = responses_log
        st.session_state.test_data_used = test_data_used

    if "test_results" in st.session_state:
        results_df = st.session_state.test_results
        
        # Display Results Table
        st.subheader("📈 Sonuç Tablosu")
        st.dataframe(results_df, use_container_width=True)
        
        # Display Charts
        st.subheader("📊 Metrik Karşılaştırması")
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("F1 Score Karşılaştırması")
            st.bar_chart(results_df.set_index("Model")["F1 Score"], color="#4CAF50")
            
        with col2:
            st.caption("Precision (Kesinlik) Karşılaştırması")
            st.bar_chart(results_df.set_index("Model")["Precision"], color="#2196F3")

        st.markdown("---")
        st.subheader("📝 Sonuçların Analizi")
        st.markdown("""
        **📊 Metriklerin Anlamı:**
        *   **Precision (Kesinlik):** Modelin *"Bu bir görsel isteğidir"* dediği durumların ne kadarı gerçekten görsel isteğiydi?
        *   **Recall (Duyarlılık):** Gerçek görsel isteklerinin ne kadarını model kaçırmadan yakaladı?
        *   **F1 Score:** Precision ve Recall'un harmonik ortalamasıdır.
        """)

        st.markdown("---")
        st.subheader("🔍 Detaylı İnceleme (Kaydedilmiş Sonuçlar)")
        
        if "test_logs" in st.session_state and "test_data_used" in st.session_state:
            responses_log = st.session_state.test_logs
            test_data_used = st.session_state.test_data_used
            
            selected_question_index = st.slider("İncelemek istediğiniz test sorusunu seçin:", 0, len(test_data_used)-1, 0)
            selected_question = test_data_used[selected_question_index]
            
            st.info(f"**Soru {selected_question_index + 1}:** {selected_question['text']}")
            st.caption(f"Beklenen Niyet: `{selected_question['expected_intent']}`")
            
            # Get cached responses for this question
            log_entry = responses_log.get(selected_question_index, {})
            
            col_grok, col_gemini = st.columns(2)
            
            with col_grok:
                st.markdown("#### xAI Grok-2")
                resp = log_entry.get("xAI Grok-2", "Veri yok")
                json_resp = extract_json(resp)
                
                if json_resp:
                    st.success("✅ JSON Üretti")
                    st.json(json_resp)
                else:
                    st.warning("📝 Metin Üretti")
                    st.write(resp)

            with col_gemini:
                st.markdown("#### Gemini 2.0 Flash")
                resp = log_entry.get("Google Gemini 2.0 Flash", "Veri yok")
                json_resp = extract_json(resp)
                
                if json_resp:
                    st.success("✅ JSON Üretti")
                    st.json(json_resp)
                else:
                    st.warning("📝 Metin Üretti")
                    st.write(resp)
        else:
            st.warning("Detaylı inceleme için önce testi başlatın.")
