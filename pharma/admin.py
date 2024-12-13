from django.contrib import admin
from .models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell, UmutiEntreeBackup, UsdToBif,\
    BonDeCommande

# Register your models here.

admin.site.register(UmutiEntree)
admin.site.register(ImitiSet)
admin.site.register(UmutiSold)
admin.site.register(umutiReportSell)
admin.site.register(UmutiEntreeBackup)
admin.site.register(UsdToBif)
admin.site.register(BonDeCommande)