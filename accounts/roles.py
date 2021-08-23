from rolepermissions.roles import AbstractUserRole

permissions = {
    # Customers
    'list_customers': True,
    'create_customers': True,
    'update_customers': True,
    'export_customers': True,
    'delete_customers': True,
    'search_customers': True,

    # Motor Deals
    'list_motor_deals': True,
    'create_motor_deals': True,
    'update_motor_deals': True,
    'export_motor_deals': True,
    'delete_motor_deals': True,

    # Motor Quotes
    'list_motor_quotes': True,
    'create_motor_quotes': True,
    'update_motor_quotes': True,
    'delete_motor_quotes': True,
    'export_motor_quotes': True,

    # Motor Orders
    'create_motor_orders': True,
    'update_motor_orders': True,
    'void_motor_orders': True,

    # Motor Policies
    'list_motor_policies': True,
    'create_motor_policies': True,
    'update_motor_policies': True,
    'export_motor_policies': True,
    'import_motor_policies': True,

    # Tasks
    'list_tasks': True,
    'create_tasks': True,
    'update_tasks': True,
    'export_tasks': True,

    # Users/Agents
    'list_users': True,
    'create_users': True,
    'update_users': True,

    # Company Specific
    'company_settings': True,
    'company_dashboard': True,
}

user_not_allowed_to = {
    # Customers
    'export_customers': False,
    'delete_customers': False,

    # Deals
    'export_motor_deals': False,
    'delete_motor_deals': False,

    # Users/Agents
    'list_users': False,
    'create_users': False,
    'update_users': False,

    # Company Specific
    'company_settings': False,
}

producer_not_allowed_to = {
    # Customers
    'list_customers': False,
    'create_customers': False,
    'export_customers': False,
    'delete_customers': False,

    # Motor Deals
    'export_motor_deals': False,

    # Tasks
    'list_tasks': False,
    'create_tasks': False,
    'update_tasks': False,
    'export_tasks': False,

    # Users/Agents
    'list_users': False,
    'create_users': False,
    'update_users': False,

    # Company Specific
    'company_settings': False,
    'company_dashboard': False,
}


def get_role_permissions(permissions_not_allowed=None):
    if permissions_not_allowed is None:
        permissions_not_allowed = {}

    allowed_permissions = dict()

    for permission_name, allowed in dict(permissions, **permissions_not_allowed).items():
        if allowed:
            allowed_permissions[permission_name] = True

    return allowed_permissions


class User(AbstractUserRole):
    available_permissions = get_role_permissions(user_not_allowed_to)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Producer(AbstractUserRole):
    available_permissions = get_role_permissions(producer_not_allowed_to)

    class Meta:
        verbose_name = 'producer'
        verbose_name_plural = 'producers'


class Admin(AbstractUserRole):
    available_permissions = permissions

    class Meta:
        verbose_name = 'admin'
        verbose_name_plural = 'admins'
