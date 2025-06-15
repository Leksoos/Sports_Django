from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    """Создает стандартные группы пользователей при миграциях"""
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    # Базовые группы и их разрешения
    GROUPS = [
        {
            'name': 'Администраторы',
            'perms': [
                ('users', 'user', 'add'),
                ('users', 'user', 'change'),
                ('users', 'user', 'view'),
                ('users', 'user', 'delete'),
                ('shop', 'product', 'add'),
                ('shop', 'product', 'change'),
                ('shop', 'product', 'view'),
                ('shop', 'product', 'delete'),
                ('orders', 'order', 'add'),
                ('orders', 'order', 'change'),
                ('orders', 'order', 'view'),
                ('orders', 'order', 'delete'),
            ]
        },
        {
            'name': 'Менеджеры',
            'perms': [
                ('shop', 'product', 'add'),
                ('shop', 'product', 'change'),
                ('shop', 'product', 'view'),
                ('orders', 'order', 'add'),
                ('orders', 'order', 'change'),
                ('orders', 'order', 'view'),
                ('users', 'user', 'view'),
            ]
        },
        {
            'name': 'Пользователи',
            'perms': [
                ('shop', 'product', 'view'),
                ('orders', 'order', 'view'),  # Только свои заказы нужно проверять в view
            ]
        }
    ]
    
    for group in GROUPS:
        group_obj, created = Group.objects.get_or_create(name=group['name'])
        for app_label, model, perm in group['perms']:
            codename = f'{perm}_{model}'
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                permission = Permission.objects.get(content_type=ct, codename=codename)
                group_obj.permissions.add(permission)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                print(f'Разрешение {codename} не найдено для {app_label}.{model}')

def assign_default_group(sender, instance, created, **kwargs):
    """Назначает группу 'Пользователи' новым пользователям"""
    if created:
        from django.contrib.auth.models import Group
        group = Group.objects.get(name='Пользователи')
        instance.groups.add(group)

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)

        from django.db.models.signals import post_save
        from .models import User
        
        post_save.connect(assign_default_group, sender=User)