### === BUILDER ===
FROM python:3.10-slim AS builder

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   gcc \
   libpq-dev \
   && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


### === FINAL IMAGE ===
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Chemin vers le vrai dossier de ton app : on cible labo_informatique
WORKDIR /conference-informatique/conference_site

# Copier les dépendances Python compilées
COPY --from=builder /install/deps /usr/local

# Copier le code source entier
COPY . /conference-informatique

EXPOSE 8000

# Lancer directement le serveur Django sans devoir naviguer dans les dossiers

CMD ["sh", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]


