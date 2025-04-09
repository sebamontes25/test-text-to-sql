### install dependencies
```bash
poetry install
```

### build the DB and pgAdmin
```bash
docker compose up -d  
```

### Seed the DB
```bash
python src/seed_db.py
```

### Run the agent
```bash
python src/main.py --question "what you want to search in the DB"
```





