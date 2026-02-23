import torch
import functools
import ollama
import edge_tts
import asyncio
import os
import uvicorn
import shutil
import subprocess
import signal
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

# --- Torch ve RVC Ayarları ---
try:
    from fairseq.data.dictionary import Dictionary
    from fairseq.tasks.hubert_pretraining import HubertPretrainingTask
    if hasattr(torch.serialization, 'add_safe_globals'):
        torch.serialization.add_safe_globals([Dictionary, HubertPretrainingTask])
except ImportError:
    pass

# Garantici yaklaşım: torch.load yaması
original_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = patched_load

# RVC Import
try:
    from rvc_python.infer import RVCInference
    print("RVC başarıyla yüklendi.")
except ImportError:
    print("RVC yükleme hatası: rvc_python kütüphanesi bulunamadı.")
    RVCInference = None

# --- Yapılandırma ---
MODEL_PATH = "models/mustafa-kemal-ataturk_1380e_42780s.pth" 
INDEX_PATH = "models/added_mustafa-kemal-ataturk_v2.index"

SYSTEM_PROMPT = """
Sen Türkiye Cumhuriyetinin kurucusu Mustafa Kemal Atatürksün. 
Şu kurallara sıkı sıkıya bağlı kal:
1. Üslubun: Vakur, ileri görüşlü, birleştirici ve entelektüel bir dil kullan. 
2. Hitap: Konuşmalarına 'Efendiler,' veya 'Çocuklarım,' gibi samimi ama saygın ifadelerle başla.
3. Rehberlik: Sorulara akıl, bilim ve mantık çerçevesinde cevap ver.
4. Karakteristik: Karamsarlıktan uzak, daima ümitvar ol. "Umutsuz durumlar yoktur, umutsuz insanlar vardır" felsefesini yansıt.
5. Dil: Güncel Türkçeyi akıcı kullan ama yer yer dönemin o asil duruşunu hissettiren kelimeler (istikbal, muvaffakiyet, azim vb.) seç.
"""

# Global variables
rvc_model = None
system_prompt = SYSTEM_PROMPT

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_rvc_model()
    yield
    print("Uygulama kapatılıyor...")




app = FastAPI(title="Atatürk AI API", lifespan=lifespan)

# --- Statik Dosyalar (Assets) ---
from fastapi.staticfiles import StaticFiles
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# --- Ses ve Chat Mantığı ---

async def metni_sese_cevir(metin, dosya_yolu):
    communicate = edge_tts.Communicate(metin, "tr-TR-AhmetNeural", rate="-5%", pitch="-5Hz")
    await communicate.save(dosya_yolu)

def convert_voice(input_path, output_path, pitch=0, index_rate=0.75, protect=0.33):
    if rvc_model:
        try:
            # Dinamik parametreleri ayarla
            rvc_model.set_params(f0method="rmvpe", f0up_key=pitch, index_rate=index_rate, protect=protect)
            print(f"RVC: Isleme baslatiliyor (Pitch: {pitch}, Index: {index_rate}, Protect: {protect})")
            rvc_model.infer_file(input_path=input_path, output_path=output_path)
            return True
        except Exception as e:
            print(f"RVC: Donusturme Hatasi: {e}")
            return False
    return False

def load_rvc_model():
    global rvc_model
    if not rvc_model and RVCInference:
        try:
            print(f"RVC: Model yukleniyor... (Device: cpu)")
            rvc_model = RVCInference(device="cpu")
            rvc_model.load_model(MODEL_PATH, index_path=INDEX_PATH)
            rvc_model.set_params(f0method="rmvpe", f0up_key=-2, index_rate=0.85, protect=0.33)
            print("RVC: Model hazir ve yuklendi.")
        except Exception as e:
            print(f"RVC: Model yukleme hatasi: {e}")
            rvc_model = None
    return rvc_model

def ataturk_konus(metin):
    """GUI için senkron seslendirme fonksiyonu"""
    load_rvc_model()
    
    temp_audio = "temp_voice.mp3"
    final_audio = "ataturk_cevap.wav"

    
    # 1. TTS
    asyncio.run(metni_sese_cevir(metin, temp_audio))
    
    # 2. RVC
    if rvc_model:
        success = convert_voice(temp_audio, final_audio)
    else:
        # Fallback
        print("RVC model yüklü değil, orijinal ses kullanılıyor.")
        shutil.copy(temp_audio, final_audio)
        success = True
        
    # 3. Oynat (Windows için)
    if success and os.path.exists(final_audio):
        try:
            import winsound
            # winsound sadece WAV destekler
            winsound.PlaySound(final_audio, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Ses çalma hatası: {e}")

class SpeakRequest(BaseModel):
    text: str
    pitch: float = 0
    index_rate: float = 0.75
    protect: float = 0.33

class SpeakResponse(BaseModel):
    audio_url: str
    message: str

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = ollama.chat(
            model=request.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': request.message},
            ],
        )
        return {"response": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama hatası: {str(e)}")

@app.get("/status")
async def get_status():
    ollama_ready = False
    try:
        ollama.list()
        ollama_ready = True
    except:
        ollama_ready = False
        
    return {
        "rvc_ready": rvc_model is not None,
        "ollama_ready": ollama_ready,
        "device": "cpu" # RVC currently on CPU
    }

@app.post("/speak", response_model=SpeakResponse)
async def speak_endpoint(request: SpeakRequest):
    print(f"API: /speak istegi alindi -> Metin: {request.text[:50]}...")
    try:
        if not request.text or len(request.text.strip()) == 0:
             raise HTTPException(status_code=400, detail="Lütfen bir metin giriniz.")

        temp_audio = "temp_voice.mp3"
        final_audio = "ataturk_output.wav"

        if os.path.exists(temp_audio): os.remove(temp_audio)
        if os.path.exists(final_audio): os.remove(final_audio)

        await metni_sese_cevir(request.text, temp_audio)

        conversion_success = False
        if rvc_model:
            conversion_success = await asyncio.to_thread(
                convert_voice, 
                temp_audio, 
                final_audio, 
                pitch=request.pitch,
                index_rate=request.index_rate,
                protect=request.protect
            )

        if not conversion_success:
            shutil.copy(temp_audio, final_audio)

        return SpeakResponse(
            audio_url="/audio",
            message="Seslendirme başarıyla tamamlandı."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio")
async def get_audio():
    output_path = "ataturk_output.wav"
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="audio/wav", filename="ataturk_ses.wav")
    raise HTTPException(status_code=404, detail="Ses dosyası bulunamadı")

@app.get("/")
async def read_root():
    return FileResponse("web/index.html")

if __name__ == "__main__":
    try:
        print("API Sunucusu Başlatılıyor...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        with open("crash_log.txt", "w") as f:
            import traceback
            traceback.print_exc(file=f)
        print(f"Sunucu hatası: {e}")

