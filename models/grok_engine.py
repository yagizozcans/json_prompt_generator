from openai import OpenAI
import json

class GrokEngine:
    def __init__(self, api_key):
        # xAI uses the OpenAI SDK format but with a different base URL
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
        self.model = "grok-2-latest" # Using the latest model as per xAI docs

    def generate_response(self, user_input, context_examples=None):
        """
        Generates a response using xAI Grok.
        
        Args:
            user_input (str): The user's message.
            context_examples (list): List of similar examples for Few-Shot learning.
        """
        
        system_prompt = """
        Sen "StableGen Assistant" adında bir yapay zeka asistanısın.
        Görevin: Kullanıcıların metin tabanlı fikirlerini Stable Diffusion için optimize edilmiş JSON formatına dönüştürmek veya teknik konularda bilgi vermek.
        
        KURALLAR:
        1. Eğer kullanıcı bir görsel, resim, çizim veya sahne tasviri istiyorsa (Niyet: generate_json):
           - SADECE geçerli bir JSON objesi döndür.
           - Markdown blokları (```json ... ```) KULLANMA.
           - ÖNCELİK: Eğer RAG Context içinde (Referans Örnekler) kullanıcı isteğine benzer karmaşık bir JSON yapısı (blueprint, scene_graph, actors vb.) varsa, MUTLAKA o yapıyı ve detay seviyesini takip et.
           - Eğer RAG'dan özel bir yapı gelmezse bile varsayılan yapıyı zenginleştir. Sadece `positive_prompt` değil, `scene_description`, `lighting`, `camera_settings` gibi alt alanlar ekle.
           
           Örnek Zengin Yapı (Eğer RAG'da yoksa bunu kullan):
           {
             "scene": {
               "description": "Detaylı sahne açıklaması...",
               "mood": "Atmosfer ve duygu...",
               "lighting": "Işıklandırma detayları..."
             },
             "subject": {
               "description": "Ana obje/karakter detayları...",
               "pose": "Duruş veya pozisyon..."
             },
             "technical": {
               "camera": "Lens ve kamera tipi...",
               "style": "Sanat stili (örn: fotorealistik, yağlı boya)..."
             },
             "generation_params": {
               "positive_prompt": "Tüm detayların birleştiği ana prompt...",
               "negative_prompt": "İstenmeyen özellikler...",
               "cfg_scale": 7.0,
               "steps": 30,
               "sampler": "Euler a"
             }
           }
           - Positive prompt içine RAG ile gelen stil önerilerini veya kullanıcının istediği stili yedir.
        
        2. Eğer kullanıcı teknik bir terim soruyor veya sohbet ediyorsa (Niyet: explain_term / greeting):
           - Normal, açıklayıcı bir metin (String) olarak cevap ver.
           - JSON döndürme.
           
        3. Asla yorum satırı ekleme, sadece istenen formatı ver.
        """
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add Few-Shot Examples if provided (Context from RAG)
        if context_examples:
            for example in context_examples:
                messages.append({"role": "user", "content": "Örnek Bağlam (RAG): " + example})
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with xAI Grok: {str(e)}"
