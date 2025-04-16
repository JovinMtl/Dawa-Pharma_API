from django.contrib import admin
from .models import UmutiEntree, ImitiSet, UmutiSold, \
    umutiReportSell, UmutiEntreeBackup, UsdToBif,\
    Assurance,\
    SubClassThep, ClassThep,\
    BonDeCommand, Client, BeneficeProgram as MinimumBenefice

# Register your models here.

admin.site.register(UmutiEntree)
admin.site.register(ImitiSet)
admin.site.register(UmutiSold)
admin.site.register(umutiReportSell)
admin.site.register(UmutiEntreeBackup)
admin.site.register(UsdToBif)
admin.site.register(Assurance)
admin.site.register(ClassThep)
admin.site.register(SubClassThep)
admin.site.register(BonDeCommand)
admin.site.register(Client)
admin.site.register(MinimumBenefice) 

admin.site.site_title = "Pharmacie UBUZIMA"
admin.site.site_header = "Pharmacie Ubuzima Administration"
admin.site.index_title = "Soyez prudent dans cette zone, vous signale Jov."