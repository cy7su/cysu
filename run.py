import time
from multiprocessing import Process


def run_website():
    from app import create_app

    app = create_app()
    app.run(host='127.0.0.1', port=8002, debug=False)


def run_telegram_bot():
    import logging

    logging.getLogger("telegram_bot").setLevel(logging.CRITICAL)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("telegram").setLevel(logging.CRITICAL)
    logging.getLogger("telegram.ext").setLevel(logging.CRITICAL)

    from app.utils.telegram_bot import TelegramBotManager

    bot_manager = TelegramBotManager()
    bot_manager.run_bot()


def main():
    website_process = Process(target=run_website)
    bot_process = Process(target=run_telegram_bot)

    try:
        website_process.start()
        time.sleep(1)
        bot_process.start()
        website_process.join()
        bot_process.join()

    except KeyboardInterrupt:
        pass
    finally:
        if website_process.is_alive():
            website_process.terminate()
            website_process.join()

        if bot_process.is_alive():
            bot_process.terminate()
            bot_process.join()


if __name__ == "__main__":
    main()
