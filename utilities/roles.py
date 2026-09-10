from enum import Enum


class RoleName(str, Enum):
    ADMIN = "admin"
    USER = "user"


# (role name, description) seed data — applied by the roles migration and
# used as the source of truth for the default role assigned at signup.
DEFAULT_ROLES = [
    (RoleName.ADMIN.value, "Full administrative access, including document management"),
    (RoleName.USER.value, "Standard authenticated user"),
]
