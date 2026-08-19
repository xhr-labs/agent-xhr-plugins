from enum import Enum


class Header(str, Enum):
    X_COMPANY_ID = "xhr-company-id"
    X_EMPLOYEE_ID = "xhr-employee-id"
