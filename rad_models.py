from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class RadiationTherapyReport(BaseModel):
    """
    A Pydantic model to represent a patient's radiation therapy report.
    """
    patient_name: str = Field(..., description="Name of the patient")
    test_therapy: str = Field(..., description="The type of test or therapy, e.g., 'therapy'.")
    radiation_type: str = Field(..., description="The specific type of radiation therapy, e.g., 'EBRT'.")
    start_date: date = Field(..., description="The start date of the radiation therapy.")
    end_date: date = Field(..., description="The end date of the radiation therapy.")
    fractions: int = Field(..., description="The number of fractions administered.")
    dosage: float = Field(..., description="The total dosage of radiation.")
    unit: str = Field(..., description="The unit of the dosage, e.g., 'GY'.")
    area_treated: str = Field(..., description="The anatomical area treated, e.g., 'Spine'.")
    events: Optional[str] = Field(None, description="Any adverse events noted during therapy.")
    medication: Optional[str] = Field(None, description="Medication given for adverse events.")
    lab_name: str = Field(..., description="Name of the hospital or laboratory.")
    lab_location: str = Field(..., description="Location of the hospital or laboratory.")
    comment: Optional[str] = Field(None, description="General comments about the therapy.")