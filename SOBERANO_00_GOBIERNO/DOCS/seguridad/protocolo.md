# PROTOCOLO DE SEGURIDAD

**Versión:** 1.0 | **Fecha:** 2026-07-02

---

## REGLAS
- Nunca compartir API Keys en chats.
- Rotar tokens cada 90 días.
- Usar GitHub Secrets para almacenamiento.
- Backup semanal de documentos.

## RIESGOS
| Riesgo | Mitigación |
| :--- | :--- |
| API Key caduca | Rotación automática |
| Vercel no despliega | GitHub Actions como respaldo |
| Redis caído | Backup en GitHub |
