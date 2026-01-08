from pydantic import BaseModel
from typing import List, Optional


class APIResponse(BaseModel):
    """API Response schema."""
    id: int
    name: str
    assumption: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Application Response schema."""
    id: int
    name: str
    apis: List[APIResponse] = []

    class Config:
        from_attributes = True


class DataEntityResponse(BaseModel):
    """Data Entity Response schema."""
    id: int
    name: str
    applications: List[ApplicationResponse] = []

    class Config:
        from_attributes = True


class SubProcessResponse(BaseModel):
    """Sub-Process Response schema."""
    id: int
    name: str
    description: Optional[str] = None
    process_level: Optional[str] = None
    process_category: Optional[str] = None
    data_entities: List[DataEntityResponse] = []

    class Config:
        from_attributes = True


class ProcessResponse(BaseModel):
    """Process Response schema."""
    id: int
    name: str
    description: Optional[str] = None
    sub_processes: List[SubProcessResponse] = []

    class Config:
        from_attributes = True


class CapabilityDetailResponse(BaseModel):
    """Capability Detail Response schema - main response for capability query."""
    id: int
    name: str
    description: Optional[str] = None
    goal: str
    vertical: str
    sub_vertical: str
    processes: List[ProcessResponse] = []

    class Config:
        from_attributes = True


class CapabilitySimpleResponse(BaseModel):
    """Simple capability response for list."""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
