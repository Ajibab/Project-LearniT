from dataclasses import dataclass

TOKEN_TYPE = (
    ("PASSWORD_RESET", "PASSWORD_RESET"),
)

ROLE_CHOICE=(
    ("ADMIN","ADMIN"),
    ("CUSTOMER","CUSTOMER"),
)

@dataclass
class TokenEnum:
    PASSWORD_RESET="PASSWORD_RESET"

@dataclass
class SytemRoleEnum:
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"