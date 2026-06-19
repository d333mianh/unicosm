"""Telegram front-end — daily push + read another person's day from a chat.

A thin, optional, online surface over the offline engine. The only place that
touches the network is `api.TelegramClient`; everything else (`parse`, `format`,
`bot.reply_for`) is pure and unit-tested. Mirrors how `notify` / `synthesis.llm`
keep the online edge isolated from the deterministic core.

Env:
  UNICOSM_TELEGRAM_TOKEN   bot token from @BotFather (or TELEGRAM_BOT_TOKEN)
  UNICOSM_TELEGRAM_CHAT_ID default chat for `telegram send`
  UNICOSM_TELEGRAM_ALLOW   comma-separated chat ids the bot will answer (optional)
"""
