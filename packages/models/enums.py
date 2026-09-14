from __future__ import annotations

from enum import StrEnum


class CompanyType(StrEnum):
    STARTUP = "startup"
    SCALEUP = "scaleup"
    NONPROFIT = "nonprofit"
    UNKNOWN = "unknown"


class FundingStage(StrEnum):
    BOOTSTRAPPED = "bootstrapped"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    GROWTH = "growth"
    UNKNOWN = "unknown"


class RemotePolicy(StrEnum):
    GLOBAL_REMOTE = "GLOBAL_REMOTE"
    REMOTE_FIRST = "REMOTE_FIRST"
    EUROPE_REMOTE = "EUROPE_REMOTE"
    EMEA_REMOTE = "EMEA_REMOTE"
    US_REMOTE = "US_REMOTE"
    COUNTRY_REMOTE = "COUNTRY_REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    UNKNOWN = "UNKNOWN"


class EmployeeRange(StrEnum):
    RANGE_1_10 = "1-10"
    RANGE_11_50 = "11-50"
    RANGE_51_100 = "51-100"
    RANGE_101_200 = "101-200"
    RANGE_201_500 = "201-500"
    RANGE_501_1000 = "501-1000"
    RANGE_1000_PLUS = "1000+"
    UNKNOWN = "unknown"


class BusinessModel(StrEnum):
    SAAS = "SaaS"
    B2B = "B2B"
    B2C = "B2C"
    MARKETPLACE = "Marketplace"
    DEVELOPER_TOOLS = "Developer Tools"
    INFRASTRUCTURE = "Infrastructure"
    API = "API"
    FINTECH = "FinTech"
    HEALTHTECH = "HealthTech"
    AI = "AI"
    WEB3 = "Web3"
    ROBOTICS = "Robotics"
    ECOMMERCE = "E-commerce"
    SECURITY = "Security"
    DATA = "Data"
    ENTERPRISE = "Enterprise"
    CONSUMER = "Consumer"


class EngineeringCategory(StrEnum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    MOBILE = "mobile"
    DEVOPS = "devops"
    SRE = "sre"
    PLATFORM = "platform"
    DATA = "data"
    MACHINE_LEARNING = "machine_learning"
    AI = "ai"
    SECURITY = "security"
    QA = "qa"
    ENGINEERING_MANAGEMENT = "engineering_management"
    OTHER = "other"


class InvestorType(StrEnum):
    VC = "vc"
    ANGEL = "angel"
    ACCELERATOR = "accelerator"
    CORPORATE = "corporate"
    PE = "pe"
    GOVERNMENT = "government"
    UNKNOWN = "unknown"


class ScrapeStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class HiringStatus(StrEnum):
    HIRING = "hiring"
    HIRING_ENGINEERS = "hiring_engineers"
    NOT_HIRING = "not_hiring"
    UNKNOWN = "unknown"
