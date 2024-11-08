from db.postgres.postgres_connection import PostgresConnection
from repositories.db_crud import DBCrud
from datetime import datetime


class PostgresCampaignsCrud(DBCrud):
    def __init__(self, db_connection: PostgresConnection):
        self.db_connection = db_connection

    def create(self, new_leads):
        try:
            for lead in new_leads:
                if not lead.get('campaign_name'):
                    continue

                self.db_connection.cursor.execute(
                    """
                    SELECT cme_nombre FROM tbl_campanas_meta WHERE cme_nombre = %s;
                    """, (lead['campaign_name'],))
                campaign = self.db_connection.cursor.fetchone()

                if not campaign:
                    general_campaign_id = 1
                    if lead['campaign_name'] == 'CAMPAÑA AREQUIPA':
                        general_campaign_id = 2

                    self.db_connection.cursor.execute("""
                    INSERT INTO tbl_campanas_meta (
                        cme_nombre,
                        cmeg_id,
                        aud_fecha_creacion,
                        aud_fecha_modificacion
                        ) VALUES (%s, %s, %s, %s);
                        """, (
                        lead['campaign_name'],
                        general_campaign_id,
                        datetime.now(),
                        datetime.now()
                    ))

                    self.db_connection.connection.commit()

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f'Error al insertar campañas: {str(e)}')

    def get_general_campaigns(self):
        try:
            self.db_connection.cursor.execute(
                """
                SELECT cmeg_id, cmeg_nombre FROM tbl_campanas_meta_general;
                """
            )
            rows = self.db_connection.cursor.fetchall()
            column_names = [desc[0] for desc in self.db_connection.cursor.description]
            object_rows = []

            for item in rows:
                object_rows.append(dict(zip(column_names, item)))

            return object_rows

        except Exception as e:
            print(f'Error al obtener la cantidad de campañas: {str(e)}')
            return None

    def get_sellers_campaigns(self):
        seller_campaigns = []
        general_campaigns = self.get_general_campaigns()
        try:
            for index, general_campaign in enumerate(general_campaigns):
                seller_campaigns.append({
                    'general_campaign_name': general_campaign['cmeg_nombre'],
                    'sellers': []
                })

                self.db_connection.cursor.execute(
                    """
                    SELECT cmeg_id, cmv_activo, vendedor_id, cmv_prioridad, cmv_leads_fijos, cmv_leads_adicionales, aau.name FROM tbl_campanas_meta_vendedor cmv
                    INNER JOIN apps_auth_userprofile aau ON aau.id = cmv.vendedor_id
                    WHERE cmv.cmv_activo = True AND cmv.cmeg_id = %s;
                    """, (general_campaign['cmeg_id'],)
                )

                rows = self.db_connection.cursor.fetchall()
                column_names = [desc[0] for desc in self.db_connection.cursor.description]
                object_rows = []

                for item in rows:
                    object_rows.append(dict(zip(column_names, item)))

                for row in object_rows:
                    seller_campaigns[index]['sellers'].append({
                        'id': row['vendedor_id'],
                        'name': row['name'],
                        'fixed_leads': row['cmv_leads_fijos'],
                        'additional_leads': row['cmv_leads_adicionales'],
                        'priority': row['cmv_prioridad']
                    })

            return seller_campaigns

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f'Error al obtener campañas de vendedores: {str(e)}')
            return []
