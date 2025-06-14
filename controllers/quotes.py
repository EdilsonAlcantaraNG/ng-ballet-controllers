from odoo import http
from odoo.http import request, Response
import json

ALLOWED_ORIGIN = "https://screen-printing-form.netlify.app"  # o define un dominio específico si lo necesitas

class QuoteAPIController(http.Controller):

    # CREATE NEW QUOTES
    @http.route('/api/quotes', type='json', auth='public', cors='*', csrf=False, methods=['POST'])
    def create_quote(self, **kwargs):
        try:
            data = request.jsonrequest

            # Validaciones básicas
            if not data.get('partner_id') or not data.get('order_lines'):
                return Response(
                    json.dumps({'error': 'Missing partner_id or order_lines'}),
                    content_type='application/json',
                    status=400
                )

            # Crear cotización
            sale_order = request.env['sale.order'].sudo().create({
                'partner_id': data['partner_id'],
                'date_order': data.get('date_order'),
                'validity_date': data.get('validity_date'),
                'note': data.get('note'),
            })

            # Crear líneas de la cotización
            for line in data['order_lines']:
                product = request.env['product.product'].sudo().browse(line['product_id'])
                if not product.exists():
                    continue  # o puedes lanzar error

                request.env['sale.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'product_id': product.id,
                    'product_uom_qty': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', product.lst_price),
                    'name': line.get('name', product.name),
                    'product_uom': product.uom_id.id,
                })

            return Response(
                json.dumps({'quote_id': sale_order.id, 'name': sale_order.name}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=201
            )

        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=500
            )

    # GET ALL QUOTES
    @http.route('/api/quotes', type='http', auth='public', cors='*', csrf=False, methods=['GET'])
    def get_quotes(self, **kwargs):
        try:
            domain = [(key, '=', value) for key, value in kwargs.items()]
            quotes = request.env['sale.order'].sudo().search(domain)

            result = []
            for q in quotes:
                lines = [{
                    'id': l.id,
                    'product_id': l.product_id.id,
                    'product_name': l.product_id.name,
                    'quantity': l.product_uom_qty,
                    'price_unit': l.price_unit,
                    'subtotal': l.price_subtotal
                } for l in q.order_line]

                result.append({
                    'id': q.id,
                    'name': q.name,
                    'partner_id': q.partner_id.id,
                    'partner_name': q.partner_id.name,
                    'date_order': q.date_order.isoformat(),
                    'validity_date': q.validity_date.isoformat() if q.validity_date else None,
                    'state': q.state,
                    'note': q.note,
                    'lines': lines
                })

            return Response(
                json.dumps({'quotes': result}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=200
            )
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)

    # UPDATE QUOTE
    @http.route('/api/quotes/<int:quote_id>', type='json', auth='public', cors='*', csrf=False, methods=['PUT', 'PATCH'])
    def update_quote(self, quote_id, **kwargs):
        try:
            data = request.jsonrequest
            sale_order = request.env['sale.order'].sudo().browse(quote_id)

            if not sale_order.exists():
                return Response(json.dumps({'error': 'Quote not found'}), content_type='application/json', status=404)

            # Update fields
            update_vals = {}
            for field in ['partner_id', 'date_order', 'validity_date', 'note']:
                if field in data:
                    update_vals[field] = data[field]
            if update_vals:
                sale_order.write(update_vals)

            # Optional: update lines
            if 'order_lines' in data:
                # Remove existing lines (optional — depends on logic)
                sale_order.order_line.unlink()

                for line in data['order_lines']:
                    product = request.env['product.product'].sudo().browse(line['product_id'])
                    if not product.exists():
                        continue  # or raise error

                    request.env['sale.order.line'].sudo().create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'product_uom_qty': line.get('quantity', 1),
                        'price_unit': line.get('price_unit', product.lst_price),
                        'name': line.get('name', product.name),
                        'product_uom': product.uom_id.id,
                    })

            return Response(
                json.dumps({'success': True, 'quote_id': sale_order.id}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=200
            )

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)
            
    # GET ALL PURCHASE QUOTES
    @http.route('/api/purchase_quotes', type='http', auth='public', cors='*', csrf=False, methods=['GET'])
    def get_purchase_quotes_by_vendor(self, **kwargs):
        try:
            vendor_id = kwargs.get('vendor_id')
            domain = []

            if vendor_id:
                domain.append(('partner_id', '=', int(vendor_id)))

            purchases = request.env['purchase.order'].sudo().search(domain)

            result = []
            for p in purchases:
                lines = [{
                    'id': l.id,
                    'product_id': l.product_id.id,
                    'product_name': l.product_id.name,
                    'quantity': l.product_qty,
                    'price_unit': l.price_unit,
                    'subtotal': l.price_subtotal
                } for l in p.order_line]

                result.append({
                    'id': p.id,
                    'name': p.name,
                    'vendor_id': p.partner_id.id,
                    'vendor_name': p.partner_id.name,
                    'date_order': p.date_order.isoformat(),
                    'state': p.state,
                    'lines': lines
                })

            return Response(
                json.dumps({'purchase_quotes': result}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=200
            )

        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                            status=500)