from templates.template_renderer import TemplateRenderer


class HTMLTemplateRenderer(TemplateRenderer):
    def render(self, context):
        # Comenzar con la estructura básica de una tabla HTML
        html_content = f'''
        <b>{context['campaign_name'][0]}:</b>
        <table border="1" style="border-collapse: collapse; width: 50%; table-layout: fixed;">
            <thead>
                <tr>
                    <th style="padding: 8px; background-color: #f2f2f2; text-align: center;">Vendedor</th>
                    <th style="padding: 8px; background-color: #f2f2f2; text-align: center;">Leads asignados</th>
                </tr>
            </thead>
            <tbody>
        '''

        # Agregar filas con datos de cada vendedor
        for index, seller in context.iterrows():
            html_content += f'''
        <tr>
            {(f'<td style="padding: 8px; background-color: #f2f2f2; text-align: center;">'
              f'<b>{seller["Vendedor"]}</b>'
              f'</td>'
              f'<td style="padding: 8px; background-color: #f2f2f2; text-align: center;">'
              f'<b>{seller["Leads"]}</b>'
              f'</td>') if seller['Vendedor'] == 'TOTAL'
            else
            (f'<td style="padding: 8px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">'
             f'{seller["Vendedor"]}'
             f'</td>'
            f'<td style="padding: 8px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">'
             f'{seller["Leads"]}'
             f'</td>')}
        </tr>
        '''

        # Cerrar la tabla
        html_content += '''
            </tbody>
        </table>
        '''

        return html_content
