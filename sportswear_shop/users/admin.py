from typing import Optional
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.http import HttpRequest
from .models import User, UserGroup


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомная админка для модели User с расширенным отображением и настройками.
    """
    list_display = ('username', 'email', 'phone', 'avatar_preview', 'status_badge', 'date_joined_short')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'email_verified')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Статусы', {
            'fields': ('is_active', 'email_verified', 'is_staff', 'is_superuser')
        }),
        ('Права доступа', {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions')
        }),
        ('Даты', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        ('Обязательные поля', {
            'fields': (
                'username',
                'password1',
                'password2',
                'email'
            )
        }),
        ('Персональная информация', {
            'fields': (
                'first_name',
                'last_name',
                'phone',
                'avatar'
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active',
                'is_staff',
                'groups'
            )
        }),
    )

    def get_fieldsets(self, request: HttpRequest, obj: Optional[User] = None):
        """
        Возвращает набор полей, отображаемых в форме админки.
        При создании объекта показывает отдельный набор полей.
        """
        if not obj:  # При создании пользователя
            return (
                (None, {'fields': ('username', 'password1', 'password2')}),
                ('Персональные данные', {'fields': ('email', 'phone')}),
                ('Группа', {'fields': ('groups',)})
            )
        return super().get_fieldsets(request, obj)

    @admin.display(description='Аватар')
    def avatar_preview(self, obj: User) -> str:
        """
        Возвращает HTML-код для отображения миниатюры аватара.
        """
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.avatar.url
            )
        return "—"

    @admin.display(description='Статус')
    def status_badge(self, obj: User) -> str:
        """
        Возвращает HTML-код с цветным бейджем, отображающим статус пользователя.
        """
        if obj.is_superuser:
            color = 'purple'
            text = 'Админ'
        elif obj.is_staff:
            color = 'blue'
            text = 'Персонал'
        else:
            color = 'green'
            text = 'Пользователь'

        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 6px; border-radius: 4px">{}</span>',
            color, text
        )

    @admin.display(description='Дата регистрации', ordering='date_joined')
    def date_joined_short(self, obj: User) -> str:
        """
        Возвращает дату регистрации пользователя в формате ДД.ММ.ГГГГ.
        """
        return obj.date_joined.strftime('%d.%m.%Y')


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    """
    Админка для модели UserGroup с ограничениями на изменение и добавление.
    """
    list_display = ('name', 'user_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    readonly_fields = ('users_in_group',)
    fields = ('name', 'permissions', 'users_in_group')

    @admin.display(description='Пользователей')
    def user_count(self, obj: UserGroup) -> int:
        """
        Возвращает количество пользователей в группе.
        """
        return obj.user_set.count()

    @admin.display(description='Пользователи в группе')
    def users_in_group(self, obj: UserGroup) -> str:
        """
        Возвращает HTML со списком пользователей в группе.
        """
        users = obj.user_set.all()
        if users:
            return format_html('<br>'.join([f"{user.username} ({user.get_full_name()})" for user in users]))
        return "Нет пользователей"

    def has_change_permission(self, request: HttpRequest, obj: Optional[UserGroup] = None) -> bool:
        """
        Запретить изменение групп через админку.
        """
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Запретить добавление новых групп.
        """
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[UserGroup] = None) -> bool:
        """
        Запретить удаление групп.
        """
        return False


# Настройки заголовков и титулов админки
admin.site.site_header = "Администрирование Sportswear Shop"
admin.site.site_title = "Sportswear Shop Admin"
admin.site.index_title = "Добро пожаловать в панель управления"
