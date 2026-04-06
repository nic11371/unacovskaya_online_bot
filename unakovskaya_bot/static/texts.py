TEXTS = {
    "text_welcome": "Здравствуйте! Очень рада вам.",
    "btn_start": "Старт",
    "text_no_links": "На данный момент материалов нет, загляните позже!",
    "text_removed_link": "✅ Удалено",
    "text_error_removed": "❌ Ошибка удаления",
    "text_restrict_admin": "⛔️ У вас нет прав администратора.",
    "text_admin_panel": "🔧 Панель администратора:",
    "text_welcome_admin": (
        "👨‍💻 Вы опознаны как администратор.\n"
        "Введите /admin для входа в панель управления."
    ),
    "text_admin_article": (
        "Отправьте сообщение (текст, фото, видео, голосовое) для всех.\n\n"
    ),
    "text_start_mailing": "Начинаю рассылку ...",
    "text_finish_mailing": "Рассылка завершена. Успешно отправлено:",
    "text_title_step": "Введите название шага (Title):",
    "text_description_step": "Введите текст описания:",
    "text_link_step": "Введите адрес ссылки:",
    "text_wrong_link": "❌ Ссылка должна начинаться с http. Попробуйте снова.",
    "text_link_added": "✅ Ссылка добавлена! Номер шага:",
    "text_empty_list": "Список пуст",
    "text_get_email": "Получить emails",
    "text_ask_email": (
        "Почти готово 😊 Сначала пришлите, пожалуйста, ваш email "
        "и я сразу отправлю следующую запись."
    ),
    "text_email_saved": "✅ Email получен, Спасибо...",
    "text_email_invalid": "❌ Некорректный email. Попробуйте ещё раз:",
    "text_email_timeout": "⏱ Время ввода email истекло. Продолжаем...",
    "text_btn_email_admin": "Получить емайлы",
    "text_btn_email_step": "⚙️ Шаг запроса email",
    "text_btn_email_text": "✏️ Текст запроса email",
    "text_ask_email_text": "Текущий текст:\n\n{}\n\nВведите новый текст:",
    "text_email_text_saved": "✅ Текст запроса email обновлён.",
    "text_ask_email_step": "Текущий шаг: {}. Введите новый номер шага:",
    "text_email_step_saved": "✅ Шаг запроса email изменён на: {}",
    "text_email_step_invalid": "❌ Введите целое положительное число.",
    "text_empty_list_emails": "Емайлы пусты",
    "text_btn_remove": "Нажмите на пункт, чтобы УДАЛИТЬ его:",
    "text_btn_art": "Написать анонс",
    "text_btn_link": "➕ Добавить ссылку",
    "text_btn_rem": "📋 Список (Удалить)",
    "text_btn_next": "Готово ✅",
    "text_btn_back": "🔙 Назад",
    "text_log_help": "Запускает телеграм-бота в режиме вебхука",
    "text_log_start": "Запуск телеграм-бота...",
    "text_log_variable_err": "Переменная BASE_URL не установлена в файле!",
    "text_log_register": "Регистрация обработчиков...",
    "text_log_webhook_set": "Вебхук установлен на:",
    "text_log_stop_bot": "Остановка бота...",
    "text_log_webhook_rem": "Вебхук удален.",
    "text_log_http": "Запуск на http://",
    "text_log_sentry": "Sentry инициализирован",
    "text_start_vk_bot": "Запуск vk bot",
    "text_log_tg_broadcast":
        "TG broadcast: не удалось поставить задачу в очередь:",
    "text_broadcast_done": (
        "✅ Рассылка завершена.\n"
        "Отправлено: {count}\n"
        "Всего в базе: {total}"
    ),
    "text_broadcast_error": "❌ Ошибка запуска рассылки: {error}",
    "text_emails_caption": "📧 Emails: {count}",
    "text_emails_send_error": "❌ Ошибка при отправке файла: {error}",
    "text_link_format": "{title}\n\n{url}\n\n{message_text}",
    "text_btn_del_link": "🗑 {order}. {title}",
    # log messages
    "log_tg_broadcast_fail_user":
        "TG broadcast: не удалось отправить пользователю %s: %s",
    "log_tg_broadcast_done": "TG broadcast завершён: %d/%d отправлено",
    "log_tg_broadcast_started": "TG broadcast запущен: %d пользователей",
    "log_tg_broadcast_fail_queue":
        "TG broadcast: не удалось поставить задачу в очередь: %s",
    "log_tg_email_request": "TG email request for user %s",
    "log_tg_email_saved": "TG email saved for user %s: %s",
    "log_tg_email_timeout": "TG email timeout for user %s",
    "log_tg_remove_button_fail": "Не удалось убрать кнопку: %s",
    "log_tg_edit_reply_markup_error": "edit_reply_markup error: %s",
    "log_vk_broadcast_fail_user":
        "VK broadcast: не удалось отправить пользователю %s: %s",
    "log_vk_broadcast_done": "VK broadcast завершён: %d/%d отправлено",
    "log_vk_broadcast_started": "VK broadcast запущен: %d пользователей",
    "log_vk_broadcast_fail_queue":
        "VK broadcast: не удалось поставить задачу в очередь: %s",
    "log_vk_broadcast_fail_admin":
        "VK broadcast: не удалось уведомить админа: %s",
    "log_vk_email_request": "VK email request for user %s",
    "log_vk_email_saved": "VK email saved for user %s: %s",
    "log_vk_email_timeout": "VK email timeout for user %s",
    "log_vk_edit_keyboard_error": "VK edit keyboard error: %s",
    "log_vk_start_fail_user_info":
        "VK /start: failed to get user info for %s: %s",
    "log_vk_start_fail_sync": "VK /start: failed to sync user %s: %s",
}
