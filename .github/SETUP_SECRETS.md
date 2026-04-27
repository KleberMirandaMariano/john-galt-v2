# 🔐 Configurar GitHub Secrets para Auto-Deploy

Para o GitHub Actions funcionar, você precisa configurar 3 secrets:

## 1️⃣ VPS_SSH_KEY (Chave Privada SSH)

```bash
# No VPS, exibir a chave privada:
cat ~/.ssh/id_ed25519

# Copiar TODO o conteúdo (incluindo -----BEGIN e -----END)
```

**No GitHub:**
1. Ir em: https://github.com/KleberMirandaMariano/john-galt-v2/settings/secrets/actions
2. Clicar "New repository secret"
3. Name: `VPS_SSH_KEY`
4. Value: (colar a chave privada completa)
5. Add secret

---

## 2️⃣ VPS_HOST (IP ou hostname do VPS)

**Valor:** `srv1514218.hstgr.cloud` ou `187.77.139.188`

**No GitHub:**
1. New repository secret
2. Name: `VPS_HOST`
3. Value: `srv1514218.hstgr.cloud`
4. Add secret

---

## 3️⃣ VPS_USER (Usuário SSH)

**Valor:** `root`

**No GitHub:**
1. New repository secret
2. Name: `VPS_USER`
3. Value: `root`
4. Add secret

---

## ✅ Testar o Deploy

Depois de configurar os 3 secrets:

1. Fazer qualquer mudança no código
2. `git add .`
3. `git commit -m "test: CI/CD"`
4. `git push origin main`

O GitHub Actions vai:
- ✅ Conectar na VPS via SSH
- ✅ Clonar/atualizar código
- ✅ Copiar configs (SOUL.md, scripts, skills)
- ✅ Reiniciar ZeroClaw
- ✅ Verificar status

**Ver logs:** https://github.com/KleberMirandaMariano/john-galt-v2/actions

---

## 🔒 Segurança

- ✅ Chave SSH fica criptografada no GitHub
- ✅ Só você tem acesso aos secrets
- ✅ Deploy só roda na branch `main`
- ✅ Pode rodar manualmente via "Actions" tab

