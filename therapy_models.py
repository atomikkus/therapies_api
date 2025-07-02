from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class DrugAdministered(BaseModel):
    """A class to represent a single drug administered during therapy."""
    drug_name: str = Field(..., description="The name of the drug administered, e.g., 'Docetaxel'.")
    dosage: Optional[float] = Field(None, description="The dosage of the drug.")
    unit: Optional[str] = Field(None, description="The unit of the dosage, e.g., 'mg'.")

class TherapyReport(BaseModel):
    """
    A Pydantic model to represent a patient's chemotherapy, biological, or hormonal therapy report.
    """
    patient_id: str = Field(..., description="Unique identifier for the patient or report.")
    therapy_type: str = Field(..., description="The overall type of therapy, e.g., 'Chemotherapy', 'Targeted Therapy'.")
    administration_route: str = Field(..., description="The route of administration, e.g., 'Intravenous'.")
    drugs_administered: List[DrugAdministered] = Field(..., description="A list of drugs administered during the therapy.")
    first_date_of_therapy: date = Field(..., description="The start date of the first cycle of therapy.")
    number_of_cycles: int = Field(..., description="The number of therapy cycles administered.")
    cycle_interval_days: int = Field(..., description="The interval between cycles in days.")
    adverse_event_observed: bool = Field(..., description="Indicates if an adverse event was observed.")
    adverse_event_medication: Optional[str] = Field(None, description="Medication given for the adverse event.")
    comment: Optional[str] = Field(None, description="General comments about the therapy or patient's condition.")
    hospital_name: str = Field(..., description="Name of the hospital or laboratory.")
    hospital_location: str = Field(..., description="Location of the hospital or laboratory.")

