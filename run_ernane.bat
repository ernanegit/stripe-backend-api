@echo off
REM run_ernane.bat - Script personalizado para Ernane

echo 🚀 Iniciando Stripe Sandbox para Ernane...

REM Caminho específico do ngrok do Ernane
set "NGROK_PATH=C:\Users\ernane\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe"

REM Verifica se ngrok existe no caminho
if not exist "%NGROK_PATH%" (
    echo ❌ ngrok não encontrado em: %NGROK_PATH%
    echo Verifique se o arquivo existe neste local
    pause
    exit /b 1
)

echo ✅ ngrok encontrado: %NGROK_PATH%

REM Verifica se o .env existe
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado!
    echo Criando arquivo .env de exemplo...
    (
    echo DEBUG=True
    echo SECRET_KEY=django-insecure-mude-esta-chave-para-producao-ernane
    echo.
    echo # Stripe Test Keys ^(obtenha em https://dashboard.stripe.com/test/apikeys^)
    echo STRIPE_PUBLISHABLE_KEY=pk_test_51...
    echo STRIPE_SECRET_KEY=sk_test_51...
    echo STRIPE_WEBHOOK_SECRET=whsec_...
    ) > .env
    echo 📝 Configure suas chaves do Stripe no arquivo .env
    echo.
)

REM Ativa virtual environment se existir
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Ativando virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment ativado
) else (
    echo ⚠️  Virtual environment não encontrado!
    echo Criando virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment criado e ativado
)

REM Verifica se Django está instalado
python -c "import django" 2>nul || (
    echo 📦 Instalando Django e dependências...
    pip install django stripe python-decouple
)

REM Verifica se as migrações precisam ser executadas
python manage.py migrate --check 2>nul || (
    echo 📊 Executando migrações...
    python manage.py migrate
)

REM Inicia servidor Django
echo 🌐 Iniciando servidor Django em http://127.0.0.1:8000...
start /B "Django Server" cmd /c "python manage.py runserver 127.0.0.1:8000"

REM Aguarda servidor iniciar
echo ⏳ Aguardando servidor iniciar...
timeout /t 5 /nobreak >nul

REM Testa se servidor está respondendo
curl -s http://127.0.0.1:8000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Aguardando mais um pouco...
    timeout /t 3 /nobreak >nul
)

REM Inicia ngrok
echo 🌍 Iniciando ngrok tunnel...
start /B "ngrok Tunnel" cmd /c ""%NGROK_PATH%" http 8000"

REM Aguarda ngrok iniciar
echo ⏳ Aguardando ngrok iniciar...
timeout /t 8 /nobreak >nul

REM Exibe informações
echo.
echo 🎉 Ambiente Stripe Sandbox PRONTO!
echo.
echo 📱 APLICAÇÃO LOCAL:
echo    http://127.0.0.1:8000
echo.
echo 🔐 ADMIN DJANGO:
echo    http://127.0.0.1:8000/admin/
echo.
echo 📊 NGROK DASHBOARD:
echo    http://localhost:4040
echo.
echo 📋 CONFIGURAÇÃO WEBHOOK:
echo 1. Acesse: http://localhost:4040
echo 2. Copie a URL pública ^(https://xxxxx.ngrok.io^)
echo 3. Vá para: https://dashboard.stripe.com/test/webhooks
echo 4. Clique "Add endpoint"
echo 5. URL: [sua-url-ngrok]/webhook/stripe/
echo 6. Eventos: payment_intent.succeeded, payment_intent.payment_failed
echo 7. Copie o "Signing secret" para o .env
echo.
echo 🧪 CARTÕES DE TESTE:
echo ✅ Sucesso: 4242 4242 4242 4242
echo ❌ Falha:   4000 0000 0000 0002  
echo 🔐 3D Sec:  4000 0000 0000 3220
echo    CVC: 123, Data: 12/25
echo.

REM Abre navegadores automaticamente
echo 🌐 Abrindo navegadores...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000
timeout /t 1 /nobreak >nul
start http://localhost:4040

echo.
echo ⚠️  Para parar os serviços: Pressione Ctrl+C
echo 💡 Mantenha esta janela aberta enquanto testa
echo.

REM Loop para manter script rodando
:wait_loop
timeout /t 30 /nobreak >nul
echo 🔄 Serviços rodando... ^(Django + ngrok^)
goto wait_loop