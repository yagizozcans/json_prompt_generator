# Product Requirements Document (PRD)
## Proje Adı: StableGen Assistant - AI Supported Prompt Engineering Chatbot

### 1. Giriş ve Amaç
**StableGen Assistant**, kullanıcıların metin tabanlı basit fikirlerini, Stable Diffusion gibi görüntü üretim modelleri (Image Generation Models) için optimize edilmiş, teknik detaylar içeren **JSON formatındaki** gelişmiş promptlara dönüştüren bir yapay zeka asistanıdır.

Bu proje, RAG (Retrieval-Augmented Generation) mimarisini ve Intent Classification (Niyet Sınıflandırma) yöntemlerini kullanarak, **OpenAI (GPT)** ve **Google (Gemini)** modellerinin performanslarını karşılaştırmalı olarak analiz etmeyi amaçlar.

### 2. Hedef Kitle
* Stable Diffusion, Midjourney veya Flux modellerini kullanan dijital sanatçılar.
* Prompt mühendisliği (Prompt Engineering) konusunda teknik bilgisi az olan kullanıcılar.
* Otomasyon süreçlerinde JSON formatında çıktıya ihtiyaç duyan geliştiriciler.

### 3. Kullanıcı Hikayeleri ve Akış
1.  **Prompt Üretimi:** Kullanıcı "Siberpunk bir İstanbul manzarası" yazar; sistem bunu `positive_prompt`, `negative_prompt`, `cfg_scale` gibi parametrelerle dolu bir JSON'a çevirir.
2.  **Stil Danışmanlığı (RAG):** Kullanıcı belirli bir sanatçı tarzı istediğinde, sistem veritabanından o sanatçıya ait en iyi prompt keyword'lerini çeker ve üretime dahil eder.
3.  **Teknik Destek:** Kullanıcı "CFG Scale nedir?" diye sorduğunda sistem teknik açıklama yapar.

### 4. Teknik Mimari ve Yöntem

#### 4.1. Kullanılan Teknolojiler
* **Arayüz:** Streamlit (Python)
* **LLM Modelleri:**
    * Model A: OpenAI GPT-4o / GPT-3.5 Turbo
    * Model B: Google Gemini Pro 1.5
* **Veri Tabanı (RAG):** ChromaDB (Vektör Veritabanı)
* **Veri Kaynağı:** `stable_diffusion_prompts.xlsx` (Min. 1000 satır veri - Sentetik ve Real Data)

#### 4.2. Intent Classification (Niyet Sınıflandırma)
Sistem, kullanıcı girdisini aşağıdaki sınıflardan birine dahil eder:
* `generate_json`: Yeni bir prompt oluşturma isteği.
* `refine_json`: Mevcut promptu revize etme isteği.
* `explain_term`: Teknik terim açıklama isteği.
* `greeting`: Selamlama/Sohbet.
* `unknown`: Kapsam dışı.

#### 4.3. RAG Akışı (Retrieval)
Eğer niyet `generate_json` ise:
1.  Kullanıcı girdisi embedding'e çevrilir.
2.  ChromaDB üzerinden en benzer "başarılı prompt örnekleri" çekilir.
3.  LLM'e şu formatta gönderilir:
    > "Kullanıcı isteği: X. Benzer başarılı örnekler: Y, Z. Buna dayanerek JSON çıktısı üret."

### 5. Veri Seti Yapısı
Veri seti `.xlsx` formatında tutulacak ve aşağıdaki sütunları içerecektir:

| Sütun Adı | Açıklama | Örnek Veri |
| :--- | :--- | :--- |
| `user_input` | Kullanıcının ham girdisi | "Yağmurlu orman, sinematik ışık" |
| `intent` | Niyet sınıfı | `generate_json` |
| `style_tags` | RAG için anahtar kelimeler | "nature, cinematic, rain, 8k" |
| `json_output` | Beklenen ideal JSON çıktısı | `{"positive": "...", "steps": 30}` |

### 6. Model Karşılaştırma Metrikleri (Başarı Kriterleri)
Proje sonunda iki model (GPT vs Gemini) şu kriterlere göre kıyaslanacaktır:

#### 6.1. Sınıflandırma Performansı (Intent Classification)
Test veri seti üzerindeki doğruluk oranları:
* **Precision (Kesinlik):** Modelin "Bu generate isteğidir" dediği tahminlerin ne kadarı doğru?
* **Recall (Duyarlılık):** Gerçek "generate" isteklerinin ne kadarını yakalayabildi?
* **F1 Score:** Denge skoru.

#### 6.2. JSON Yapısal Doğruluğu
* Üretilen çıktının `json.loads()` ile hatasız parse edilip edilemediği.
* Gerekli anahtarların (`positive_prompt`, `steps` vb.) eksiksiz olup olmadığı.

### 7. Dosya ve Klasör Yapısı
```text
PROJE_ROOT/
├── .env                     # API Keyleri
├── app.py                   # Streamlit Ana Uygulaması
├── requirements.txt         # Kütüphaneler
├── PRD.md                   # Proje Dokümanı
├── data/
│   ├── sd_prompts_train.xlsx  # Eğitim/RAG Verisi
│   └── sd_prompts_test.xlsx   # Performans Test Verisi
├── database/
│   └── chroma_db/           # Vektör Veritabanı Dosyaları
├── models/
│   ├── __init__.py
│   ├── gpt_engine.py        # OpenAI Entegrasyonu
│   ├── gemini_engine.py     # Google Gemini Entegrasyonu
│   └── rag_manager.py       # Embedding ve Retrieval İşlemleri
└── utils/
    ├── metrics.py           # Precision/Recall Hesaplama
    └── data_loader.py       # Excel Okuma İşlemleri