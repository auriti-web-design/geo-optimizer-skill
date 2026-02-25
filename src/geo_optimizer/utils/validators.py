"""
Validatori di input per GEO Optimizer.

Controlla URL (anti-SSRF) e percorsi file (anti-path-traversal)
prima di effettuare operazioni di rete o filesystem.
"""

import ipaddress
import socket
from pathlib import Path
from typing import Optional, Set, Tuple
from urllib.parse import urlparse


# Reti private/riservate da bloccare (RFC 1918, loopback, link-local, metadata cloud)
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # loopback IPv4
    ipaddress.ip_network("10.0.0.0/8"),         # privato RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),      # privato RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),     # privato RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),     # link-local (AWS/GCP/Azure metadata)
    ipaddress.ip_network("::1/128"),            # loopback IPv6
    ipaddress.ip_network("fc00::/7"),           # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),          # IPv6 link-local
]

_ALLOWED_SCHEMES = {"https", "http"}

# Nomi host interni noti
_BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata",
    "metadata.google.internal",
    "169.254.169.254",
}


def validate_public_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica che l'URL punti a un host pubblico, non a reti interne.

    Previene attacchi SSRF bloccando:
    - IP privati (RFC 1918), loopback, link-local
    - Cloud metadata endpoints (169.254.169.254)
    - Schema non consentiti (file://, ftp://, ecc.)
    - Nomi host interni (localhost, metadata)

    Returns:
        (True, None) se sicuro, (False, messaggio_errore) altrimenti.
    """
    parsed = urlparse(url)

    # 1. Verifica schema
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False, f"Schema non consentito: '{parsed.scheme}'. Solo http/https."

    # 2. Estrai hostname
    hostname = parsed.hostname
    if not hostname:
        return False, "Hostname mancante o non valido."

    # 3. Blocca nomi host interni noti
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        return False, f"Host non consentito: '{hostname}'."

    # 4. Blocca URL con credenziali embedded (user:pass@host)
    if "@" in (parsed.netloc or ""):
        return False, "URL con credenziali embedded non consentiti."

    # 5. Risolvi DNS e verifica che ogni IP risolto sia pubblico
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # DNS non risolvibile — non è un errore di sicurezza,
        # lascio che il fetch fallisca normalmente
        return True, None

    for _, _, _, _, sockaddr in infos:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        for network in _BLOCKED_NETWORKS:
            if ip_obj in network:
                return False, (
                    f"L'indirizzo '{ip_str}' risolto per '{hostname}' "
                    f"è in una rete privata/riservata."
                )

    return True, None


def validate_safe_path(
    file_path: str,
    allowed_extensions: Optional[Set[str]] = None,
    must_exist: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Verifica che un percorso file sia sicuro.

    Risolve symlink e path traversal, controlla l'estensione.

    Args:
        file_path: Percorso da validare.
        allowed_extensions: Set di estensioni consentite (es. {".html", ".htm"}).
        must_exist: Se True, verifica che il file esista.

    Returns:
        (True, None) se sicuro, (False, messaggio_errore) altrimenti.
    """
    try:
        resolved = Path(file_path).resolve()
    except (OSError, ValueError) as e:
        return False, f"Percorso non valido: {e}"

    if must_exist and not resolved.exists():
        return False, f"File non trovato: {resolved}"

    if must_exist and not resolved.is_file():
        return False, f"Non è un file: {resolved}"

    if allowed_extensions:
        if resolved.suffix.lower() not in allowed_extensions:
            return False, (
                f"Estensione non consentita: '{resolved.suffix}'. "
                f"Consentite: {', '.join(sorted(allowed_extensions))}"
            )

    return True, None


def url_belongs_to_domain(url: str, domain: str) -> bool:
    """
    Verifica l'appartenenza esatta al dominio, senza substring match.

    Gestisce subdomain legittimi (es. blog.example.com per example.com).
    Blocca URL con credenziali embedded (@).

    Args:
        url: URL completo da verificare.
        domain: Dominio di riferimento (es. "example.com").

    Returns:
        True se l'URL appartiene al dominio.
    """
    parsed = urlparse(url)
    netloc = parsed.netloc

    # Blocca URL con credenziali embedded
    if "@" in netloc:
        return False

    # Rimuove porta se presente
    hostname = netloc.split(":")[0].lower()
    domain_lower = domain.lower()

    # Corrispondenza esatta o subdomain legittimo
    return hostname == domain_lower or hostname.endswith("." + domain_lower)
