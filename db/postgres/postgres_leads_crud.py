from db.postgres.postgres_connection import PostgresConnection
from db.postgres.postgres_person_crud import PostgresPersonCrud
from repositories.db_crud import DBCrud


class PostgresLeadsCrud(DBCrud):
    def __init__(self, db_connection: PostgresConnection, person_crud: PostgresPersonCrud):
        self.db_connection = db_connection
        self.person_crud = person_crud

    def find_all_and_compare(self, sellers):
        historical_leads = []

        seller_ids = [seller['id'] for seller in sellers]

        seller_ids_names = {seller['id']: seller['name'] for seller in sellers}

        placeholders = ', '.join(['%s'] * len(seller_ids))
        query = f"SELECT * FROM meta_leads WHERE ml_vendedor_id IN ({placeholders});"

        self.db_connection.cursor.execute(query, seller_ids)
        rows = self.db_connection.cursor.fetchall()

        column_names = [column[0] for column in self.db_connection.cursor.description]
        object_rows = []

        for item in rows:
            object_rows.append(dict(zip(column_names, item)))

        for row in object_rows:
            historical_leads.append({
                'seller_id': row['ml_vendedor_id'],
                'seller_name': seller_ids_names[row['ml_vendedor_id']],
                'form': row['ml_formulario'],
                'dni': row['ml_dni_persona']
            })

        return historical_leads

    def create(self, new_leads_to_db):
        try:
            for index, row in new_leads_to_db.iterrows():
                person_id = self.person_crud.create(row)
                if person_id:
                    self.db_connection.cursor.execute("""
                        INSERT INTO meta_leads (
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
                            ml_vendedor_id,
                            per_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['Red social'],
                        row['Formulario'],
                        row['Diplomado'],
                        row['Nombres'],
                        row['Ciudad'],
                        row['DNI'],
                        row['Enfermero'],
                        row['Grado'],
                        row['Celular'],
                        row['Correo'],
                        row['Fecha de registro'],
                        row['Fecha de descarga'],
                        row['Vendedor_ID'],
                        person_id
                    ))

            self.db_connection.connection.commit()
            print('Registros insertados correctamente.')

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f'Error al insertar leads: {str(e)}')
