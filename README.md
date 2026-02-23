<div align="center">

<img src="icon.png" alt="Atatürk AI Voice Banner" width="100%" style="border-radius: 20px; margin-bottom: 20px;">

# 🇹🇷 ATATÜRK AI VOICE

### _“Cumhuriyetin Sesi, Yapay Zeka ile Gelecekte”_

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![RVC](https://img.shields.io/badge/RVC-Voice_Conversion-FF6F00?style=for-the-badge)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

<p align="justify">
Bu proje, Türkiye Cumhuriyeti'nin kurucusu <b>Mustafa Kemal Atatürk</b>'ün sesini yapay zeka teknolojileri (RVC & TTS) kullanarak dijital ortama taşımayı hedefler. Gelişmiş ses dönüştürme algoritmaları sayesinde, girdiğiniz herhangi bir metni Ata'mızın o vakur ve asil sesiyle dinleyebilir, projelerinize entegre edebilirsiniz.
</p>

[Özellikler](#özellikler) • [Kurulum](#kurulum) • [API Kullanımı](#api-kullanımı) • [Arayüz](#arayüz) • [Katkıda Bulunma](#katkıda-bulunma)

</div>

<br>

## 🚀 Özellikler

- **🎭 RVC v2 Entegrasyonu:** En gerçekçi ses deneyimi için Retrieval-based Voice Conversion teknolojisi.
- **⚡ Akıllı API:** FastAPI tabanlı, hızlı ve dokümantasyonu hazır (Swagger) bir sunucu yapısı.
- **🖥️ Modern GUI:** CustomTkinter ile tasarlanmış, kullanıcı dostu masaüstü asistan arayüzü.
- **🌐 Web Arayüzü:** Tarayıcı üzerinden metin seslendirme ve ses dosyası indirme imkanı.
- **🧠 Ollama Entegrasyonu:** Atatürk'ün düşüncelerini ve üslubunu yansıtan AI Chat sistemi.

<br>

## 🛠️ Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- NVIDIA GPU (Hızlı işlem için opsiyonel, CPU desteği mevcuttur)
- [Ollama](https://ollama.com/) (Chat özelliği için)

### Adımlar

1. **Depoyu Klonlayın:**

   ```bash
   git clone https://github.com/Memati8383/Ataturk-AI-Voice.git
   cd Ataturk-AI-Voice
   ```

2. **Sanal Ortamı Hazırlayın:**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate # Linux/Mac
   ```

3. **Bağımlılıkları Yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Modelleri Yerleştirin:**
   `.pth` ve `.index` uzantılı model dosyalarınızın ana dizinde olduğundan emin olun.

<br>

## 📡 API Kullanımı

API sunucusunu başlatmak için:

```bash
python main.py
```

### Örnek İstek (Python)

```python
import requests

url = "http://localhost:8000/speak"
payload = {"text": "Ey Türk Gençliği! Birinci vazifen..."}
response = requests.post(url, json=payload)

if response.status_code == 200:
    audio_path = response.json()["audio_url"]
    print(f"Ses dosyası hazır: {audio_path}")
```

<br>

## 🎨 Arayüz (GUI)

Masaüstü asistanını kullanmak isterseniz:

```bash
python gui.py
```

Arayüz üzerinden hem Atatürk ile sohbet edebilir hem de verdigi cevapları sesli olarak dinleyebilirsiniz.

<br>

## 🔒 Yasal Uyarı ve Etik Kullanım

Bu proje tamamen **eğitim, anma ve teknolojik araştırma** amaçlı geliştirilmiştir. Mustafa Kemal Atatürk'ün aziz hatırasına saygı çerçevesinde kullanılması esastır. Sesin, yanıltıcı bilgiler üretmek veya uygunsuz içeriklerde kullanılmak amacıyla kullanılması kesinlikle önerilmez.

<br>

## 🤝 Katkıda Bulunma

1. Bu depoyu Fork'layın.
2. Yeni bir Feature Branch oluşturun (`git checkout -b feature/Gelistirme`).
3. Değişikliklerinizi Commit edin (`git commit -m 'Yeni özellik eklendi'`).
4. Branch'inizi Push edin (`git push origin feature/Gelistirme`).
5. Bir Pull Request açın.

---

<div align="center">
  <p><i>"Hayatta en hakiki mürşit ilimdir, fendir."</i> - Mustafa Kemal Atatürk</p>
  <b>Memati8383</b> tarafından ❤️ ile geliştirilmiştir.
</div>
