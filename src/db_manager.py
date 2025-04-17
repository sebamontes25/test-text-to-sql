from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        self.inspector = inspect(self.engine)
        self.schema = None

    def get_schema(self) -> str:
        if self.schema is not None:
            return self.schema

        schema = []
        for table_name in self.inspector.get_table_names():
            schema.append(f"Table: {table_name}")
            columns = self.inspector.get_columns(table_name)
            for column in columns:
                col_str = f"  Column: {column['name']} {column['type']}"
                schema.append(col_str)
            self.schema = "\n".join(schema)
        return self.schema

    def raw_query_invoke(self, query_string: str) -> pd.DataFrame:
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query_string))
                rows = result.mappings().all()
            return pd.DataFrame(rows)
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
