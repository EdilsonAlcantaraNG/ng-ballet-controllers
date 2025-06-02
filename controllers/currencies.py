from odoo import http
from odoo.http import request, Response
import json

ALLOWED_ORIGIN = 'https://screen-printing-form.netlify.app'

class CurrenciesAPIController(http.Controller):

    @http.route('/api/currencies', type='http', auth='public', methods=['GET'], csrf=False)
    def list_currencies(self, **kwargs):
        try:
            domain = [(key, 'ilike', value) for key, value in kwargs.items()]
            currencies = request.env['res.currency'].with_user(request.env.user).sudo().search(domain)
            result = [{
                'id': c.id,
                'name': c.name,
                'symbol': c.symbol
            } for c in currencies]
            return Response(json.dumps({'currencies': result}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)


# controllers/currency_rates_api.py
class CurrencyRatesAPIController(http.Controller):

    @http.route('/api/currency_rates', type='http', auth='public', methods=['GET'], csrf=False)
    def list_currency_rates(self, **kwargs):
        try:
            domain = [(key, 'ilike', value) for key, value in kwargs.items()]
            rates = request.env['res.currency.rate'].with_user(request.env.user).sudo().search(domain)
            result = [{
                'id': r.id,
                'currency': r.currency_id.name,
                'rate': r.rate,
                'date': r.name.strftime('%d/%m/%Y')  # Convertir date a string
            } for r in rates]
            return Response(json.dumps({'rates': result}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)
