from sqlalchemy import MetaData
from sqlalchemy.sql.ddl import CreateTable
from app import db, app as flask_app


with flask_app.app_context():
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    with open('schema.sql', 'w', encoding='utf-8') as f:
        for table in metadata.sorted_tables:
            create_table = str(CreateTable(table)).strip() + ';\n\n'
            f.write(create_table)
