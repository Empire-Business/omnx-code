# 🚫 Regras de Git (INEGOCIÁVEIS)

```
# .gitignore OBRIGATÓRIO — a IA deve criar/verificar no início do projeto:
.env
.env.local
.env.*.local
*.env
```

> ❌ **É PROIBIDO fazer commit do `.env` ou qualquer arquivo com credenciais.**
> Se a IA detectar que o `.env` está sendo commitado (ou não está no `.gitignore`), deve parar tudo e corrigir antes de continuar.
