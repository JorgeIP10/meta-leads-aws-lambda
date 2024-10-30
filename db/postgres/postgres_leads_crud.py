from db.postgres.postgres_connection import PostgresConnection
from db.postgres.postgres_person_crud import PostgresPersonCrud
from repositories.db_crud import DBCrud


class PostgresLeadsCrud(DBCrud):
    def __init__(self, db_connection: PostgresConnection, person_crud: PostgresPersonCrud):
        self.db_connection = db_connection
        self.person_crud = person_crud

    def find_all_and_compare(self, campaigns_seller_leads_object_list):
        historical_sellers_repartition = []
        seller_ids_campaigns_list = []
        seller_ids_names = {}

        for seller_campaign in campaigns_seller_leads_object_list:
            seller_ids = []
            for seller in seller_campaign['sellers_data_structure'].get_sellers_list():
                if seller['id'] not in seller_ids:
                    seller_ids.append(seller['id'])

                if seller['id'] not in seller_ids_names:
                    seller_ids_names[seller['id']] = seller['name']

            seller_ids_campaigns_list.append({
                'campaign': seller_campaign['campaign'],
                'sellers_ids': seller_ids
            })

        object_rows_list = []

        for seller_ids_campaign in seller_ids_campaigns_list:
            if not seller_ids_campaign['sellers_ids']:
                continue

            placeholders = ', '.join(['%s'] * len(seller_ids_campaign['sellers_ids']))
            query = f"SELECT * FROM meta_leads WHERE ml_vendedor_id IN ({placeholders});"
            self.db_connection.cursor.execute(query, seller_ids_campaign['sellers_ids'])
            rows = self.db_connection.cursor.fetchall()

            column_names = [column[0] for column in self.db_connection.cursor.description]
            object_rows = []
            for item in rows:
                object_rows.append(dict(zip(column_names, item)))

            object_rows_list.append({
                'campaign': seller_ids_campaign['campaign'],
                'rows': object_rows
            })

        for index, object_rows in enumerate(object_rows_list):
            historical_sellers_repartition.append({
                'campaign': object_rows['campaign'],
                'seller_leads': []
            })
            for row in object_rows['rows']:
                historical_sellers_repartition[index]['seller_leads'].append({
                    'seller_id': row['ml_vendedor_id'],
                    'seller_name': seller_ids_names[row['ml_vendedor_id']],
                    'form': row['ml_formulario'],
                    'dni': row['ml_dni_persona']
                })

        return historical_sellers_repartition

    def create(self, new_leads_to_db_list):
        try:
            for new_leads_to_db in new_leads_to_db_list:
                for index, row in new_leads_to_db.iterrows():
                    person_id = self.person_crud.create(row)
                    general_campaign_id = 1
                    if row['Nombre de campaña'] == 'Campaña Inversionistas':
                        general_campaign_id = 2

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
                                per_id,
                                cmeg_id
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row['Red social'],
                            row['Formulario'],
                            row['Diplomado'],
                            row['Nombre'],
                            row['Ciudad'],
                            row['DNI'],
                            row['Enfermero'],
                            row['Grado'],
                            row['Celular'],
                            row['Correo'],
                            row['Fecha de registro'],
                            row['Fecha de descarga'],
                            row['Vendedor_ID'],
                            person_id,
                            general_campaign_id
                        ))

                self.db_connection.connection.commit()
                print('Registros insertados correctamente.')

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f'Error al insertar leads: {str(e)}')
