import requests
from datetime import datetime, timedelta


class RequestHandler:
    def __init__(self, access_token_page, page_id, url_base):
        self.access_token_page = access_token_page
        self.page_id = page_id
        self.url_base = url_base
        self.url_form = f"{url_base}/{page_id}/leadgen_forms"
        self.params_forms, self.params_leads = self.set_params()

    def set_params(self):
        self.params_forms = {
            'access_token': self.access_token_page,
            'limit': 100,
            'fields': 'id,name,context_card,status'
        }

        self.params_leads = {
            'access_token': self.access_token_page,
            'limit': 100,
            'fields': 'created_time,field_data,form_id,platform'
        }

        return self.params_forms, self.params_leads

    def get_forms(self):
        # Realizamos una solicitud GET a la API
        response = requests.get(self.url_form, params=self.params_forms)

        forms = []

        # Verificamos el estado de la respuesta
        if response.status_code == 200:

            data = response.json()

            for form in data['data']:
                if form['status'] == 'ACTIVE':
                    form_id = form['id']

                    if ' + DNI' in form['name']:
                        form['name'] = form['name'].split(' + DNI')[0]
                    if ' NUEVO DNI' in form['name']:
                        form['name'] = form['name'].split(' NUEVO DNI')[0]

                    self.get_forms_by_id(forms, form, form_id)
        else:
            # Si hubo un error, imprimimos el código de estado y el mensaje de error
            print(f'Error {response.status_code}: {response.text}')
            return None

        return forms

    def get_forms_by_id(self, forms, form, form_id):
        form_url = f"{self.url_base}/{form_id}"
        form_response = requests.get(form_url, params={
            'access_token': self.access_token_page,
            'fields': 'context_card'
        })

        if form_response.status_code == 200:
            form_data = form_response.json()
            preview_title = form_data.get('context_card', {}).get('title', '')

            forms.append({
                'id': form_id,
                'name': form['name'],
                'preview_title': preview_title,
                'status': form['status']
            })
        else:
            print(f'Error {form_response.status_code}: {form_response.text}')
            return None

    def get_leads(self, forms, start_date_str, end_date_str):
        all_leads = []

        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y") + timedelta(days=1) - timedelta(seconds=1)

        for form in forms:
            form_id = form['id']
            form_name = form['name']
            preview_title = form['preview_title']

            url = f"{self.url_base}/{form_id}/leads"
            response = requests.get(url, params=self.params_leads)

            if response.status_code == 200:
                data = response.json()

                for lead in data['data']:
                    created_time = datetime.strptime(lead['created_time'], "%Y-%m-%dT%H:%M:%S%z")
                    adjusted_time = created_time - timedelta(hours=5)
                    adjusted_time_naive = adjusted_time.replace(tzinfo=None)

                    if start_date <= adjusted_time_naive <= end_date:
                        lead['created_time'] = adjusted_time_naive.strftime("%d-%m-%Y %H:%M:%S")
                        lead['form_name'] = form_name
                        lead['preview_title'] = preview_title
                        lead['download_time'] = datetime.now().strftime("%d-%m-%Y")

                        all_leads.append(lead)
            else:
                # Si hubo un error, imprimimos el código de estado y el mensaje de error
                print(f'Error {response.status_code}: {response.text}')
                return None

        return all_leads
