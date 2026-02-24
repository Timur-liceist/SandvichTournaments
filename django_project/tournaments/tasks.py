import time


def send_tournament_notification(tournament_id, user_email):
    """
    Пример задачи: отправка уведомления
    """
    print(f"Начинаем обработку турнира {tournament_id} для {user_email}")
    time.sleep(5)  # Имитация долгой работы (генерация графика, запрос к API)
    print(f"Уведомление для турнира {tournament_id} отправлено!")
    return "Success"
