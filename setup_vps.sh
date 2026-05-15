#!/bin/bash
# ============================================================
# setup_vps.sh — John Galt v2 — Auto-deploy setup
# Configura o VPS para receber git pull automático via GitHub Actions
# ============================================================

set -e

REPO_DIR="/root/john-galt-v2"
DEPLOY_SCRIPT="/root/deploy.sh"
GITHUB_REPO="https://github.com/KleberMirandaMariano/john-galt-v2.git"

echo "========================================"
echo "  John Galt v2 — VPS Setup"
echo "========================================"

# 1. Verifica se o repositório já existe
if [ -d "$REPO_DIR/.git" ]; then
  echo "[OK] Repositório já existe em $REPO_DIR"
  cd "$REPO_DIR"
  git pull origin main
else
  echo "[INFO] Clonando repositório..."
  cd /root
  git clone "$GITHUB_REPO" john-galt-v2
  echo "[OK] Repositório clonado em $REPO_DIR"
fi

# 2. Cria o script de deploy que será chamado pelo GitHub Actions
echo "[INFO] Criando script de deploy em $DEPLOY_SCRIPT..."
cat > "$DEPLOY_SCRIPT" << 'DEPLOY_EOF'
#!/bin/bash
# deploy.sh — chamado remotamente pelo GitHub Actions
set -e

REPO_DIR="/root/john-galt-v2"
LOG_FILE="/var/log/john-galt-deploy.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploy iniciado" >> "$LOG_FILE"

cd "$REPO_DIR"
git fetch origin
git reset --hard origin/main
git pull origin main

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploy concluído com sucesso" >> "$LOG_FILE"

# Reinicia serviços se existirem (ajuste conforme necessário)
if command -v docker &> /dev/null && docker ps -q --filter "name=john-galt" | grep -q .; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Reiniciando containers Docker..." >> "$LOG_FILE"
  cd "$REPO_DIR"
  docker compose pull 2>/dev/null || true
  docker compose up -d --remove-orphans 2>/dev/null || true
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Containers reiniciados" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Deploy finalizado ===" >> "$LOG_FILE"
DEPLOY_EOF

chmod +x "$DEPLOY_SCRIPT"
echo "[OK] Script de deploy criado: $DEPLOY_SCRIPT"

# 3. Cria arquivo de log
touch /var/log/john-galt-deploy.log
echo "[OK] Log criado: /var/log/john-galt-deploy.log"

# 4. Verifica que o GitHub Actions workflow existe
if [ -f "$REPO_DIR/.github/workflows/deploy.yml" ]; then
  echo "[OK] GitHub Actions workflow encontrado"
else
  echo "[AVISO] Workflow .github/workflows/deploy.yml não encontrado"
  echo "        Crie o workflow no GitHub para ativar o auto-deploy"
fi

echo ""
echo "========================================"
echo "  Setup concluído com sucesso!"
echo "========================================"
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Acesse: github.com/KleberMirandaMariano/john-galt-v2/settings/secrets/actions"
echo "2. Adicione o Secret: VPS_HOST = 187.77.139.188"
echo "3. Adicione o Secret: VPS_PASSWORD = <sua senha root>"
echo ""
echo "Após isso, todo commit externo fará git pull automático neste servidor."
echo ""
