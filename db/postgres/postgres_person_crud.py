from db.postgres.postgres_connection import PostgresConnection
from repositories.db_crud import DBCrud
from datetime import datetime


class PostgresPersonCrud(DBCrud):
    def __init__(self, db_connection: PostgresConnection):
        self.db_connection = db_connection

    def create(self, person):
        try:
            self.db_connection.cursor.execute("""
                INSERT INTO tbl_persona (
                    tdo_id,
                    per_numero_documento,
                    per_nombres,
                    per_apellido_paterno,
                    per_apellido_materno,
                    gen_id,
                    per_telefono,
                    per_correo,
                    per_direccion,
                    escv_id,
                    pscg_id,
                    aud_fecha_creacion,
                    aud_fecha_modificacion
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (per_numero_documento) DO NOTHING
                RETURNING per_id;
            """, (
                1,
                person['DNI'],
                person['Nombre'],
                person['Apellido paterno'],
                person['Apellido materno'],
                None,
                person['Celular'],
                person['Correo'],
                '',
                None,
                7,
                datetime.now(),
                datetime.now()
            ))

            person_id = self.db_connection.cursor.fetchone()

            if person_id:
                person_id = person_id[0]
            else:
                self.db_connection.cursor.execute("""
                    SELECT per_id 
                    FROM tbl_persona 
                    WHERE per_numero_documento = %s
                """, (person['DNI'],))

                result = self.db_connection.cursor.fetchone()
                person_id = result[0] if result else None

            return person_id

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f'Error al insertar o buscar persona: {str(e)}')
            return None
