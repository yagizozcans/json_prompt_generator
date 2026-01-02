from google import genai
import os

class GeminiEngine:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash'

    def generate_response(self, user_input, context_examples=None):
        """
        Generates a response using Google Gemini 2.0 Flash.
        
        Args:
            user_input (str): The user's message.
            context_examples (list): List of similar examples for Few-Shot learning.
        """
        
        system_instructions = """
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
        
        # Construct the prompt with context
        full_prompt = system_instructions + "\n\n"
        
        if context_examples:
            full_prompt += "REFERANS ALINACAK BAŞARILI ÖRNEKLER (RAG Context):\n"
            for example in context_examples:
                full_prompt += f"- {example}\n"
            full_prompt += "\n"
            
        full_prompt += f"KULLANICI İSTEĞİ: {user_input}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"
