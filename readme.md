# 🎮 Trivex — Ігровий Маркетплейс

**Trivex** — це функціональна платформа для торгівлі ігровими послугами, предметами та акаунтами. Проєкт створений для забезпечення безпечного зв'язку між продавцями та покупцями, поєднуючи надійність Django зі швидкістю real-time технологій.

---

## 🛠 Технологічний стек

Для розробки ми обрали сучасний стек, що дозволяє масштабувати проєкт:

- **Backend**: ![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white) + ![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)
- **Database**: ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
- **Real‑time & Cache**: ![Redis](https://img.shields.io/badge/Redis-7.2-red?logo=redis)
- **Asynchronous**: Django Channels
- **Frontend**: ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript) (Axios / WebSockets)
- **Version Control**: ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white) (GitHub)

---

## 🏗 Як працює проєкт (Логіка та безпека)

### 🔐 Безпека та Аутентифікація
Ми впровадили систему захисту банківського рівня для реєстрації:

- **Hashed Codes**: При реєстрації генерується код підтвердження. Він хешується (як пароль) і зберігається в кеші Django. Це гарантує, що навіть при витоку даних з кешу, код неможливо прочитати.
- **Rate Limiting**: Захист від брутфорсу — після 5 невдалих спроб входу IP та Email блокуються на 5 хвилин.

### 🛒 Торгове ядро та Кошик
- **Hybrid Cart**: Якщо користувач не авторизований, товари зберігаються в Cookies. Після входу в акаунт функція `merge_cart_from_cookies` автоматично переносить їх у базу даних до профілю користувача.
- **Оптимізація**: Використання `.select_related()` для мінімізації запитів до БД.

### 💬 Real-time Чат (Redis + PostgreSQL)
Найцікавіша частина проєкту — живий чат між покупцем та продавцем. Ось як він працює технічно:

1. **Надсилання**: Користувач пише повідомлення ➔ воно летить через WebSocket до сервера.
2. **Збереження**: Django Channels спочатку записує повідомлення в PostgreSQL. Це гарантує надійність та збереження історії листування.
3. **Розсилка (Redis)**: Після запису в БД, сигнал передається в Redis (Channel Layer). Redis знає, хто зараз онлайн у цій "кімнаті" чату, і миттєво пересилає повідомлення іншому учаснику.
4. **Результат**: Повідомлення з'являється у співрозмовника за мілісекунди без перезавантаження сторінки.

---

## 📦 Керування залежностями (UV)

Для прискорення встановлення пакетів та ізоляції середовища ми використовуємо **UV** — сучасну заміну `pip` + `virtualenv`.

### Як встановити залежності з UV:
```bash
# Встановлення UV (якщо ще не встановлено)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Створення віртуального оточення та встановлення пакетів
uv venv
uv pip install -r requirements.txt

---

```
```
📂 Структура проєкту
Trivex/
├── .venv/                      
├── backend/                     
│   ├── authentication/          
│   │   ├── migrations/
│   │   ├── services/
│   │   │   ├── email_service.py
│   │   │   └── verification_service.py
│   │   ├── templates/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── mail_handler.py
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── chat/                     
│   │   ├── migrations/
│   │   ├── templates/chat/
│   │   │   ├── chat_list.html
│   │   │   └── chat_room.html
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── consumers.py          
│   │   ├── models.py
│   │   ├── routing.py            
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── core/                      
│   │   ├── asgi.py
│   │   ├── routers.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── games/                      
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── templatetags/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── media/                       
│   │   ├── avatars/
│   │   └── games/
│   │
│   ├── static/                      
│   └── templates/                    
│
├── .env                              
├── .gitignore
├── manage.py                         
└── requirements.txt    
```


### 👨‍💻 Командна розробка через Git
Ми з другом працюємо над проєктом спільно, використовуючи професійний підхід до Git:

- **Гілки (Branches)**: Кожна фіча (чат, кошик, профілі) створюється в окремій гілці. Це дозволяє нам не заважати один одному та безпечно тестувати код.
- **Pull Requests**: Перед злиттям коду в основну гілку (`main`), ми обмінюємося інформацією та перевіряємо зміни, щоб уникнути конфліктів у базі даних.

---

## 📈 Особисті досягнення (Features)

- **Custom Logging**: Впроваджено логер `user_actions`, який фіксує всі важливі дії на сайті (реєстрація, створення оголошень, видалення).
- **No-Refresh UX**: Завдяки AJAX та WebSockets, користувач отримує динамічний інтерфейс без зайвих перезавантажень сторінок.
- **Clean Code**: Чіткий поділ на сервіси та моделі для легкого масштабування проєкту в майбутньому.

---

## 👥 Розробники

- **Danil Pavlov** — (https://github.com/Danya-creator-coder)
- **Artem Zalutskij** — (https://github.com/Art112-122)

---