import json

from django.views.decorators.http import require_http_methods
import copy
import random
from . import models
from django.http import JsonResponse, HttpResponse, QueryDict
from psycopg2 import OperationalError, errorcodes
from django.db import transaction
import time
from decimal import Decimal

# Create your views here.


def hello(request):
    """
    GET 获取考生 工号+姓名
    :param request:
        :return:
    """
    # data = {
    #     '工号': '00035687',
    #     '姓名': '闫化强',
    # }
    return HttpResponse('00035687 闫化强', status=200)


@require_http_methods(['GET'])
def unit(request, id=None):
    """
    接口1-查看数量精度
    :param request:
    :param unit_id:
    :return:
    """
    dict_data = {}
    try:
        if id:
            obj_unit = models.Unit.objects.get(pk=id)
            dict_data['res'] = {
                'id': obj_unit.number,
                'name': obj_unit.name,
                'precision': obj_unit.precision,
            }
            return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})


@require_http_methods(['PUT'])
def update_unit(request):
    """
    接口2-更新数量精度
    :param request:
    :return:
    """
    dict_data = {}
    try:
        params = json.loads(request.body)
        id = params.get('id')
        precision = params.get('precision')
        if precision < 0 or not isinstance(precision, int):
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
        obj_unit = models.Unit.objects.get(pk=id)
        if obj_unit:
            obj_unit.precision = precision
            obj_unit.save()
            dict_data['res'] = {
                'id': obj_unit.number,
                'name': obj_unit.name,
                'precision': obj_unit.precision,
            }
            return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
        else:
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})


def _get_round(data, unit):
    """
    数量精度控制
    根据精度控制数据显示位数
    :param data:
    :param precison:
    :return:
    """
    # 获取精度
    try:
        if unit:
            obj_unit = models.Unit.objects.filter(name=unit)
            if not obj_unit:
                return False
            else:
                precision = obj_unit[0].precision
                if not data:
                    if precision:
                        round_data = '0.'
                        for i in range(0, precision):
                            round_data += '0'
                    else:
                        round_data = '0'
                else:
                    round_data = round(data, precision)
                return round_data
        else:
            return False
    except Exception:
        return False


@require_http_methods(['GET'])
def product(request):
    """
    接口3-查看商品列表
    :param request:
    :return:
    """
    dict_data = {'res': []}
    try:
        products = models.Material.objects.all().order_by('id').values()
        for pro in products:
            material_id = pro.get('id')
            price = models.PriceList.objects.filter(material_id=material_id).values()
            prod = {
                'id': pro.get('id'),
                'name': pro.get('name'),
                'unit': pro.get('unit'),
                'price_list': [],
            }
            for p in price:
                price_list = {
                    'quantity_start': _get_round(p.get('quantity_start'), pro.get('unit')),
                    'quantity_end': _get_round(p.get('quantity_end'), pro.get('unit')),
                    'price_start': p.get('price_start'),
                    'price_end': p.get('price_end'),
                }
                prod['price_list'].append(price_list)
            dict_data['res'].append(prod)
        return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})


@require_http_methods(['PUT'])
def price_list(request):
    """
    接口4-更新商品价目表
    :param request:
    :return:
    """
    dict_data = {}
    try:
        params = json.loads(request.body)
        product_id = params.get('product_id')
        if not models.Material.objects.get(pk=product_id):
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
        price_list = params.get('price_list')
        price_begin = []
        price_end = []
        for p in price_list:
            if float(p.get('quantity_start')) < 0 or float(p.get('quantity_end')) < 0 or float(p.get('price_start')) < 0 or float(p.get('price_end')) < 0:
                return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            if float(p.get('quantity_start')) >= float(p.get('quantity_end')) or float(p.get('price_start')) >= float(p.get('price_end')):
                return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            # if isinstance(p.get('quantity_start'), str) or isinstance(p.get('quantity_end'), str) or isinstance(p.get('price_start'), str) or isinstance(p.get('price_end'), str):
            #     return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            price_begin.append(p.get('quantity_start'))
            price_end.append(p.get('quantity_end'))
        for pb in price_begin:
            if pb != min(price_begin):
                if pb not in price_end:
                    return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
        if product_id and price_list:
            # 查询当前产品已有价目表，清空
            has_product_list = models.PriceList.objects.filter(material_id=product_id)
            if has_product_list:
                has_product_list.delete()
            # 创建价目表

            for pl in price_list:
                pl['material_id'] = product_id
                models.PriceList.objects.create(**pl)
            return_price_list = []
            new_product_list = models.PriceList.objects.filter(material_id=product_id)
            unit_name = models.Material.objects.get(pk=product_id).unit
            for npl in new_product_list:
                data_price_list = {
                    'quantity_start': _get_round(npl.quantity_start, unit_name),
                    'quantity_end': _get_round(npl.quantity_end, unit_name),
                    'price_start': npl.price_start,
                    'price_end': npl.price_end,
                }
                return_price_list.append(data_price_list)

            return JsonResponse({'res': {'product_id': product_id, 'price_list': return_price_list}}, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
        else:
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})


