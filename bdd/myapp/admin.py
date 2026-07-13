from django.contrib import admin
from django.db import models as dj_models

from . import models as app_models

# 1. Loop automático actualizado (Excluye las tres tablas conflictivas)
for model in app_models.__dict__.values():
    if (
        isinstance(model, type)
        and issubclass(model, dj_models.Model)
        and model._meta.app_label == 'myapp'
        and not model._meta.abstract
        # Excluimos Bodega, BodegaAlmacenaProducto y ProveedorSuministraProducto
        and model.__name__ not in ['Bodega', 'BodegaAlmacenaProducto', 'ProveedorSuministraProducto']
    ):
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass

# REGISTRO PERSONALIZADO PARA EL MODELO BODEGA
@admin.register(app_models.Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('nombre_bodega', 'ubicacion_bodega')
    # Evita que Django use un solo campo como enlace nativo automático
    list_display_links = None 

    # 1. Creamos campos personalizados con enlaces explícitos compuestos para el listado
    def get_list_display(self, request):
        return ('link_nombre_bodega', 'link_ubicacion_bodega')

    def link_nombre_bodega(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="./{}|{}/change/">{}</a>', obj.nombre_bodega, obj.ubicacion_bodega, obj.nombre_bodega)
    link_nombre_bodega.short_description = 'Nombre Bodega'

    def link_ubicacion_bodega(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="./{}|{}/change/">{}</a>', obj.nombre_bodega, obj.ubicacion_bodega, obj.ubicacion_bodega)
    link_ubicacion_bodega.short_description = 'Ubicación Bodega'

    # 2. Reescribimos cómo el admin recupera la bodega en la vista de edición
    def get_object(self, request, object_id, from_field=None):
        try:
            if '|' in object_id:
                nombre_b, ubicacion_b = object_id.split('|')
                return self.get_queryset(request).get(
                    nombre_bodega=nombre_b, 
                    ubicacion_bodega=ubicacion_b
                )
            else:
                # Si Django llega a mandar solo el nombre por error en algún botón interno, 
                # tomamos el primero que coincida para evitar que la página se caiga con un error 500
                return self.get_queryset(request).filter(nombre_bodega=object_id).first()
        except (ValueError, app_models.Bodega.DoesNotExist):
            return None

    # 3. Estructura de la URL para la vista de cambio
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<str:object_id>/change/',
                self.admin_site.admin_view(self.change_view),
                name='myapp_bodega_change'
            ),
        ]
        return custom_urls + urls

@admin.register(app_models.BodegaAlmacenaProducto)
class BodegaAlmacenaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_bodega', 'ubicacion_bodega', 'sku', 'cantidad')
    list_display_links = None # Desactivamos los enlaces por defecto defectuosos

    # Enlaces manuales con la clave triple unida por pipes "|"
    def get_list_display(self, request):
        return ('link_bodega', 'sku', 'cantidad')

    def link_bodega(self, obj):
        from django.utils.html import format_html
        # Pasamos el id compuesto de 3 partes: nombre|ubicacion|sku
        # obj.sku.sku o obj.sku_id según cómo esté definido el campo en tu modelo
        sku_val = obj.sku.sku if hasattr(obj.sku, 'sku') else obj.sku
        return format_html(
            '<a href="./{}|{}|{}/change/">{} ({})</a>', 
            obj.nombre_bodega, obj.ubicacion_bodega, sku_val, obj.nombre_bodega, obj.ubicacion_bodega
        )
    link_bodega.short_description = 'Bodega (Ubicación)'

    # Recuperamos el objeto descomponiendo las 3 partes
    def get_object(self, request, object_id, from_field=None):
        try:
            if '|' in object_id:
                parts = object_id.split('|')
                if len(parts) == 3:
                    nombre_b, ubicacion_b, sku_val = parts
                    return self.get_queryset(request).get(
                        nombre_bodega=nombre_b, 
                        ubicacion_bodega=ubicacion_b,
                        sku=sku_val
                    )
            # Respaldo seguro si falla o falta alguna parte en llamadas internas de Django
            nombre_b = object_id.split('|')[0]
            return self.get_queryset(request).filter(nombre_bodega=nombre_b).first()
        except (ValueError, app_models.BodegaAlmacenaProducto.DoesNotExist):
            return None

    # URL personalizada que acepta el identificador compuesto de 3 campos
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<str:object_id>/change/',
                self.admin_site.admin_view(self.change_view),
                name='myapp_bodegaalmacenaproducto_change'
            ),
        ]
        return custom_urls + urls

