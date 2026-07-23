# 🔄 Deploy — Fluxo Automático, Vercel + Cloudflare e Checklist

## Fluxo de Deploy Automático

```
Você salva o código
       ↓
GitHub recebe a atualização
       ↓
Vercel detecta automaticamente
       ↓
Vercel compila e publica (~1-2 min)
       ↓
Site atualizado no ar ✅
```

- Branch `main` → Deploy em **produção** (site real)
- Outras branches → Deploy em **preview** (URL temporária para testes)

## Configuração Vercel + Cloudflare

**Passos para conectar domínio:**
1. Em **Settings → Domains** no Vercel, adicionar o domínio e copiar o CNAME
2. No painel DNS do Cloudflare, adicionar o CNAME do Vercel com proxy ativo (ícone laranja)
3. Em **SSL/TLS** no Cloudflare, selecionar modo **Full (Strict)**

**Configurações de segurança obrigatórias no Cloudflare:**

| Configuração          | Onde ativar                    | Por que fazer                                      |
|-----------------------|--------------------------------|----------------------------------------------------|
| WAF (Firewall)        | Security → WAF                 | Bloqueia automaticamente ataques conhecidos        |
| Bot Fight Mode        | Security → Bots                | Identifica e bloqueia bots maliciosos              |
| Rate Limiting         | Security → WAF → Rate Limiting | Limita acessos por IP por minuto                   |
| HTTPS Always          | SSL/TLS → Edge Certificates    | Redireciona HTTP para HTTPS                        |
| HSTS                  | SSL/TLS → Edge Certificates    | Força HTTPS permanentemente                        |
| Min TLS Version: 1.2  | SSL/TLS → Edge Certificates    | Bloqueia protocolos antigos e inseguros            |
| Turnstile (captcha)   | Turnstile                      | Proteção anti-bot nas páginas de login/signup      |

> 💡 **O que é o WAF?** Imagine um segurança na porta de uma festa com uma lista de "tipos suspeitos" — o WAF faz isso digitalmente, bloqueando padrões de ataque antes mesmo de chegarem ao seu site.

## Checklist de Deploy (Vercel)

- [ ] Conta Vercel criada e conectada ao GitHub?
- [ ] Todas as variáveis de ambiente adicionadas no painel do Vercel?
- [ ] `vercel.json` criado com todos os headers de segurança?
- [ ] HTTPS ativo (cadeado verde no navegador)?
- [ ] Preview Deployments protegidos por senha ou login?
- [ ] Domínio personalizado configurado (se aplicável)?
- [ ] Cloudflare configurado na frente do Vercel?
- [ ] WAF e Bot Fight Mode ativos no Cloudflare?
- [ ] Rate Limiting configurado no Cloudflare?
- [ ] Vercel Analytics ativo?
- [ ] **Sistema de tickets de erro ativo em produção (botão de reportar + captura automática + fila) e `docs/SISTEMA-DE-TICKETS.md` atualizado?** ✅ OBRIGATÓRIO
- [ ] **Skill `/security-auditor` executada antes do deploy?** ✅ OBRIGATÓRIO
- [ ] A IA explicou ao usuário como verificar cada item no painel?
