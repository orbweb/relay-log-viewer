from django.contrib import admin
from parse.models import RelayEntry, RelaySession, DataflowMonth

admin.site.register(RelayEntry)
admin.site.register(RelaySession)
admin.site.register(DataflowMonth)
