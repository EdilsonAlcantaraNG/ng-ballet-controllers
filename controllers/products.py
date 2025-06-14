from odoo import http
from odoo.http import request, Response
import json
import base64

ALLOWED_ORIGIN = 'https://screen-printing-form.netlify.app'

class ProductAPIController(http.Controller):

    @http.route('/api/products_serigraphy', type='http', auth='public', cors='*', methods=['GET'], csrf=False)
    def get_products_starting_with_ss(self, **kwargs):
        try:
            name_filter = kwargs.get('name')

            domain = [
                ('name', 'ilike', 'SS-%'),
                ('sale_ok', '=', True)
            ]

            if name_filter:
                domain.append(('name', 'ilike', name_filter))

            products_raw = request.env['product.template'].sudo().search(domain)
            products = [p for p in products_raw if p.name.strip().startswith('SS-')]

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            resultado = []

            for prod in products:
                sizes, colors = [], []
                brands = []
                for line in prod.attribute_line_ids:
                    attr_name = line.attribute_id.name.strip().lower()
                    for ptav in line.product_template_value_ids:
                        value = ptav.product_attribute_value_id
                        item = {
                            'id': value.id,
                            'name': value.name,
                        }
                        if attr_name == 'brand':
                            brands.append(item)
                        if attr_name == 'size':
                            sizes.append(item)
                        elif attr_name == 'color':
                            item['html_color'] = value.html_color or ''
                            colors.append(item)

                resultado.append({
                    'product_id': prod.id,
                    'name': prod.name,
                    'image': f"{base_url}/public/product_image/{prod.product_variant_id.id}",
                    'sizes': sizes,
                    'colors': colors,
                })

            return Response(
                json.dumps({'products': resultado}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=200
            )

        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=500
            )

    @http.route('/api/products_serigraphy_plus', type='http', auth='public', cors='*', methods=['GET'], csrf=False)
    def get_products_starting_with_ss(self, **kwargs):
        try:
            name_filter = kwargs.get('name')

            domain = [
                ('name', 'ilike', 'SS-%'),
                ('sale_ok', '=', True)
            ]

            if name_filter:
                domain.append(('name', 'ilike', name_filter))

            products_raw = request.env['product.template'].sudo().search(domain)
            products = [p for p in products_raw if p.name.strip().startswith('SS-')]

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            resultado = []

            for prod in products:
                sizes, colors = [], []
                brands = []
                for line in prod.attribute_line_ids:
                    attr_name = line.attribute_id.name.strip().lower()
                    for ptav in line.product_template_value_ids:
                        value = ptav.product_attribute_value_id
                        item = {
                            'id': value.id,
                            'name': value.name,
                        }
                        if attr_name == 'brand':
                            brands.append(item)
                        if attr_name == 'size':
                            sizes.append(item)
                        elif attr_name == 'color':
                            item['html_color'] = value.html_color or ''
                            colors.append(item)

                resultado.append({
                    'product_id': prod.id,
                    'name': prod.name,
                    'image': f"{base_url}/web/image/product.product/{prod.product_variant_id.id}/image_128",

                    # Campos adicionales
                    'price': prod.product_variant_id.lst_price,
                    'default_code': prod.default_code or '',
                    'description': prod.description_sale or '',
                    'type': prod.type,
                    'uom_id': {
                        'id': prod.uom_id.id,
                        'name': prod.uom_id.name
                    },
                    'currency_id': {
                        'id': prod.currency_id.id,
                        'name': prod.currency_id.name
                    },
                    'categ_id': {
                        'id': prod.categ_id.id,
                        'name': prod.categ_id.name
                    },
                    'taxes_id': [
                        {'id': tax.id, 'name': tax.name}
                        for tax in prod.taxes_id
                    ],
                    'barcode': prod.barcode or '',
                    'active': prod.active,
                    'create_date': prod.create_date.isoformat() if prod.create_date else None,
                    'write_date': prod.write_date.isoformat() if prod.write_date else None,

                    # Atributos
                    'sizes': sizes,
                    'colors': colors,
                    'brands': brands,
                })

            return Response(
                json.dumps({'products': resultado}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=200
            )

        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)],
                status=500
            )

    @http.route('/public/product_image/<int:product_id>', type='http', cors='*', auth='public')
    def public_product_image(self, product_id):
        product = request.env['product.product'].sudo().browse(product_id)
        if not product.exists() or not product.image_1920:
            return Response(status=404)

        image_data = base64.b64decode(product.image_1920)
        return Response(
            image_data,
            content_type='image/png',
            headers=[
                ('Content-Length', str(len(image_data))),
                ('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            ]
        )

    @http.route('/api/products', type='http', auth='public', cors='*', methods=['GET'], csrf=False)
    def list_products(self, **kwargs):
        try:
            domain = [(key, 'ilike', value) for key, value in kwargs.items()]
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            products = request.env['product.product'].with_user(request.env.user).sudo().search(domain)
            result = [{
                'product_id': p.id,
                'name': p.name,
                'image': f"{base_url}/web/image/product.product/{p.product_variant_id.id}/image_128",
                'price': p.lst_price,
                'default_code': p.default_code or '',
                'description': p.description_sale or '',
                'type': p.type,  # 'consu', 'service', or 'product'
                'uom_id': {
                    'id': p.uom_id.id,
                    'name': p.uom_id.name
                },
                'currency_id': {
                    'id': p.currency_id.id,
                    'name': p.currency_id.name
                },
                'categ_id': {
                    'id': p.categ_id.id,
                    'name': p.categ_id.name
                },
                'taxes_id': [
                    {'id': tax.id, 'name': tax.name}
                    for tax in p.taxes_id
                ],
                'barcode': p.barcode or '',
                'active': p.active,
                'create_date': p.create_date.isoformat() if p.create_date else None,
                'write_date': p.write_date.isoformat() if p.write_date else None
            } for p in products]
            return Response(json.dumps({'products': result}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json',
                            headers=[('Access-Control-Allow-Origin', ALLOWED_ORIGIN)], status=500)