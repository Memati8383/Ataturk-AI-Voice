import customtkinter as ctk
import threading
import ollama
from main import ataturk_konus, system_prompt
import sys
import os

# --- GUI Ayarları ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class AtaturkAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Atatürk AI - Sesli Asistan")
        self.geometry("1100x700")

        # Grid Layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Sol Panel) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ATATÜRK AI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_desc = ctk.CTkLabel(self.sidebar_frame, text="Cumhuriyetin Sesi", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.sidebar_desc.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Model Seçimi
        self.model_label = ctk.CTkLabel(self.sidebar_frame, text="Ollama Modeli:", anchor="w")
        self.model_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        
        self.model_option_menu = ctk.CTkOptionMenu(self.sidebar_frame, dynamic_resizing=False, command=self.change_model)
        self.model_option_menu.grid(row=3, column=0, padx=20, pady=(10, 10))
        
        # Modelleri Çek
        self.load_models()

        # Boşluk
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Görünüm Modu:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        self.current_model = "llama3"

        # --- Ana Chat Alanı (Sağ Panel) ---
        self.chat_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chat_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Sohbet Geçmişi
        self.chat_history = ctk.CTkTextbox(self.chat_frame, width=400, font=ctk.CTkFont(size=14))
        self.chat_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_history.configure(state="disabled")

        # Giriş Alanı ve Buton
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Efendiler, bir sorunuz mu var? (Örn: Cumhuriyet nedir?)", height=40, font=ctk.CTkFont(size=14))
        self.entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")
        self.entry.bind("<Return>", self.send_event)

        self.send_button = ctk.CTkButton(self.input_frame, text="Gönder", width=100, height=40, command=self.send_message_thread)
        self.send_button.grid(row=0, column=1, padx=0, pady=0)
        
        # Durum Çubuğu
        self.status_label = ctk.CTkLabel(self.chat_frame, text="Hazır", text_color="gray", anchor="w")
        self.status_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Konuşma Durumu (Thread çakışmasını önlemek için basit flag)
        self.is_speaking = False

    def load_models(self):
        try:
            response = ollama.list()
            # ollama kütüphanesinin versiyonuna göre response bir dict veya nesne olabilir
            
            models_list = []
            
            # Nesne ise (yeni versiyonlar)
            if hasattr(response, 'models'):
                models_list = response.models
            # Dict ise ve models anahtarı varsa (eski versiyonlar)
            elif isinstance(response, dict) and 'models' in response:
                models_list = response['models']
            
            model_names = []
            for m in models_list:
                # Nesne ise .model, Dict ise ['model'] veya ['name']
                if hasattr(m, 'model'):
                    model_names.append(m.model)
                elif isinstance(m, dict):
                    model_names.append(m.get('model') or m.get('name'))
            
            # None değerleri temizle
            model_names = [name for name in model_names if name]

            if not model_names:
                print("Uyarı: Hiç model bulunamadı, varsayılan olarak llama3 eklendi.")
                model_names = ["llama3"] # Fallback

            self.model_option_menu.configure(values=model_names)
            
            # Varsayılan model seçimi
            default_model = next((m for m in model_names if "llama3" in m), model_names[0])
            self.model_option_menu.set(default_model)
            self.current_model = default_model
            
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            # Hata durumunda boş bırakmak yerine manuel giriş imkanı verelim veya varsayılan ekleyelim
            self.model_option_menu.configure(values=["llama3"])
            self.model_option_menu.set("llama3")
            self.current_model = "llama3"

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_model(self, new_model: str):
        self.current_model = new_model
        print(f"Model değiştirildi: {new_model}")

    def send_event(self, event):
        self.send_message_thread()

    def send_message_thread(self):
        # 1. Kullanıcı girdisini ANA THREAD'de al
        user_input = self.entry.get()
        if not user_input.strip():
            return
            
        self.entry.delete(0, "end")
        
        # 2. UI güncellemelerini başlat
        self.append_chat("Siz", user_input)
        self.status_label.configure(text="Atatürk düşünüyor...", text_color="#F59E0B") # Amber
        self.send_button.configure(state="disabled")
        self.entry.configure(state="disabled")

        # 3. Arka plan thread'ini başlat
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()

    def process_message(self, user_input):
        try:
            # Ollama Çağrısı (Ağır işlem)
            response = ollama.chat(
                model=self.current_model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input},
                ],
            )
            ai_response = response['message']['content']
            
            # Cevabı UI'da göster (Main thread'e schedule et)
            self.after(0, lambda: self.on_response_ready(ai_response))
            
            # Seslendirme (Bu da ağır işlem, ama önce metni göstermek istiyoruz)
            self.after(0, lambda: self.status_label.configure(text="Ses hazırlanıyor...", text_color="#10B981"))
            
            # Ses işlemini burada yapabiliriz çünkü zaten thread içindeyiz
            # Ancak process_message içinde yaparsak UI donmaz.
            # ataturk_konus print ettiği için konsolu kirletebilir ama sorun değil.
            
            from main import ataturk_konus
            ataturk_konus(ai_response)
            
            self.after(0, lambda: self.status_label.configure(text="Hazır", text_color="gray"))

        except Exception as e:
            self.after(0, lambda: self.on_error(str(e)))
            
    def on_response_ready(self, response_text):
        self.append_chat("Atatürk", response_text)
        self.send_button.configure(state="normal")
        self.entry.configure(state="normal")
        self.entry.focus()
        
    def on_error(self, error_msg):
        self.append_chat("Sistem", f"Hata oluştu: {error_msg}")
        self.status_label.configure(text="Hata", text_color="red")
        self.send_button.configure(state="normal")
        self.entry.configure(state="normal")

    def append_chat(self, sender, message):
        self.chat_history.configure(state="normal")
        
        if sender == "Siz":
            self.chat_history.insert("end", f"\n[Siz]: {message}\n", "user_tag")
        elif sender == "Atatürk":
            self.chat_history.insert("end", f"\n==================================================\n", "separator")
            self.chat_history.insert("end", f"[Atatürk]:\n{message}\n", "ai_tag")
            self.chat_history.insert("end", f"==================================================\n", "separator")
        else:
            self.chat_history.insert("end", f"\n[{sender}]: {message}\n")
            
        self.chat_history.see("end")
        self.chat_history.configure(state="disabled")

if __name__ == "__main__":
    app = AtaturkAIApp()
    app.mainloop()
