"""
Mock data for the certificates app (since we're not using a database)
"""
from decimal import Decimal
import uuid
from datetime import datetime


class MockProject:
    def __init__(self, id, name_of_contractor, contract_no, vote_no, tender_sum):
        self.id = id
        self.name_of_contractor = name_of_contractor
        self.contract_no = contract_no
        self.vote_no = vote_no
        self.tender_sum = Decimal(str(tender_sum))
        self.created_at = datetime.now()


class MockCertificate:
    def __init__(self, id, project_id, currency, current_claim_excl_vat, previous_payment_excl_vat=0):
        self.id = id
        self.project_id = project_id
        self.currency = currency
        self.current_claim_excl_vat = Decimal(str(current_claim_excl_vat))
        self.vat_value = self.current_claim_excl_vat * Decimal('0.15')
        self.previous_payment_excl_vat = Decimal(str(previous_payment_excl_vat))
        self.created_at = datetime.now()


class MockCalculations:
    def __init__(self, certificate):
        self.certificate_id = certificate.id
        self.value_of_workdone_incl_vat = certificate.current_claim_excl_vat + certificate.vat_value
        self.total_value_of_workdone_excl_vat = certificate.current_claim_excl_vat
        self.retention = certificate.current_claim_excl_vat * Decimal('0.10')
        self.total_amount_payable = certificate.current_claim_excl_vat + certificate.vat_value - self.retention


# Mock data storage
MOCK_PROJECTS = [
    MockProject("1", "ABC Construction Ltd", "CON-2023-001", "V-2023-001", 500000.0),
    MockProject("2", "XYZ Builders Inc", "CON-2023-002", "V-2023-002", 750000.0),
    MockProject("3", "Mega Structures Co", "CON-2023-003", "V-2023-003", 1200000.0),
]

MOCK_CERTIFICATES = [
    MockCertificate("1", "1", "USD", 50000.0, 0.0),
    MockCertificate("2", "2", "ZIG", 100000.0, 50000.0),
]

MOCK_CALCULATIONS = {
    "1": MockCalculations(MOCK_CERTIFICATES[0]),
    "2": MockCalculations(MOCK_CERTIFICATES[1]),
}


def get_project_by_id(project_id):
    for project in MOCK_PROJECTS:
        if project.id == project_id:
            return project
    return None


def get_certificate_by_id(certificate_id):
    for certificate in MOCK_CERTIFICATES:
        if certificate.id == certificate_id:
            return certificate
    return None


def get_certificates_by_project_id(project_id):
    return [cert for cert in MOCK_CERTIFICATES if cert.project_id == project_id]


def get_calculations_by_certificate_id(certificate_id):
    return MOCK_CALCULATIONS.get(certificate_id)


def create_project(name_of_contractor, contract_no, vote_no, tender_sum):
    new_id = str(len(MOCK_PROJECTS) + 1)
    project = MockProject(new_id, name_of_contractor, contract_no, vote_no, tender_sum)
    MOCK_PROJECTS.append(project)
    return project


def create_certificate(project_id, currency, current_claim_excl_vat, previous_payment_excl_vat):
    new_id = str(len(MOCK_CERTIFICATES) + 1)
    certificate = MockCertificate(new_id, project_id, currency, current_claim_excl_vat, previous_payment_excl_vat)
    MOCK_CERTIFICATES.append(certificate)
    
    # Create calculations
    calculations = MockCalculations(certificate)
    MOCK_CALCULATIONS[new_id] = calculations
    
    return certificate
