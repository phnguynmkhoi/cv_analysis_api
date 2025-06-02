from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from modules.crud import CRUD
from modules.db import get_db
from modules.models import Person, Education, ResumeFile
from modules.ingestor import CV_Local_Ingestor, CV_Google_Drive_Ingestor

router = APIRouter()

@router.get("/person/{person_id}")
async def get_person(
    person_id: int
):
    """
    Get a person by ID.
    
    Parameters:
        person_id (int): The ID of the person to retrieve.
    
    Returns:
        Person: The retrieved person record.
    """
    raise NotImplementedError("Get person functionality is not implemented yet.")

@router.post("/upload-cv")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a file and create a new person record.
    
    Parameters:
        file (UploadFile): The file to upload.
    
    Returns:
        Person: The created person record.
    """
    raise NotImplementedError("File upload functionality is not implemented yet.")
    
# Post a new file through Google Drive URL in the body
@router.post("/upload-cv-by-google-drive-url")
async def upload_by_google_drive_url(
    url: str = Body(..., description="Google Drive URL of the file to upload")
    
):
    """
    Upload a file from Google Drive URL and create a new person record.
    
    Parameters:
        url (str): The Google Drive URL of the file to upload.
    
    Returns:
        Person: The created person record.
    """
    raise NotImplementedError("Google Drive URL upload functionality is not implemented yet.")

@router.post("/upload-cv-by-google-drive-folder-url")
async def upload_by_google_drive_folder_url(
    url: str = Body(..., description="Google Drive folder URL of the files to upload")
):
    """
    Upload multiple files from a Google Drive folder URL and create new person records.
    
    Parameters:
        url (str): The Google Drive folder URL of the files to upload.
    
    Returns:
        list: A list of created person records.
    """
    raise NotImplementedError("Google Drive folder URL upload functionality is not implemented yet.")

@router.post("/update-cv/{person_id}")
async def update_cv(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Update a person's CV by uploading a new file.
    
    Parameters:
        person_id (int): The ID of the person to update.
        file (UploadFile): The new CV file to upload.
    
    Returns:
        Person: The updated person record.
    """
    raise NotImplementedError("Update CV functionality is not implemented yet.")

@router.post("/update-cv-by-google-drive-url/{person_id}")
async def update_cv_by_google_drive_url(
    person_id: int,
    url: str = Body(..., description="Google Drive URL of the new CV file to upload"),
):
    """
    Update a person's CV by uploading a new file from Google Drive URL.
    
    Parameters:
        person_id (int): The ID of the person to update.
        url (str): The Google Drive URL of the new CV file to upload.
    
    Returns:
        Person: The updated person record.
    """
    raise NotImplementedError("Update CV by Google Drive URL functionality is not implemented yet.")

@router.post("/search-cv")
async def search_cv(
    payload: dict = Body(..., description="Search query for CVs"),
    db: Session = Depends(get_db),
):
    """
    Search for CVs based on a query.
    
    Parameters:
        query (str): The search query.
    
    Returns:
        list: A list of person records matching the search query.
    """
    raise NotImplementedError("Search CV functionality is not implemented yet.")

@router.post("/delete-cv/{person_id}")
async def delete_cv(
    person_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a person's CV by ID.
    
    Parameters:
        person_id (int): The ID of the person whose CV to delete.
    
    Returns:
        str: A success message.
    """
    raise NotImplementedError("Delete CV functionality is not implemented yet.")