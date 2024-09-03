from templates.template_renderer import TemplateRenderer


class HTMLTemplateRenderer(TemplateRenderer):
    def render(self, context):
        # Comenzar con la estructura básica de una tabla HTML
        html_content = '''
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
                <td style="padding: 8px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{seller['Vendedor']}</td>
                <td style="padding: 8px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{seller['Leads']}</td>
            </tr>
            '''

        # Cerrar la tabla
        html_content += '''
            </tbody>
        </table>
        '''

        return html_content
