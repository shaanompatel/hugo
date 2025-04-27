from django.db import models


class SalesOrder(models.Model):
    sales_order_id = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    quantity = models.IntegerField()
    order_type = models.CharField(max_length=100)
    requested_date = models.CharField(max_length=100)
    created_at = models.CharField(max_length=100)
    accepted_request_date = models.CharField(max_length=100)

    class Meta:
        db_table = 'sales_orders'


class StockLevel(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    quantity_available = models.IntegerField()

    class Meta:
        db_table = 'stock_levels'


class StockMovement(models.Model):
    date = models.CharField(max_length=100)
    part_id = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'stock_movements'


class Supplier(models.Model):
    supplier_id = models.CharField(max_length=100)
    part_id = models.CharField(max_length=100)
    price_per_unit = models.FloatField()
    lead_time_days = models.IntegerField()
    min_order_qty = models.IntegerField()
    reliability_rating = models.FloatField()

    class Meta:
        db_table = 'suppliers'


class DispatchParameter(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    min_stock_level = models.IntegerField()
    reorder_quantity = models.IntegerField()
    reorder_interval_days = models.IntegerField()

    class Meta:
        db_table = 'dispatch_parameters'


class MaterialMaster(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    part_type = models.CharField(max_length=100)
    used_in_models = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    weight = models.FloatField()
    blocked_parts = models.CharField(max_length=100, null=True, blank=True)
    successor_parts = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'material_master'


class MaterialOrder(models.Model):
    order_id = models.CharField(max_length=100, primary_key=True)
    part_id = models.CharField(max_length=100)
    quantity_ordered = models.IntegerField()
    order_date = models.CharField(max_length=100)
    expected_delivery_date = models.CharField(max_length=100)
    supplier_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    actual_delivered_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'material_orders'



# BOM tables for each model
class S1V1BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S1_V1_BOM'


class S1V2BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S1_V2_BOM'


class S2V1BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S2_V1_BOM'


class S2V2BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S2_V2_BOM'


class S3V1BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S3_V1_BOM'


class S3V2BOM(models.Model):
    part_id = models.CharField(max_length=100, primary_key=True)
    part_name = models.CharField(max_length=255)
    qty = models.IntegerField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'S3_V2_BOM'

