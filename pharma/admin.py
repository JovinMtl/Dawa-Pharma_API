from django.contrib import admin
from .models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell, UmutiEntreeBackup, UsdToBif,\
    BonDeCommande, Assurance,\
    SubClassThep, ClassThep,\
    BonDeCommand, Client

# Register your models here.

admin.site.register(UmutiEntree)
admin.site.register(ImitiSet)
admin.site.register(UmutiSold)
admin.site.register(umutiReportSell)
admin.site.register(UmutiEntreeBackup)
admin.site.register(UsdToBif)
# admin.site.register(BonDeCommande)
admin.site.register(Assurance)
admin.site.register(ClassThep)
admin.site.register(SubClassThep)
admin.site.register(BonDeCommand)
admin.site.register(Client)