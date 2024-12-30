from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile

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


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['show_image', 'user', 'city', 'state', 'country']
    
    # Custom function to show user profile image
    def show_image(self, user_profile):
        # if user profile has any image
        if user_profile.profile_picture:
            return format_html(f'<img src="{user_profile.profile_picture.url}" alt="{user_profile.user.email}" width="50" height="50" style="object-fit:cover; border-radius:50%">')
        # if user profile does not have any image
        else:
            return 'No image'
        

admin.site.register(UserProfile, UserProfileAdmin)
        
    