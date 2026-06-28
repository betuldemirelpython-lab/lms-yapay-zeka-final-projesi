@echo off
setlocal

rem -------------------------------------------------
rem 0. Çakışan Portları Temizle (FastAPI: 8000, Streamlit: 8501)
rem -------------------------------------------------
echo Mevcut portlar kontrol ediliyor ve temizleniyor...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Port 8000 kullanan PID %%a sonlandiriliyor...
    taskkill /F /PID %%a
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
    echo Port 8501 kullanan PID %%a sonlandiriliyor...
    taskkill /F /PID %%a
)

rem -------------------------------------------------
rem 1. Sanal ortamı oluştur ve aktive et
rem -------------------------------------------------
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

rem -------------------------------------------------
rem 2. Bağımlılıkları kur
rem -------------------------------------------------
pip install -r requirements.txt

rem -------------------------------------------------
rem 3. .env dosyasını oluştur (örnek .env zaten var)
rem -------------------------------------------------
if not exist .env (
    copy .env.example .env
)

rem -------------------------------------------------
rem 4. FastAPI (AI Servisi) başlat
rem -------------------------------------------------
start "" cmd /c "uvicorn ai_service:app --reload"

rem -------------------------------------------------
rem 5. Streamlit UI'yi başlat
rem -------------------------------------------------
streamlit run app.py
