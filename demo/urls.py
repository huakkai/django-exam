"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import kaoshi.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/hello', kaoshi.views.hello),
    # 接口1-查看数量精度
    path('api/v1/unit/<int:id>', kaoshi.views.unit),
    # 接口2-更新数量精度
    path('api/v1/unit', kaoshi.views.update_unit),
    # 接口3-查看商品列表
    path('api/v1/product', kaoshi.views.product),
    # 接口4-更新商品价目表
    path('api/v1/price_list', kaoshi.views.price_list),
    # 接口5-获取库存商品列表、接口6-跟新库存商品数量
    path('api/v1/stock', kaoshi.views.stock),
    # 接口7-新建订单
    path('api/v1/sale_order', kaoshi.views.sale_order),

]
