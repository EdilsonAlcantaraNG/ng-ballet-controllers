from odoo import http
from odoo.http import request, Response
import json

ALLOWED_ORIGIN = 'https://screen-printing-form.netlify.app'

class PartnersAPIController(http.Controller):

    @http.route('/api/partners', type='http', auth='public', methods=['GET'], csrf=False)
    def list_partners(self, **kwargs):
        try:
            domain = [(key, 'ilike', value) for key, value in kwargs.items()]
            partners = request.env['res.partner'].with_user(request.env.user).sudo().search(domain)
            result = [{
                'id': p.id,
                'name': p.name,
                'email': p.email,
                'phone': p.phone,
                'is_customer': p.customer_rank > 0
            } for p in partners]
            return Response(json.dumps({'partners': result}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)

    @http.route('/api/partners', type='http', auth='public', methods=['POST'], csrf=False)
    def create_partner(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            partner = request.env['res.partner'].with_user(request.env.user).sudo().create(data)
            return Response(json.dumps({'id': partner.id, 'name': partner.name, 'email': partner.email, 'phone': partner.phone }), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=201)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)

    @http.route('/api/partners/<int:partner_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_partner(self, partner_id, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            partner = request.env['res.partner'].with_user(request.env.user).sudo().browse(partner_id)
            if not partner.exists():
                return Response(json.dumps({'error': 'Partner not found'}), content_type='application/json',
                                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=404)
            partner.write(data)
            return Response(json.dumps({'status': 'updated'}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)

    @http.route('/api/partners/<int:partner_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_partner(self, partner_id):
        try:
            partner = request.env['res.partner'].with_user(request.env.user).sudo().browse(partner_id)
            if not partner.exists():
                return Response(json.dumps({'error': 'Partner not found'}), content_type='application/json',
                                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=404)
            partner.unlink()
            return Response(json.dumps({'status': 'deleted'}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)


