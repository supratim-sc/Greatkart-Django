from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login']

    # having link on fields to open account object
    list_display_links = ['email', 'username']

    '''Making date_joined, last_login fields as read-only, 
    if not specified as read-only along with fieldsets=[], then show error, 
    and if used fieldsets=[] only, then will not show these two fields while open'''
    readonly_fields = ['date_joined', 'last_login']

    # ordering results on admin page by
    ordering = ['-date_joined'] # ordering by 'date_joined' in descending order

    # as we have used custom user model, we need to use some extra properties
    filter_horizontal = []
    list_filter = []

    # show password field as readonly
    fieldsets = []

admin.site.register(Account, AccountAdmin)