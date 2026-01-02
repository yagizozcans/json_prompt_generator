# 🎨 StableGen Assistant - AI Supported Prompt Engineering Chatbot

**StableGen Assistant**, kullanıcıların basit metin fikirlerini Stable Diffusion gibi görsel üretim modelleri için optimize edilmiş, teknik parametreler içeren **JSON formatındaki** profesyonel promptlara dönüştüren bir yapay zeka asistanıdır.

Bu proje, **RAG (Retrieval-Augmented Generation)** mimarisini ve **Intent Classification (Niyet Sınıflandırma)** yöntemlerini kullanarak, **xAI (Grok-2)** ve **Google (Gemini 2.0 Flash)** modellerinin performanslarını karşılaştırmalı olarak analiz etmeyi amaçlar.

---

## 🚀 Özellikler

*   **Akıllı Prompt Üretimi:** "Siberpunk İstanbul" gibi basit bir girdiyi `positive_prompt`, `negative_prompt`, `cfg_scale` ve `steps` içeren detaylı bir JSON çıktısına dönüştürür.
*   **RAG Destekli Stil Önerileri:** ChromaDB vektör veritabanı sayesinde, kullanıcının isteğine en uygun başarılı prompt örneklerini (Few-Shot Learning) bularak modelin daha kaliteli çıktı üretmesini sağlar.
*   **Niyet Analizi (Intent Classification):** Kullanıcının görsel mi istediğini yoksa teknik bir soru mu sorduğunu ("CFG Scale nedir?") otomatik algılar.
*   **Model Karşılaştırma Modülü:** xAI Grok-2 ve Google Gemini 2.0 Flash modellerini aynı test seti üzerinde yarıştırarak **Precision**, **Recall** ve **F1 Score** metriklerini hesaplar ve görselleştirir.
*   **İnteraktif Performans Analizi:** Test sonuçlarını ve model cevaplarını arayüz üzerinden anlık inceleme imkanı sunar.

---

## 🛠️ Teknolojiler

*   **Arayüz:** Streamlit (Python)
*   **LLM Modelleri:**
    *   🚀 **xAI Grok-2** (OpenAI alternatifi olarak entegre edildi)
    *   ⚡ **Google Gemini 2.0 Flash**
*   **Vektör Veritabanı:** ChromaDB
*   **Embedding Modeli:** Sentence Transformers (`all-MiniLM-L6-v2`)
*   **Veri Analizi:** Pandas, Scikit-learn

---

## 📂 Proje Yapısı

```text
PROJE_ROOT/
├── app.py                   # Streamlit Ana Uygulaması (Arayüz)
├── requirements.txt         # Gerekli Kütüphaneler
├── .env                     # API Anahtarları (Şablon)
├── data/
│   ├── dummy_data_generator.py # Sentetik Veri Üretici Script
│   ├── sd_prompts.xlsx       # Ana Veri Seti (Train + Test)
│   └── test_set.json         # Otomatik Ayrılan Test Verisi (%20)
├── models/
│   ├── grok_engine.py        # xAI Grok API Wrapper
│   ├── gemini_engine.py      # Google Gemini API Wrapper
│   └── rag_manager.py        # RAG ve ChromaDB İşlemleri
└── utils/
    ├── evaluation.py         # Performans Testi ve Metrik Hesaplama
    └── helpers.py            # Yardımcı Fonksiyonlar (JSON Parsing vb.)
```

---

## ⚙️ Kurulum

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/kullaniciadi/StableGen-Assistant.git
    cd StableGen-Assistant
    ```

2.  **Sanal Ortam Oluşturun (Önerilen):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Anahtarlarını Ayarlayın:**
    `.env` dosyasını oluşturun ve anahtarlarınızı ekleyin:
    ```ini
    XAI_API_KEY=xai-...
    GOOGLE_API_KEY=AIza...
    ```

---

## ▶️ Kullanım

Uygulamayı başlatmak için terminalde şu komutu çalıştırın:

```bash
streamlit run app.py
```

### 1. Chatbot Modu
*   Sol panelden model seçimi yapın (Grok-2 veya Gemini 2.0).
*   Chat ekranına bir fikir yazın (örn: *"Van Gogh tarzında yıldızlı gece"*).
*   Asistan size Stable Diffusion'da kullanabileceğiniz hazır bir JSON çıktısı verecektir.

### 2. Veritabanı Güncelleme
*   Sol paneldeki **"Veritabanını Güncelle"** butonuna basarak Excel dosyasındaki verilerin `%80`'ini RAG veritabanına, `%20`'sini test setine ayırın.

### 3. Performans Analizi
*   **"Performans Analizi"** sekmesine geçin.
*   **"🚀 Testi Başlat"** butonuna tıklayın.
*   Modellerin zorlayıcı test sorularına verdiği yanıtları, doğruluk skorlarını (F1 Score) ve grafiklerini inceleyin.

---

## 📊 Örnek Çıktı (JSON)

Kullanıcı Girdisi: *"Siberpunk İstanbul manzarası"*

```json
{
  "positive_prompt": "cyberpunk istanbul cityscape, neon lights, futuristic skyscrapers, rain, night, highly detailed, 8k, unreal engine 5 render, galata tower cyberpunk style",
  "negative_prompt": "blur, low quality, distortion, watermark, text, daytime",
  "cfg_scale": 7.0,
  "steps": 30,
  "sampler": "Euler a"
}
```

---

## 📝 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.




