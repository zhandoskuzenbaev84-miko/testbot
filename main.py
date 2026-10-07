"""
DTM Repetitor Agent asosiy ishga tushirish fayli (Main entrypoint).
Foydalanish:
  python main.py --cli    (Interaktiv terminal rejimini ishga tushirish)
  python main.py --bot    (Telegram botni ishga tushirish)
  python main.py --eval   (TZ-04 9-bo'lim eval testlarini ishga tushirish)
  python main.py --seed   (Bazani 300+ savol bilan qayta to'ldirish)
"""
import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import TELEGRAM_BOT_TOKEN
from core.database import db

def main():
    parser = argparse.ArgumentParser(description="DTM Repetitor-Agent tizimi")
    parser.add_argument("--cli", action="store_true", help="Interaktiv CLI rejimida ishga tushirish")
    parser.add_argument("--bot", action="store_true", help="Telegram botni ishga tushirish")
    parser.add_argument("--eval", action="store_true", help="Eval baholash testlarini ishga tushirish")
    parser.add_argument("--seed", action="store_true", help="Savollar bazasini to'ldirish")

    args = parser.parse_args()

    # Baza savollar sonini tekshirish
    q_count = db.count_questions()
    if q_count < 300 and not args.eval:
        from core.seed_data import seed_database
        print(f"Savollar bazasida {q_count} ta savol mavjud. 300 ta savol yuklanmoqda...")
        seed_database()

    if args.eval:
        import eval
        eval.run_eval_suite()
    elif args.bot:
        import asyncio
        from bot.bot import start_bot
        asyncio.run(start_bot())
    elif args.cli:
        from cli import run_cli
        run_cli()
    else:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "your_telegram_bot_token_here":
            print("Telegram bot tokenni aniqlandi. Bot ishga tushirilmoqda...")
            import asyncio
            from bot.bot import start_bot
            asyncio.run(start_bot())
        else:
            print("Telegram bot token aniqlanmadi. CLI rejim ishga tushirilmoqda...")
            from cli import run_cli
            run_cli()

if __name__ == "__main__":
    main()
