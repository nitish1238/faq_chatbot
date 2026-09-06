# FAQ Chatbot (Django)

A small chat app for a made-up online store. A logged-in user types a
question, the page sends it to the server with `fetch`, and the server
replies with an answer. There is no AI — answers come from a database
table, matched by simple keyword overlap.

## Tech used

- Python + Django
- PostgreSQL
- Plain HTML, CSS, JavaScript (no React, no jQuery)

## 1. Setup

### Requirements
- Python 3.10+
- PostgreSQL running locally (or accessible on a host you control)

### Steps

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd faq_chatbot

# 2. Create and activate a virtual environment
python3 -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the Postgres database (adjust user/password as needed)
createdb faq_chatbot
# or, inside psql:
#   CREATE DATABASE faq_chatbot;

# 5. Copy the example env file and fill in real values
cp .env.example .env
```

Open `.env` and set:

```
DJANGO_SECRET_KEY=some-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=faq_chatbot
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
```

Generate a random secret key if you want one:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Migrations, FAQ data, and a superuser

```bash
python manage.py migrate
python manage.py import_faqs data/faqs.csv
python manage.py createsuperuser
```

### Run it

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. You'll be redirected to `/login/` if
you're not logged in — register a new account or use the superuser you
just created.

### Run the tests

```bash
python manage.py test
```

There are 3 tests:
1. A message matching a FAQ returns the correct answer.
2. A message matching nothing returns the fallback message.
3. User A cannot open User B's conversation (returns 404).

## 2. Test login

A test account is included so you don't have to register one yourself:

- **Username:** `testuser`
- **Password:** `testpass123`

(Create it locally with `python manage.py shell` and
`User.objects.create_user('testuser', password='testpass123')`, or just
register a fresh account on `/register/` — either works.)

## 3. How the keyword matching works

All of the matching logic lives in `chatbot/services/matcher.py`, kept
out of the view on purpose so it's easy to test and read on its own.

1. The user's message is lowercased and stripped of punctuation
   (`"What's your Return policy?"` → `"whats your return policy"`).
2. It's split into a set of words.
3. Every **active** `FAQ` row has a `keywords` field — a comma-separated
   list like `"refund,return,return policy"`. Each keyword (which can be
   one word or a short phrase) is checked against the message's words.
4. Whichever FAQ scores the most keyword matches wins and its `answer`
   is sent back.
5. If no FAQ scores at least 1 point, the fixed fallback is sent:
   > Sorry, I could not find an answer. Please contact customer support.

This is intentionally simple — no AI, no external APIs, no fuzzy
matching library. It's just set intersection.

## 4. Project layout

```
faq_chatbot/
├── faq_chatbot/          # Django project settings, root urls
├── chatbot/
│   ├── models.py         # FAQ, Conversation, Message (UUID primary keys)
│   ├── views.py          # accounts + chat page + the 4 API endpoints
│   ├── urls.py
│   ├── services/
│   │   └── matcher.py    # keyword matching logic (see above)
│   ├── management/commands/import_faqs.py
│   ├── templates/chatbot/
│   ├── static/chatbot/{css,js}
│   └── tests.py
├── data/faqs.csv         # 20 FAQ rows across 4 categories
├── requirements.txt
├── .env.example
└── manage.py
```

## 5. API endpoints

| Method | URL                                          | Purpose                |
|--------|-----------------------------------------------|-------------------------|
| GET    | `/api/conversations/`                        | List my chats           |
| POST   | `/api/conversations/`                        | Create a new chat        |
| GET    | `/api/conversations/<uuid>/`                 | Open one chat + messages |
| POST   | `/api/conversations/<uuid>/messages/`        | Send a message           |

All of these require login and only ever operate on the logged-in
user's own conversations — trying to open someone else's conversation
returns a 404, not a 403, so a bad ID and someone else's ID look the
same from the outside.

## 6. What I did not finish

- The optional order-status feature ("where is my order ORD-1001") is
  not implemented.
- Deleting a conversation is not implemented.
- Not deployed anywhere — this README covers running it locally.

## 7. Notes on security basics covered

- CSRF protection is left on everywhere; the frontend reads the token
  from Django's `{% csrf_token %}` tag and sends it as the
  `X-CSRFToken` header on every `fetch` POST.
- All validation (empty message, 500-character limit, ownership checks)
  happens on the server, not just in JavaScript.
- `SECRET_KEY` and the database password are read from `.env`, which is
  git-ignored. Only `.env.example` (names, no real values) is committed.
