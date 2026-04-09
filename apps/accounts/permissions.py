from .constants import Roles


def is_authenticated(user):
    return user and user.is_authenticated


def is_citizen(user):
    return (
        is_authenticated(user)
        and user.role
        and user.role.name == Roles.CITIZEN
    )


def is_municipal_admin(user):
    return (
        is_authenticated(user)
        and user.role
        and user.role.name == Roles.MUNICIPAL_ADMIN
    )


def is_super_admin(user):
    return (
        is_authenticated(user)
        and (
            user.is_superuser
            or (user.role and user.role.name == Roles.SUPER_ADMIN)
        )
    )


def is_admin_or_superadmin(user):
    return is_municipal_admin(user) or is_super_admin(user)
