from django.contrib import admin
from .models import User, BetDeal, Deal, OutputCoin, InputCoin
# Register your models here.
admin.site.register(User)
admin.site.register(BetDeal)
admin.site.register(Deal)
admin.site.register(OutputCoin)
admin.site.register(InputCoin)

