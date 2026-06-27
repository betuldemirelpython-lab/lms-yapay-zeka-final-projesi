# AI Destekli LMS – Kurulum ve Çalıştırma Rehberi

Bu proje, **Streamlit** tabanlı bir ön yüz, **FastAPI** tabanlı AI servisleri ve **SQLite** veritabanı kullanarak bir öğrenim yönetim sistemi (LMS) sunar.

## 📁 Proje Yapısı
```
lms-yapayzeka-final/
├─ app.py            # Streamlit UI
├─ ai_service.py     # FastAPI (AI analiz & özetleme)
├─ database.py       # SQLAlchemy + SQLite
├─ models.py         # Pydantic şemalar
├─ requirements.txt  # Bağımlılıklar
├─ .env.example      # Çevre değişkeni örneği
├─ run_all.bat       # Windows için tek komutla başlatma
└─ README.md         # Bu dosya
```

## 📦 Gereksinimler
- **Python 3.9+**
- **Windows** (komut dosyası `.bat` olarak hazırlanmıştır)

## ⚙️ Kurulum Adımları
1. **Depoyu indirin / klonlayın**
   ```bat
   git clone https://github.com/kullanici/ai-lms.git
   cd ai-lms\lms-yapayzeka-final
   ```
2. **`run_all.bat` dosyasını çalıştırın**
   ```bat
   run_all.bat
   ```
   Bu betik:
   - Sanal ortam (`venv`) oluşturur (eğer yoksa).
   - Bağımlılıkları `pip install -r requirements.txt` ile kurar.
   - `.env.example` dosyasını kopyalayıp `.env` oluşturur (anahtarları doldurun).
   - FastAPI sunucusunu ayrı bir komut penceresinde başlatır.
   - Streamlit UI'yi `http://localhost:8501` adresinde açar.

## 🔧 Çevre Değişkenleri (`.env`)
`.env.example` dosyasını `.env` olarak kopyaladıktan sonra aşağıdaki alanları doldurun:
```
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
# İsteğe bağlı
JWT_SECRET=your-secret-key
DATABASE_URL=sqlite:///./lms.db
# FastAPI URL (özellikle farklı bir host/port kullanıyorsanız)
FASTAPI_URL=http://127.0.0.1:8000
```
> **Not:** `FASTAPI_URL` değeri `app.py` içinde varsayılan olarak `http://127.0.0.1:8000`tir. Farklı bir adres kullandığınızda bu satırı güncelleyin.

## 🚀 Uygulamayı Çalıştırma
- **Tek seferlik**: `run_all.bat` yukarıdaki adımları otomatik yapar.
- **Manuel** (isteğe bağlı):
  ```bat
  call venv\Scripts\activate
  uvicorn ai_service:app --reload   # FastAPI (http://127.0.0.1:8000)
  streamlit run app.py               # Streamlit UI (http://localhost:8501)
  ```

## 🧪 Test Etme
1. Tarayıcınızda **http://localhost:8501** adresine gidin.
2. Sol menüden **Kayıt** → bir kullanıcı oluşturun, ardından **Giriş** yapın.
3. **Kurslar**, **İçerik Yükle**, **Metin Analizi**, **İçerik Özeti** sekmelerini deneyin.
   - Metin Analizi: bir paragraf girip *Analiz Et* butonuna basın; sonuç API üzerinden dönecek.
   - İçerik Özeti: uzun bir metin girip *Özetle* butonuna basın; özet gösterilecek.

## 📚 Geliştirme Notları
- **Veritabanı**: `database.py` içinde `init_db()` fonksiyonu, FastAPI başlatıldığında otomatik çalışır.
- **Kimlik Doğrulama**: Şu anda sadece placeholder bir login sistemi var. JWT veya OAuth eklemek isterseniz `models.py` ve `database.py` üzerine genişletebilirsiniz.
- **LLM Sağlayıcıları**: `ai_service.py` OpenAI API'yi kullanıyor; Gemini veya Groq entegrasyonu için `call_openai` fonksiyonunu ilgili SDK'ya göre değiştirmeniz yeterli.

## 🛠️ Sorun Giderme
- **`File does not exist: app.py`** hatası: `streamlit run app.py` komutunu **`lms-yapayzeka-final` klasörünün içinde** çalıştırın. `run_all.bat` bunu otomatik yapar.
- **FastAPI yanıt vermiyor**: `uvicorn` penceresindeki hataları kontrol edin, `.env` dosyasındaki `OPENAI_API_KEY` doğru mu? 
- **Bağımlılık hataları**: `pip install --upgrade pip` ardından `pip install -r requirements.txt`.

---
**Hazır!** Yukarıdaki adımları izleyerek uygulamayı çalıştırabilir ve AI destekli LMS'inizi kullanmaya başlayabilirsiniz. Yardımcı olabileceğim başka bir konu olursa lütfen söyleyin!
