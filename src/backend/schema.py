from pydantic import BaseModel, Field
from typing import Optional, List

class CV_SearchRequest(BaseModel):
    """
    Request model for CV search.
    """
    query: str = Field(..., description="Search query string")
    limit: Optional[int] = Field(5, description="Maximum number of results to return")
    skills: Optional[List[str]] = Field(None, description="List of required skills")
    years_of_experience: Optional[int] = Field(0, description="Minimum years of experience required")