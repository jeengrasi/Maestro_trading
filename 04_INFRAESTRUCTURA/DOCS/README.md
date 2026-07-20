# Maestro_Trading_AI V1.0 - Paper Trading

Deploy directo desde iPad. 0 terminal.

[[Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/tu-usuario/maestro-trading-ai)

### Variables de Entorno Requeridas

Pégalas en Vercel → Settings → Environment Variables:

| Key | Value |
| --- | --- |
| `ALPACA_API_KEY` | Tu key de Alpaca Paper |
| `ALPACA_SECRET_KEY` | Tu secret de Alpaca |
| `ALPACA_PAPER` | `true` |
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather |
| `TELEGRAM_CHAT_ID` | Tu chat ID de @userinfobot |

### Comandos Telegram

- `/start` - Estado del bot
- `/balance` - Ver saldo Paper 
- `/stop` - Pausa total de emergencia
