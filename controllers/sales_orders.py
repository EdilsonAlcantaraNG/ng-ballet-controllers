from odoo import http
from odoo.http import request, Response
import json

ALLOWED_ORIGIN = 'https://screen-printing-form.netlify.app'

class SaleOrdersAPIController(http.Controller):

    @http.route('/api/sale_orders', type='http', auth='public', methods=['GET'], csrf=False)
    def list_sale_orders(self, **kwargs):
        try:
            domain = [(key, 'ilike', value) for key, value in kwargs.items()]
            orders = request.env['sale.order'].with_user(request.env.user).sudo().search(domain)
            result = [{
                'id': o.id,
                'name': o.name,
                'partner': o.partner_id.name,
                'total': o.amount_total
            } for o in orders]
            return Response(json.dumps({'orders': result}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)

