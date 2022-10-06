from django.contrib import admin

from tests.market.admin.checkout_admin import CheckoutAdmin
from tests.market.admin.generalmanager_admin import GeneralManagerAdmin
from tests.market.admin.inventory_admin import InventoryAdmin
from tests.market.admin.item_admin import ItemAdmin
from tests.market.admin.item_sale_admin import ItemSaleAdmin
from tests.market.admin.shop_admin import ShopAdmin
from tests.market.admin.shoppingmall_admin import ShoppingMallAdmin
from tests.market.admin.transaction_admin import TransactionAdmin
from tests.market.models import (
    Checkout,
    GeneralManager,
    Inventory,
    Item,
    ItemSale,
    Shop,
    ShoppingMall,
    Transaction,
)

admin.site.register(Item, ItemAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(ShoppingMall, ShoppingMallAdmin)
admin.site.register(GeneralManager, GeneralManagerAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ItemSale, ItemSaleAdmin)
admin.site.register(Checkout, CheckoutAdmin)
