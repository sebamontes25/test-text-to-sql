### install poetry for environment
```bash
pip install poetry
```

### install dependencies
```bash
poetry install
```

### build the DB and pgAdmin hay que tener instalado docker y docker compose
```bash
docker compose up -d  
```

### Seed the DB with random data (definido en src/models.py)
```bash
poetry run python src/seed_db.py
```

### Run the agent con una pregunta por consola
```bash
poetry run python src/main.py --question "what you want to search in the DB"
```

### Run the agent con streamlit (es una aplicación web)
```bash
poetry run streamlit run src/app.py"
```

### en caso de querer correr la API 
```bash
poetry run python src/api_call_app.py"
```