# REGISTRO PERSONALIZADO PARA PROVEEDOR SUMINISTRA PRODUCTO (Sin errores de campos)
@admin.register(app_models.ProveedorSuministraProducto)
class ProveedorSuministraProductoAdmin(admin.ModelAdmin):
    # 1. Eliminamos 'id_lote' de aquí para que pase el System Check de Django sin errores
    list_display = ('rut_proveedor', 'sku_producto', 'fecha', 'fecha_vencimiento_lote')
    list_display_links = None  # Desactivamos los enlaces por defecto que provocan colapsos

    # Creamos la fila con un enlace manual combinando RUT, SKU y Fecha
    def get_list_display(self, request):
        return ('link_suministro', 'fecha_vencimiento_lote')

    def link_suministro(self, obj):
        from django.utils.html import format_html
        # Extraemos de forma segura los valores string
        rut_val = obj.rut_proveedor.rut if hasattr(obj.rut_proveedor, 'rut') else getattr(obj, 'rut_proveedor_id', '')
        sku_val = obj.sku_producto.sku if hasattr(obj.sku_producto, 'sku') else getattr(obj, 'sku_producto_id', '')
        # Formateamos la fecha como string YYYY-MM-DD para usarla de forma segura en la URL
        fecha_val = obj.fecha.strftime('%Y-%m-%d') if obj.fecha else 'sin_fecha'
        
        # Unimos los 3 parámetros que identifican este lote de forma exclusiva usando el pipe "|"
        return format_html(
            '<a href="./{}|{}|{}/change/">Prov: {} &rarr; SKU: {} (Fecha Ingreso: {})</a>', 
            rut_val, sku_val, fecha_val, rut_val, sku_val, fecha_val
        )
    link_suministro.short_description = 'Relación Suministro / Lote Inicial'

    # Recuperamos el registro en la vista de edición separando las 3 partes
    def get_object(self, request, object_id, from_field=None):
        try:
            if '|' in object_id:
                parts = object_id.split('|')
                if len(parts) == 3:
                    rut_val, sku_val, fecha_val = parts
                    
                    filtros = {}
                    
                    # 1. Filtrado por Proveedor
                    if hasattr(self.model, 'rut_proveedor'):
                        filtros['rut_proveedor'] = rut_val
                    else:
                        filtros['rut_proveedor_id'] = rut_val
                        
                    # 2. Filtrado por Producto
                    if hasattr(self.model, 'sku_producto'):
                        filtros['sku_producto'] = sku_val
                    else:
                        filtros['sku_producto_id'] = sku_val
                        
                    # 3. Filtrado por la Fecha de Ingreso del lote
                    if fecha_val != 'sin_fecha':
                        filtros['fecha'] = fecha_val

                    # Ejecutamos la consulta unitaria exacta
                    obj = self.get_queryset(request).filter(**filtros).first()
                    if obj:
                        return obj

            # Respaldo en caso de llamadas imperfectas internas de Django
            rut_primer_bloque = object_id.split('|')[0]
            if hasattr(self.model, 'rut_proveedor'):
                return self.get_queryset(request).filter(rut_proveedor=rut_primer_bloque).first()
            return self.get_queryset(request).filter(rut_proveedor_id=rut_primer_bloque).first()
            
        except Exception:
            return None

    # URL compatible con strings complejos para la clave compuesta
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<str:object_id>/change/',
                self.admin_site.admin_view(self.change_view),
                name='myapp_proveedorsuministraproducto_change'
            ),
        ]
        return custom_urls + urls