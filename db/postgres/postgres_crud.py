from db.postgres.postgres_connection import PostgresConnection
from repositories.db_crud import DBCrud


class PostgresCrud(DBCrud):
    def __init__(self, db_connection: PostgresConnection):
        self.db_connection = db_connection

    def find_all_and_compare(self, sellers):
        historical_leads = []

        seller_ids = [seller['id'] for seller in sellers]

        seller_ids_names = {seller['id']: seller['name'] for seller in sellers}

        # Crear una consulta SQL usando la cláusula IN
        placeholders = ', '.join(['%s'] * len(seller_ids))
        query = f"SELECT * FROM meta_leads WHERE ml_vendedor_id IN ({placeholders});"

        # Ejecutar la consulta una sola vez
        self.db_connection.cursor.execute(query, seller_ids)
        rows = self.db_connection.cursor.fetchall()

        column_names = [column[0] for column in self.db_connection.cursor.description]
        object_rows = []

        for item in rows:
            object_rows.append(dict(zip(column_names, item)))

        # Recorrer las filas resultantes en un solo bucle
        for row in object_rows:
            historical_leads.append({
                'seller_id': row['ml_vendedor_id'],
                'seller_name': seller_ids_names[row['ml_vendedor_id']],
                'form': row['ml_formulario'],
                'dni': row['ml_dni_persona']
            })

        return historical_leads

    def create(self, new_leads_to_db):
        for index, row in new_leads_to_db.iterrows():
            self.db_connection.cursor.execute("""INSERT INTO meta_leads (
            ml_red_social,
            ml_formulario,
            ml_diplomado,
            ml_nombre_persona,
            ml_ciudad_persona,
            ml_dni_persona,
            ml_es_enfermero_persona,
            ml_nivel_estudios_persona,
            ml_telefono_persona,
            ml_correo_persona,
            ml_fecha_registro,
            ml_fecha_descarga,
            ml_vendedor_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['Red social'],
                  row['Formulario'],
                  None,
                  row['Nombre completo'],
                  row['Ciudad'],
                  row['DNI'],
                  row['Enfermero'],
                  row['Grado'],
                  row['Celular'],
                  row['Correo'],
                  row['Fecha de registro'],
                  row['Fecha de descarga'],
                  row['Vendedor_ID']))

        self.db_connection.connection.commit()

        print('Registros insertados correctamente.')
