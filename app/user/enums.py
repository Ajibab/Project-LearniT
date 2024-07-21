from dataclasses import dataclass

TOKEN_TYPE = (
    ("PASSWORD_RESET", "PASSWORD_RESET"),
)

ROLE_CHOICE=(
    ("INSTRUCTOR","INSTRUCTOR"),
    ("LEARNER","LEARNER"),
    ("LMS_ADMIN","LMS_ADMIN"),
    ("PLATFORM_ADMIN","PLATFORM_ADMIN"),
)

@dataclass
class TokenEnum:
    PASSWORD_RESET="PASSWORD_RESET"

@dataclass
class SytemRoleEnum:
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"

GENDER_OPTION = (("MALE", "MALE"), ("FEMALE","FEMALE"))
