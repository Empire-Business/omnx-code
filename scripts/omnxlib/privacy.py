"""Best-effort presentation redaction, never a claim that arbitrary data is secret-free."""
from __future__ import annotations
import re
from .core import require, portable_path

SECRET_PATTERNS = (
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?(?:-----END [^-]+PRIVATE KEY-----|$)'),
    re.compile(r'(?i)\b(?:sb_secret_|sk_live_|sk_test_|ghp_|github_pat_)[A-Za-z0-9_-]{8,}'),
    re.compile(r'(?i)(?:authorization\s*[:=]\s*[\"\']?\s*(?:bearer|basic)\s+)[A-Za-z0-9._~+/-]+=*'),
    re.compile(r'(?i)\b(?:[A-Z0-9_]*(?:SECRET|PASSWORD|ACCESS_TOKEN|API_KEY|PRIVATE_KEY|HOTTOK)[A-Z0-9_]*)\b\s*[:=]\s*[\"\']?[^\s\"\',;<]{4,}'),
    re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b'),
)

def redact(text):
    if not isinstance(text, str): return text
    for pattern in SECRET_PATTERNS:
        text = pattern.sub('[REDACTED]', text)
    return text

def public_object(value):
    if isinstance(value, dict): return {k: public_object(v) for k, v in value.items()}
    if isinstance(value, list): return [public_object(v) for v in value]
    return redact(value)

def safe_subject_path(rel):
    portable_path(rel)
    parts = rel.lower().split('/')
    require(not any(p in {'.git', '.ssh', 'node_modules', 'vendor', 'local', 'migrations', 'backup', 'backups'} or p.startswith('.env') for p in parts),
            'protected_subject', 'Este caminho não pode ser exibido como proposta.', 5)
    require(not parts[-1].endswith(('.pem', '.key', '.p12', '.pfx', '.sqlite', '.db')),
            'protected_subject', 'Credenciais e bancos não são propostas de revisão.', 5)
    return rel
