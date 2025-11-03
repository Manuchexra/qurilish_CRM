from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html  # Bu importni qo'shing
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'colored_role', 'phone_number', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Role Information'), {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number'),
        }),
    )
    
    # Role bo'yicha rangli ko'rsatish
    def colored_role(self, obj):
        colors = {
            'super_admin': 'red',
            'main_warehouse_admin': 'orange',
            'warehouse_admin': 'blue',
            'main_warehouse_forwarder': 'green', 
            'warehouse_receiver': 'purple',
        }
        color = colors.get(obj.role, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_role_display())
    colored_role.short_description = 'Roli'
    colored_role.admin_order_field = 'role'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Super admin bo'lmagan foydalanuvchilar uchun cheklovlar
        if not request.user.is_superuser:
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'role' in form.base_fields and obj:
                form.base_fields['role'].disabled = True
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Agar foydalanuvchi super admin bo'lmasa, faqat o'zini va pastroq darajadagi foydalanuvchilarni ko'rsin
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)
    
    def has_change_permission(self, request, obj=None):
        # Super admin bo'lmagan foydalanuvchilar boshqa super adminlarni o'zgartira olmasin
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Super admin bo'lmagan foydalanuvchilar boshqa super adminlarni o'chira olmasin
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    # Qo'shimcha admin actionlar
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} ta foydalanuvchi faollashtirildi")
    activate_users.short_description = "Tanlangan foydalanuvchilarni faollashtirish"
    
    def deactivate_users(self, request, queryset):
        # Super adminlarni faolsizlantirishni oldini olish
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists() and not request.user.is_superuser:
            self.message_user(request, "Super admin foydalanuvchilarni faolsizlantirish mumkin emas!", level='ERROR')
            return
        
        regular_users = queryset.filter(is_superuser=False)
        updated = regular_users.update(is_active=False)
        self.message_user(request, f"{updated} ta foydalanuvchi faolsizlantirildi")
    deactivate_users.short_description = "Tanlangan foydalanuvchilarni faolsizlantirish"

# Admin panel sarlavhasini o'zgartirish
admin.site.site_header = "Qurilish Mollari CRM Tizimi"
admin.site.site_title = "Warehouse CRM"
admin.site.index_title = "Boshqaruv paneliga xush kelibsiz"