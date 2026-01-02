import chromadb
import pandas as pd
import os
import json
from sklearn.model_selection import train_test_split
from chromadb.utils import embedding_functions

class RAGManager:
    def __init__(self, excel_path="data/sd_prompts.xlsx", db_path="database/chroma_db", test_data_path="data/test_set.json"):
        self.excel_path = excel_path
        self.db_path = db_path
        self.test_data_path = test_data_path
        self.collection_name = "stable_diffusion_prompts"
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize client with persistence
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Use default embedding function (all-MiniLM-L6-v2)
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_func
        )
        
        # Initialize DB if empty
        if self.collection.count() == 0:
            self.initialize_db()

    def initialize_db(self):
        """Loads data from Excel, splits into Train/Test, and populates the vector database with Train set."""
        if not os.path.exists(self.excel_path):
            print(f"Warning: Excel file not found at {self.excel_path}")
            return False

        try:
            df = pd.read_excel(self.excel_path)
            
            # --- TEST SETİ MANTIĞI ---
            # Eğer test_set.json ZATEN VARSA ve doluysa, onu koru.
            # Veritabanına sadece bu test setinde OLMAYAN verileri yükle.
            
            test_data_exists = False
            if os.path.exists(self.test_data_path):
                try:
                    with open(self.test_data_path, 'r', encoding='utf-8') as f:
                        existing_test_data = json.load(f)
                        if len(existing_test_data) > 0:
                            test_data_exists = True
                            print(f"Existing test set found ({len(existing_test_data)} samples). Protecting it.")
                except:
                    pass

            if test_data_exists:
                # Test setindeki soruları ana veriden çıkar (Basit eşleşme ile)
                test_texts = [item['text'] for item in existing_test_data]
                train_df = df[~df['user_input'].isin(test_texts)]
                
                print(f"Using existing Test Set. Train Data: {len(train_df)} samples loaded to DB.")
                
            else:
                # Test seti yoksa OLUŞTUR (İlk sefer)
                print("No existing test set found. Creating new one with Extended Cases...")
                
                manual_hard_test_cases = [
                    # 1. Çeldirici: "Prompt" kelimesi geçen sorular (Intent: explain_term / text)
                    {"user_input": "Prompt mühendisliği nedir?", "intent": "explain_term"},
                    {"user_input": "Bana prompt üretme, sadece saati söyle.", "intent": "unknown"},
                    {"user_input": "Json çıktısı nasıl görünür?", "intent": "explain_term"},
                    
                    # 2. Çeldirici: Görsel isteği ama çok soyut/negatif (Intent: generate_json)
                    {"user_input": "Hiçbir şeyin olmadığı bir boşluk çiz.", "intent": "generate_json"},
                    {"user_input": "Bana hüzünlü bir şarkı gibi hissettiren bir resim yap.", "intent": "generate_json"},
                    
                    # 3. Selamlama / Sohbet (Intent: greeting)
                    {"user_input": "Merhaba, nasılsın?", "intent": "greeting"},
                    {"user_input": "Selam, bugün hava nasıl?", "intent": "greeting"},
                    {"user_input": "Günaydın!", "intent": "greeting"},
                    
                    # 4. Vedalaşma (Intent: greeting / farewell)
                    {"user_input": "Görüşürüz, kendine iyi bak.", "intent": "greeting"},
                    {"user_input": "Baybay", "intent": "greeting"},
                    {"user_input": "Çıkış yapıyorum.", "intent": "greeting"},
                    
                    # 5. Reddetme / Olumsuz Emirler (Intent: unknown veya greeting)
                    {"user_input": "Hayır, bunu istemiyorum.", "intent": "unknown"},
                    {"user_input": "Vazgeçtim, yapma.", "intent": "unknown"},
                    {"user_input": "Kötü cevap verdin.", "intent": "unknown"},
                    
                    # 6. Sepet / Ürün İşlemleri (E-Ticaret Senaryoları - Kapsam Dışı / unknown)
                    {"user_input": "Bu ürünü sepete ekle.", "intent": "unknown"},
                    {"user_input": "Siparişim nerede kaldı?", "intent": "unknown"},
                    {"user_input": "Ürünü iade etmek istiyorum.", "intent": "unknown"},
                    {"user_input": "Fiyatı ne kadar?", "intent": "unknown"},
                    
                    # 7. Konuya Özgü Teknik Sorular (Intent: explain_term)
                    {"user_input": "Seed -1 ne demek?", "intent": "explain_term"},
                    {"user_input": "Negative prompt ne işe yarar?", "intent": "explain_term"},
                    
                    # 8. Normal Görsel İstekleri (Intent: generate_json)
                    {"user_input": "Kırmızı araba", "intent": "generate_json"},
                    {"user_input": "Uzayda süzülen astronot", "intent": "generate_json"}
                ]
                
                # Mevcut veriden %5 rastgele al, üzerine zor örnekleri ekle
                train_df, random_test_df = train_test_split(df, test_size=0.05, random_state=42)
                
                # DataFrame formatına çevir
                hard_test_df = pd.DataFrame(manual_hard_test_cases)
                
                # Test seti = Rastgele %5 + Yeni Manuel Örnekler
                final_test_df = pd.concat([random_test_df, hard_test_df], ignore_index=True)
                
                # Save Test Data for Evaluation
                test_data_list = []
                for _, row in final_test_df.iterrows():
                    test_data_list.append({
                        "text": str(row['user_input']),
                        "expected_intent": str(row['intent'])
                    })
                
                with open(self.test_data_path, 'w', encoding='utf-8') as f:
                    json.dump(test_data_list, f, indent=2, ensure_ascii=False)
                print(f"New Test Data saved to {self.test_data_path} with {len(test_data_list)} samples.")

            # Populate ChromaDB with ONLY Train Data
            ids = [str(i) for i in range(len(train_df))] # Re-index IDs
            documents = []
            metadatas = []
            
            for _, row in train_df.iterrows():
                doc_text = f"Input: {row['user_input']}. Style: {row.get('style_tags', '')}"
                documents.append(doc_text)
                
                meta = {
                    "user_input": str(row['user_input']),
                    "intent": str(row['intent']),
                    "style_tags": str(row.get('style_tags', '')),
                    "json_output": str(row['json_output'])
                }
                metadatas.append(meta)

            if documents:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"Successfully added {len(documents)} documents to ChromaDB (Train Set).")
                return True
            return False
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

    def refresh_db(self):
        """Clears and reloads the database from Excel source."""
        try:
            print("Refreshing database...")
            # Delete existing collection
            self.client.delete_collection(self.collection_name)
            
            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_func
            )
            
            # Repopulate
            return self.initialize_db()
        except Exception as e:
            print(f"Error refreshing database: {e}")
            return False

    def query_db(self, query_text, n_results=3):
        """Retrieves most relevant examples for the query."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
                
            n_results = min(n_results, count)
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results for LLM context
            context_examples = []
            if results['metadatas'] and len(results['metadatas']) > 0:
                for meta in results['metadatas'][0]:
                    example = f"User Input: {meta['user_input']}\nJSON Output: {meta['json_output']}"
                    context_examples.append(example)
            
            return context_examples
            
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