@require_http_methods(['GET', 'PUT'])
def stock(request):
    """
    接口5-获取库存商品列表
    接口6-更新库存商品实际数量
    :param request:
    :return:
    """
    dict_data = {}
    res = []
    if request.method == 'GET':
        try:
            stock_obj = models.Stock.objects.all().order_by('id')
            for s in stock_obj:
                # 获取计量单位
                unit_name = s.material_id.unit
                s_dict = {
                    'id': s.id,
                    'product_id_id': s.material_id_id,
                    'quantity': _get_round(s.quantity, unit_name),
                    'product_name': s.material_name,
                }
                res.append(s_dict)
            dict_data['res'] = res
            return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
        except Exception as e:
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
    if request.method == 'PUT':
        try:
            params = json.loads(request.body)
            product_id = params.get('product_id')
            quantity = params.get('quantity')
            obj_product = models.Stock.objects.filter(material_id_id=product_id)
            if not obj_product:
                return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            if quantity < 0 or isinstance(quantity, str):
                return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            # 加锁
            obj_product = _update_data(models.Stock, obj_product[0].id)
            if not obj_product:
                return JsonResponse("当前有其他用户在更新库存信息，请稍后重试", status=403, safe=False, json_dumps_params={"ensure_ascii": False})
            # obj_product.update(**{'quantity': quantity})
            time.sleep(5)
            obj_product.quantity = quantity
            obj_product.save()
            dict_product = {
                'id': obj_product.id,
                'product_id_id': obj_product.material_id_id,
                'quantity': _get_round(Decimal(obj_product.quantity), obj_product.material_id.unit),
                'product_name': obj_product.material_id.name,
                'product_unit': obj_product.material_id.unit,
            }
            dict_data['res'] = dict_product
            return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
        except Exception as e:
            return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})


@transaction.atomic
def _update_data(obj, id):
    """
    加锁更新
    :return:
    """
    sp = transaction.savepoint()
    try:
        o = obj.objects.select_for_update(nowait=True).get(pk=id)
    except Exception as e:
        transaction.savepoint_rollback(sp)
        print("当前有其他用户在更新数据库信息，请稍后重试")
        return JsonResponse("当前有其他用户在更新数据库信息，请稍后重试", status=403, safe=False, json_dumps_params={"ensure_ascii": False})
    return o


@require_http_methods(['POST'])
def sale_order(request):
    """
    接口7-新建订单
    :param request:
    :return:
    """
    dict_data = {}
    try:
        params = request.POST
        order_type = request.POST.get('order_type')
        if order_type not in ['common_order', 'service_order']:
            return JsonResponse("参数异常", status=400, safe=False, json_dumps_params={"ensure_ascii": False})
        biz_date = params.get('biz_date')
        sal_employee = params.get('sal_employee')
        customer = params.get('customer')
        sale_order_line = json.loads(params.get('sale_order_line'))
        # 创建表头
        sale_head = {
            'order_type': order_type,
            'biz_date': biz_date,
            'sal_employee': sal_employee,
            'customer': customer,
            'number': 'SO-' + str(random.randint(0, 100)).zfill(6)
        }
        head = models.SaleOrder.objects.create(**sale_head)
        head.save()
        # 创建表体
        amount_total = 0
        return_line = []
        for i, line in enumerate(sale_order_line):
            line['order_id'] = head.id
            stock_product = models.Stock.objects.filter(material_id=line.get('product_id'))
            price_product = models.PriceList.objects.filter(material_id=line.get('product_id'))
            if price_list:
                label = []
                for pp in price_product:
                    if pp.price_start <= float(line.get('unit_price')) < pp.price_end:
                        label.append(True)
                if not any(label):
                    info = "第" + str(i + 1) + "行明细，单价超出价目表范围"
                    return JsonResponse(info, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
            if stock_product[0].quantity < line.get('quantity'):
                info = "商品" + str(stock_product[0].material_id.name) + "库存不足，请稍后重试"
                return JsonResponse(info, status=403, safe=False, json_dumps_params={"ensure_ascii": False})
            else:
                # stock_product.update(**{'quantity': stock_product[0] - line.get('quantity')})
                quantity = stock_product[0].quantity - line.get('quantity')
                # stock_product.update(**{'quantity': quantity})
                # 加锁更新
                obj_product = _update_data(models.Stock, stock_product[0].id)
                if not obj_product:
                    return JsonResponse("当前有其他用户在更新库存信息，请稍后重试", status=403, safe=False, json_dumps_params={"ensure_ascii": False})
                obj_product.quantity = quantity
                obj_product.save()
            obj_line = models.SaleOrderLine.objects.create(**line)
            obj_line.save()
            return_line.append({
                'product_id': obj_line.product.id,
                'product_name': obj_line.product.name,
                'quantity': _get_round(Decimal(obj_line.quantity), obj_line.product.unit),
                'unit_price': round(Decimal(obj_line.unit_price), 5),
                'amount': round(Decimal(obj_line.unit_price) * Decimal(obj_line.quantity), 2)
            })
            amount_total += (Decimal(obj_line.unit_price) * obj_line.quantity)
        return_order = {
            'id': head.id,
            'order_type': head.order_type,
            'number': head.number,
            'biz_date': head.biz_date,
            'sal_employee': head.sal_employee,
            'customer': head.customer,
            'amount_total': round(amount_total, 2),
            'sale_order_line_ids': return_line
        }
        dict_data['res'] = return_order
        return JsonResponse(dict_data, status=200, safe=False, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse(dict_data, status=400, safe=False, json_dumps_params={"ensure_ascii": False})
