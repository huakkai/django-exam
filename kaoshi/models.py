from django.db import models
from django.utils import timezone

# Create your models here.


class Unit(models.Model):
    number = models.CharField('编号', max_length=10)
    name = models.CharField('名称', max_length=10)
    precision = models.IntegerField('精度')

    class Meta:
        db_table = "unit"

    def __str__(self):
        return "%s" % [self.name]

    def __unicode__(self):
        return '%d: %s' % (self.number, self.name, self.precision)


class Material(models.Model):
    number = models.CharField('编号', max_length=50)
    name = models.CharField('名称', max_length=50)
    unit = models.CharField('计量单位', max_length=50, default='个')

    class Meta:
        db_table = "product"

    def __str__(self):
        return "%s" % [self.name]

    def __unicode__(self):
        return '%d: %s' % (self.number, self.name, self.uom_id)


class PriceList(models.Model):
    material = models.ForeignKey("Material", on_delete=models.CASCADE)
    quantity_start = models.DecimalField(max_digits=19, decimal_places=10)
    quantity_end = models.DecimalField(max_digits=19, decimal_places=10)
    price_start = models.DecimalField(max_digits=19, decimal_places=5)
    price_end = models.DecimalField(max_digits=19, decimal_places=5)

    class Meta:
        db_table = "price_list"

    def __str__(self):
        return "%s" % [self.id]

    def __unicode__(self):
        return '%d: %s' % (self.quantity_start, self.quantity_end)


class Stock(models.Model):
    material_id = models.OneToOneField("Material", on_delete=models.CASCADE)
    material_name = models.CharField(max_length=50)
    material_unit = models.CharField(max_length=50)
    # material_unit_price = models.DecimalField(max_digits=19, decimal_places=5)
    quantity = models.DecimalField(max_digits=19, decimal_places=10)

    class Meta:
        db_table = "stock"

    def __str__(self):
        return "%s" % [self.material_name]

    def __unicode__(self):
        return '%d: %s' % (self.material_name, self.material_unit, self.material_unit_price, self.quantity)


class SaleOrder(models.Model):
    number = models.CharField('Number', max_length=50)
    order_type = models.CharField(max_length=50, default=None)
    biz_date = models.DateTimeField(default=None)
    sal_employee = models.CharField(max_length=50, default=None)
    customer = models.CharField(max_length=50, default=None)

    class Meta:
        db_table = "sale_order"

    def __str__(self):
        return "%s" % [self.number]

    def __unicode__(self):
        return '%d' % (self.number,)


class SaleOrderLine(models.Model):

    order = models.ForeignKey("SaleOrder", on_delete=models.CASCADE)
    product = models.ForeignKey("Material", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=19, decimal_places=5, default=0)
    unit_price = models.DecimalField(max_digits=19, decimal_places=5, default=0)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)

    class Meta:
        db_table = "sale_order_line"

    def __str__(self):
        return "%s" % [self.product]

    def __unicode__(self):
        return '%d: %s' % (self.product, self.quantity)
