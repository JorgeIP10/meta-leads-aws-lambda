import copy
import random
import pandas as pd


class DataHandler:
    def __init__(self, campaigns_seller_leads_object_list, historical_sellers_repartition_list, new_leads):
        self.campaigns_seller_leads_object_list = campaigns_seller_leads_object_list
        self.historical_sellers_repartition_list = historical_sellers_repartition_list
        self.new_leads = new_leads
        self.df_new_leads = pd.DataFrame()
        self.dict_sellers = None
        self.highest_priority_sellers_count = 0
        self.highest_priority_sellers_list = []
        self.leads_with_priority = 0
        self.created_time_name_str = 'Fecha de registro'
        self.download_time_name_str = 'Fecha de descarga'

    def new_leads_to_dataframe(self):
        campaigns = [object['campaign'] for object in self.campaigns_seller_leads_object_list]

        for lead in self.new_leads:
            lead_info = {
                'form_name': lead.get('form_name', '').upper(),
                'preview_title': lead.get('preview_title', '').upper(),
                'download_time': lead.get('download_time', ''),
                'platform': lead.get('platform', ''),
                '¿cuál_es_tu_nivel_de_estudios?': '',
                '¿eres_enfermero?': '',
                'nombre': '',
                'apellido_paterno': '',
                'apellido_materno': '',
                'full_name': '',
                'email': '',
                'city': '',
                'phone_number': '',
                'dni': '',
                'created_time': lead.get('created_time', ''),
                'campaign_name': lead.get('campaign_name', 'Sin campaña')
            }

            for field in lead.get('field_data', []):
                if field.get('values'):
                    lead_info[field['name']] = field['values'][0]

                if field['name'] == 'phone_number' and field['values'][0].startswith('+51'):
                    lead_info[field['name']] = field['values'][0].split('+51')[1]

            lead_info['full_name'] = (f"{lead_info['nombre']} "
                                      f"{lead_info['apellido_paterno']} "
                                      f"{lead_info['apellido_materno']}")

            if (lead_info['campaign_name'] not in campaigns):
                lead_info['campaign_name'] = 'Campaña OEA'

            for campaigns_seller_leads_object in self.campaigns_seller_leads_object_list:
                if campaigns_seller_leads_object['campaign'] != lead_info['campaign_name']:
                    continue
                campaigns_seller_leads_object['leads'].append(lead_info)

        for index, campaign_seller_leads_object in enumerate(self.campaigns_seller_leads_object_list):
            leads = pd.DataFrame(campaign_seller_leads_object['leads'])
            self.campaigns_seller_leads_object_list[index]['leads_dataframe'] = leads
            self.campaigns_seller_leads_object_list[index]['leads_dataframe'].rename(columns={
                'platform': 'Red social',
                'form_name': 'Formulario',
                'preview_title': 'Diplomado',
                'full_name': 'Nombre completo',
                'nombre': 'Nombre',
                'apellido_paterno': 'Apellido paterno',
                'apellido_materno': 'Apellido materno',
                'city': 'Ciudad',
                'dni': 'DNI',
                '¿eres_enfermero?': 'Enfermero',
                '¿cuál_es_tu_nivel_de_estudios?': 'Grado',
                'phone_number': 'Celular',
                'email': 'Correo',
                'created_time': self.created_time_name_str,
                'download_time': self.download_time_name_str,
                'campaign_name': 'Nombre de campaña'
            }, inplace=True)

    def transform_data_to_db(self):
        def map_enfermero(value):
            if pd.isna(value):
                return None
            return {'sí': True, 'no': False}.get(value, None)

        new_leads_to_db_list = []

        for campaigns_seller_leads_object in self.campaigns_seller_leads_object_list:
            leads_dataframe = campaigns_seller_leads_object['leads_dataframe']
            if leads_dataframe.empty:
                continue

            leads_dataframe['Enfermero'] = leads_dataframe['Enfermero'].map(map_enfermero)

            leads_dataframe['DNI'] = leads_dataframe['DNI'].apply(lambda x: str(int(x)) if pd.notna(x) else 'None')
            leads_dataframe[self.created_time_name_str] = pd.to_datetime(leads_dataframe[self.created_time_name_str],
                                                                        format='%d-%m-%Y %H:%M:%S')
            leads_dataframe[self.download_time_name_str] = pd.to_datetime(leads_dataframe[self.download_time_name_str],
                                                                         format='%d-%m-%Y')
            new_leads_to_db_list.append(leads_dataframe)

        return new_leads_to_db_list

    def prepare_data(self, campaigns_seller_leads_object):
        self.highest_priority_sellers_list = []
        self.highest_priority_sellers_count = 0
        sellers_distribute = campaigns_seller_leads_object['sellers_data_structure'].get_sellers_list()
        len_new_leads_to_distribute = len(campaigns_seller_leads_object['leads'])
        len_sellers = len(sellers_distribute)
        exists_priority = False

        if len_new_leads_to_distribute < len_sellers:
            leads_by_seller = 1
            res_leads_by_seller = -1
            len_for = len_new_leads_to_distribute
            self.highest_priority_sellers_list = campaigns_seller_leads_object['sellers_data_structure'].priority_sellers_handler.remove_highest_priority()
        else:
            fixed_leads = 0
            number_of_sellers_with_fixed_leads = 0
            for seller in sellers_distribute:
                if seller['fixed_leads'] > 0:
                    fixed_leads += seller['fixed_leads']
                    number_of_sellers_with_fixed_leads += 1

            len_new_leads_to_distribute -= fixed_leads
            len_sellers -= number_of_sellers_with_fixed_leads
            leads_by_seller = int(len_new_leads_to_distribute / len_sellers)
            res_leads_by_seller = len_new_leads_to_distribute % len_sellers
            len_for = res_leads_by_seller

            self.highest_priority_sellers_count = campaigns_seller_leads_object['sellers_data_structure'].priority_sellers_handler.get_highest_priority_sellers_count()
            if self.highest_priority_sellers_count > 0:
                self.highest_priority_sellers_list = campaigns_seller_leads_object['sellers_data_structure'].priority_sellers_handler.remove_highest_priority()

                leads_with_priority = 0
                for seller in self.highest_priority_sellers_list:
                    seller['leads'] = seller['additional_leads'] + leads_by_seller
                    leads_with_priority += seller['leads']

                len_new_leads_to_distribute_with_priority = len_new_leads_to_distribute - leads_with_priority
                len_sellers_with_priority = len_sellers - self.highest_priority_sellers_count

                if len_new_leads_to_distribute_with_priority >= len_sellers_with_priority:
                    leads_by_seller = int(len_new_leads_to_distribute_with_priority / len_sellers_with_priority)
                    res_leads_by_seller = len_new_leads_to_distribute_with_priority % len_sellers_with_priority
                    len_for = res_leads_by_seller
                    exists_priority = True

        sellers_distribute: list = campaigns_seller_leads_object['sellers_data_structure'].get_sellers_list() + self.highest_priority_sellers_list
        sellers_with_fixed_leads = []
        indexes_to_remove = []

        for index, seller in enumerate(sellers_distribute):
            seller['is_chosen'] = False
            seller['is_eligible'] = True

            if seller['fixed_leads'] > 0:
                seller['leads'] = seller['fixed_leads']
                indexes_to_remove.append(index)
                sellers_with_fixed_leads.append(seller)
            elif seller['additional_leads'] > 0:
                if not exists_priority:
                    seller['leads'] = leads_by_seller
                else:
                    seller['is_eligible'] = False
            else:
                seller['leads'] = leads_by_seller

        # Se eliminan los vendedores con leads fijos
        deleted_sellers = 0
        for index in indexes_to_remove:
            del sellers_distribute[index - deleted_sellers]
            deleted_sellers += 1

        sellers_distribute_copy = copy.deepcopy(sellers_distribute)
        eligible_sellers = [seller for seller in sellers_distribute_copy if seller['is_eligible']]

        # Se agregan los leads restantes aleatoriamente
        if res_leads_by_seller != 0:
            for i in range(len_for):
                random_seller_leads = random.choice(eligible_sellers)
                random_seller_index = sellers_distribute_copy.index(random_seller_leads)

                sellers_distribute_copy[random_seller_index]['leads'] += 1
                sellers_distribute_copy[random_seller_index]['is_chosen'] = True
                eligible_sellers.remove(random_seller_leads)

        # Usar .loc[] para evitar SettingWithCopyWarning
        campaigns_seller_leads_object['leads_dataframe'].loc[:, 'Vendedor'] = None

        sellers_distribute_copy += sellers_with_fixed_leads

        for seller in sellers_distribute_copy:
            seller['count'] = 0
            seller['is_available'] = True
            campaigns_seller_leads_object['sellers_data_structure'].update_seller(seller['id'], seller)

        return sellers_distribute_copy

    def distribute_leads(self, sellers_distribute_copy, leads_dataframe):
        restart = True

        sellers_distribute_copy_copy = copy.deepcopy(sellers_distribute_copy)
        sellers_distribute_copy_while = []

        while restart:
            restart = False
            sellers_distribute_copy_while = copy.deepcopy(sellers_distribute_copy_copy)

            for index, lead in leads_dataframe.iterrows():
                sellers_copy = copy.deepcopy(sellers_distribute_copy_while)

                random_seller_leads = None
                random_seller_index = None

                while sellers_copy:
                    random_seller_leads = random.choice(sellers_copy)
                    random_seller_index = sellers_distribute_copy_while.index(random_seller_leads)

                    if random_seller_leads['count'] == random_seller_leads['leads']:
                        sellers_copy.remove(random_seller_leads)
                        random_seller_leads['is_available'] = False

                        count = 0
                        for seller in sellers_distribute_copy_while:
                            if seller['count'] == seller['leads']:
                                count += 1

                        if not sellers_copy and count != len(sellers_distribute_copy_while):
                            print('NO HAY MÁS VENDEDORES DISPONIBLES, NO TODOS HAN ALCANZADO SU CUOTA, SE REINICIA')
                            restart = True
                            break

                        continue
                    else:
                        for historical_sellers_repartition in self.historical_sellers_repartition_list:
                            for historical_seller_repartition in historical_sellers_repartition['seller_leads']:
                                if (random_seller_leads['name'] == historical_seller_repartition['seller_name']
                                        and (lead['Formulario'] == historical_seller_repartition['form']
                                             and lead['DNI'] == historical_seller_repartition['dni'])):
                                    print(f'REPETIDO: {random_seller_leads["name"]}\n')
                                    for seller in sellers_copy:
                                        if seller['name'] == random_seller_leads['name']:
                                            sellers_copy.remove(random_seller_leads)

                                            if sellers_copy:
                                                print(f'HAY MÁS VENDEDORES DISPONIBLES,'
                                                      f'el vendedor {random_seller_leads["name"]} se elimina')
                                                random_seller_leads['is_available'] = False
                                            else:
                                                print('NO HAY MÁS VENDEDORES DISPONIBLES')
                                                restart = True
                                            break

                                if restart:
                                    break

                                if not random_seller_leads['is_available']:
                                    print('OTRO INTENTO')
                                    break

                    if restart:
                        break

                    if random_seller_leads['is_available']:
                        break

                if restart:
                    print('---------------------REINICIO---------------------')
                    break

                if random_seller_leads['is_available']:
                    print(f'{random_seller_leads["name"]} + 1')
                    sellers_distribute_copy_while[random_seller_index]['count'] += 1

                    leads_dataframe.at[index, 'Vendedor'] = sellers_distribute_copy_while[random_seller_index]['name']
                    leads_dataframe.at[index, 'Leads'] = sellers_distribute_copy_while[random_seller_index]['leads']

        return sellers_distribute_copy_while

    def get_dataframes_to_email(self):
        distributed_leads_sellers_list = []
        campaign_dataframes_list = []
        for index, campaigns_seller_leads_object in enumerate(self.campaigns_seller_leads_object_list):
            if not campaigns_seller_leads_object['leads']:
                continue
            campaign_dataframes_list.append({
                'campaign': campaigns_seller_leads_object['campaign'],
                'leads_dataframe': campaigns_seller_leads_object['leads_dataframe']
            })
            prepared_data = self.prepare_data(campaigns_seller_leads_object)
            distributed_leads_sellers = self.distribute_leads(prepared_data, campaigns_seller_leads_object['leads_dataframe'])
            distributed_leads_sellers_list.append(distributed_leads_sellers)

        sellers_dict_list = []
        dict_sellers_ids = {}

        for distributed_leads_sellers in distributed_leads_sellers_list:
            total_leads = 0
            total_count = 0
            seller_dict = {}
            for seller in distributed_leads_sellers:
                if seller['leads'] != seller['count']:
                    print(f'Vendedor: {seller["name"]}')
                    print(f'Leads asignados: {seller["leads"]}')
                    print(f'Contador de leads: {seller["count"]}')
                    print(f'Leads no asignados: {seller["leads"] - seller["count"]}')
                    print('---------------------')

                seller_dict[seller['name']] = seller['count']
                dict_sellers_ids[seller['name']] = seller['id']

                total_leads += seller['leads']
                total_count += seller['count']

            seller_dict['TOTAL'] = total_count
            sellers_dict_list.append(seller_dict)

            print(f'Total de leads: {total_leads}')
            print(f'Total de leads asignados: {total_count}')

        print(sellers_dict_list)
        leads_to_email_dict_list = []
        count = 1

        for index, campaign_dataframe in enumerate(campaign_dataframes_list):
            campaign_dataframe['leads_dataframe']['Vendedor_ID'] =(
                campaign_dataframe['leads_dataframe']['Vendedor'].map(lambda x: dict_sellers_ids[x]))
            campaign_dataframe['leads_dataframe'].sort_values(by=self.created_time_name_str, inplace=True)
            df_new_leads_to_email = campaign_dataframe['leads_dataframe'].drop(columns=['Vendedor_ID'])
            df_columns = [
                'Nombre de campaña', 'Formulario', 'Diplomado', self.download_time_name_str,
                'Red social', 'Grado', 'Enfermero',
                'Nombre', 'Apellido paterno', 'Apellido materno',
                'Nombre completo', 'Correo', 'Ciudad',
                'Celular', 'Vendedor', 'DNI',
                self.created_time_name_str, 'Leads'
            ]
            df_new_leads_to_email = df_new_leads_to_email.reindex(columns=df_columns)

            dict_lead_detail_to_email = {
                'dataframe': df_new_leads_to_email,
                'sheet_name': f'Detalle - {count}',
            }

            dict_sellers_df = pd.DataFrame(sellers_dict_list[index].items(), columns=['Vendedor', 'Leads'])
            dict_lead_sellers_to_email = {
                'dataframe': dict_sellers_df,
                'sheet_name': f'Resumen - {count}',
            }

            count += 1
            leads_to_email_dict_list.append([dict_lead_detail_to_email, dict_lead_sellers_to_email])

        return leads_to_email_dict_list
