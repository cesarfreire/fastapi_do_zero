# FastAPI 2025

## Alembic e SQLAlchemy

### Migrations

Executa migration:

```bash
alembic upgrade head
```

Desfazer última migration:

```bash
alembic downgrade -1
```

### Sessões

```python
engine = create_engine(Settings().DATABASE_URL)

session = Session(engine)

session.add(obj)       # Adiciona no banco
session.delete(obj)    # Remove do banco
session.refresh(obj)   # Atualiza objeto com a sessão

session.scalars(query) # Lista N objetos
session.scalar(query)  # Lista 1 objeto

session.commit()       # Executa as UTs no banco
session.rollback()     # Desfaz as UTs
```
