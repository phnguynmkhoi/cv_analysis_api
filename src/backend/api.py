from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import JSONResponse
import uuid

from modules.crud import CRUD
from modules.ingestor import CV_Local_Ingestor, CV_GDrive_Ingestor
from modules.extractor import CVInformationExtractor
from modules.embedder import Embedder
from modules.models import Person, Education, ResumeFile
from backend.dependencies import get_crud_module, get_local_ingestor, get_gdrive_ingestor, get_extractor, get_embedder
from backend.schema import CV_SearchRequest
router = APIRouter()

@router.get("/person/{person_id}")
async def get_person(
    person_id: int,
    crud_module: CRUD = Depends(get_crud_module),
):
    """
    Get a person by ID.
    
    Parameters:
        person_id (int): The ID of the person to retrieve.
    
    Returns:
        Person: The retrieved person record.
    """
    person = crud_module.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    education = crud_module.get_educations_by_person_id(person_id)
    resume_files = crud_module.get_resume_files_by_person_id(person_id)
    return JSONResponse(
        content={
            "person": person,
            "education": education,
            "resume_files": resume_files
        },
        status_code=200
    )

@router.post("/upload-cv")
async def upload_file(
    file: UploadFile = File(...),
    crud_module: CRUD = Depends(get_crud_module),
    ingestor: CV_Local_Ingestor = Depends(get_local_ingestor),
    extractor: CVInformationExtractor = Depends(get_extractor),
    embedder: Embedder = Depends(get_embedder),
):
    """
    Upload a file and create a new person record.
    
    Parameters:
        file (UploadFile): The file to upload.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    file_location = f"tmp/{uuid.uuid4()}_{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    ingested_data = ingestor.ingest(file_location)
    if not ingested_data:
        raise HTTPException(status_code=400, detail="Failed to ingest the file")
    
    raw_text = ingested_data["raw_text"]
    file_path = ingested_data["file_path"]
    extracted_data = extractor.extract_and_transform(raw_text)
    education = extracted_data.get("education", [])
    educations = [Education(
        institution=edu.get("institution", ""),
        degree=edu.get("degree", ""),
        field=edu.get("field", ""),
        start_date=edu.get("start_date", None),
        end_date=edu.get("end_date", None)
    ) for edu in education]
    resume_files = ResumeFile(
        filename=file.filename,
        storage_url=f"file://{file_path}",
        status="QUEUED"
    )
    person = Person(
        full_name=extracted_data.get("name", "Unknown"),
        email=extracted_data.get("email", ""),
        phone=extracted_data.get("phone", ""),
        summary=extracted_data.get("summary", "")
    )
    # Create person and resume files in the database
    person, _, resume_files = crud_module.create_person(
        person=person,
        educations=educations,
        resume_files=[resume_files]
    )

    payload = {
        "skills": extracted_data.get("skills", []),
        "years_of_experience": extracted_data.get("years_of_experience", 0),
        "skills_description": extracted_data.get("skills_description", ""),
        "work_description": extracted_data.get("work_description", "")
    }

    resume_file = resume_files[0]
    embedder.embed_cv(person_id=person.id, resume_id = resume_file.id, payload=payload)

    crud_module.update_resume_file_status(
        resume_file_id=resume_file.id,
        status="SUCCESS",
    )

    return JSONResponse(
        content={
            "message": "File uploaded successfully",
        },
        status_code=201
    )
    
# # Post a new file through Google Drive URL in the body
@router.post("/upload-cv-by-google-drive-url")
async def upload_by_google_drive_url(
    url: str = Body(..., embed=True, description="Google Drive URL of the file to upload"),
    ingestor: CV_GDrive_Ingestor = Depends(get_gdrive_ingestor),
    extractor: CVInformationExtractor = Depends(get_extractor),
    embedder: Embedder = Depends(get_embedder),
    crud_module: CRUD = Depends(get_crud_module)
):
    """
    Upload a file from Google Drive URL and create a new person record.
    
    Parameters:
        url (str): The Google Drive URL of the file to upload.

    """
    ingestor.download_file(url)
    ingested_data = ingestor.ingest(url)
    file_path = ingested_data["file_path"]
    raw_text = ingested_data["raw_text"]
    gdrive_url = ingested_data["gdrive_url"]
    extracted_data = extractor.extract_and_transform(raw_text)
    education = extracted_data.get("education", [])
    educations = [Education(
        institution=edu.get("institution", ""),
        degree=edu.get("degree", ""),
        field=edu.get("field", ""),
        start_date=edu.get("start_date", None),
        end_date=edu.get("end_date", None)
    ) for edu in education]
    resume_files = ResumeFile(
        filename=f"{file_path}",
        storage_url=gdrive_url, 
        status="QUEUED"
    )
    person = Person(
        full_name=extracted_data.get("name", "Unknown"),
        email=extracted_data.get("email", ""),
        phone=extracted_data.get("phone", ""),
        summary=extracted_data.get("summary", "")
    )
    # Create person and resume files in the database
    person, _, resume_files = crud_module.create_person(
        person=person,
        educations=educations,
        resume_files=[resume_files]
    )
    payload = {
        "skills": extracted_data.get("skills", []),
        "years_of_experience": extracted_data.get("years_of_experience", 0),        
        "skills_description": extracted_data.get("skills_description", ""),
        "work_description": extracted_data.get("work_description", "")
    }
    print(resume_files)
    resume_file = resume_files[0]
    embedder.embed_cv(person_id=person.id, resume_id = resume_file.id, payload=payload)
    crud_module.update_resume_file_status(
        resume_file_id=resume_file.id,
        status="SUCCESS",
    )
    return JSONResponse(
        content={
            "message": "File uploaded successfully",
        },
        status_code=201
    )

@router.post("/upload-cv-by-google-drive-folder-url")
async def upload_by_google_drive_folder_url(
    url: str = Body(..., embed=True, description="Google Drive folder URL of the files to upload"),
    ingestor: CV_GDrive_Ingestor = Depends(get_gdrive_ingestor),
    extractor: CVInformationExtractor = Depends(get_extractor),
    embedder: Embedder = Depends(get_embedder),
    crud_module: CRUD = Depends(get_crud_module)
):
    """
    Upload multiple files from a Google Drive folder URL and create new person records.
    
    Parameters:
        url (str): The Google Drive folder URL of the files to upload.
    """

    ingested_data = ingestor.ingest_folder(url)
    if not ingested_data:
        raise HTTPException(status_code=400, detail="Failed to ingest the files")
    
    for i, raw_text in enumerate(ingested_data["raw_texts"]):
        file_path = ingested_data["file_paths"][i]
        extracted_data = extractor.extract_and_transform(raw_text)
        if extracted_data.get("name") is None:
            continue
        education = extracted_data.get("education", [])
        educations = [Education(
            institution=edu.get("institution", ""),
            degree=edu.get("degree", ""),
            field=edu.get("field", ""),
            start_date=edu.get("start_date", None),
            end_date=edu.get("end_date", None)
        ) for edu in education]
        resume_files = ResumeFile(
            filename=f"{file_path}",
            storage_url=f"{ingested_data.get('gdrive_folder_url', '')}/{file_path}", 
            status="QUEUED"
        )
        person = Person(
            full_name=extracted_data.get("name", "Unknown"),
            email=extracted_data.get("email", ""),
            phone=extracted_data.get("phone", ""),
            summary=extracted_data.get("summary", "")
        )
        # Create person and resume files in the database
        person, _, resume_files = crud_module.create_person(
            person=person,
            educations=educations,
            resume_files=[resume_files]
        )
        payload = {
            "skills": extracted_data.get("skills", []),
            "years_of_experience": extracted_data.get("years_of_experience", 0),        
            "skills_description": extracted_data.get("skills_description", ""),
            "work_description": extracted_data.get("work_description", "")
        }
        resume_file = resume_files[0]
        embedder.embed_cv(person_id=person.id, resume_id = resume_file.id, payload=payload)
        crud_module.update_resume_file_status(
            resume_file_id=resume_file.id,
            status="SUCCESS",
        )

    return JSONResponse(
        content={
            "message": "Folder uploaded successfully",
        },
        status_code=201
    )

@router.post("/update-cv/{resume_id}")
async def update_cv(
    resume_id: int,
    file: UploadFile = File(..., description="New CV file to upload"),
    crud_module: CRUD = Depends(get_crud_module),
    ingestor: CV_Local_Ingestor = Depends(get_local_ingestor),
    extractor: CVInformationExtractor = Depends(get_extractor),
    embedder: Embedder = Depends(get_embedder),
):
    """
    Update a person's CV by uploading a new file.
    Parameters:
        resume_id (int): The ID of the resume file to update.
        file (UploadFile): The new CV file to upload.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_location = f"tmp/{uuid.uuid4()}_{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    ingested_data = ingestor.ingest(file_location)
    if not ingested_data:
        raise HTTPException(status_code=400, detail="Failed to ingest the file")
    
    raw_text = ingested_data["raw_text"]
    file_path = ingested_data["file_path"]
    extracted_data = extractor.extract_and_transform(raw_text)
    
    resume_file = crud_module.get_resume_file(resume_id)
    if not resume_file:
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    if resume_file.status != "SUCCESS":
        raise HTTPException(status_code=400, detail="Resume file is not in a valid state for update")
    # Update resume file details
    crud_module.update_resume_file_by_id(
        resume_file_id=resume_file.id,
        updates={
            "filename": file.filename,
            "storage_url": f"file://{file_path}",
            "status": "QUEUED"
        }
    )
    
    person = crud_module.get_person(resume_file.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    educations = extracted_data.get("education", [])
    educations = [Education(
        institution=edu.get("institution", ""),
        degree=edu.get("degree", ""),
        field=edu.get("field", ""),
        start_date=edu.get("start_date", None),
        end_date=edu.get("end_date", None)
    ) for edu in educations]
    # Update person and resume files in the database
    crud_module.update_person(
        person_id = person.id,
        updates = {
            "full_name": extracted_data.get("name", person.full_name),
            "email": extracted_data.get("email", person.email),
            "phone": extracted_data.get("phone", person.phone), 
            "summary": extracted_data.get("summary", person.summary)
        }
    )

    crud_module.update_education_by_person_id(
        person_id=person.id,
        educations=educations
    )
    payload = {
        "skills": extracted_data.get("skills", []),
        "years_of_experience": extracted_data.get("years_of_experience", 0),        
        "skills_description": extracted_data.get("skills_description", ""),
        "work_description": extracted_data.get("work_description", "")
    }
    embedder.embed_cv(person_id=person.id, resume_id = resume_file.id, payload=payload)
    crud_module.update_resume_file_status(
        resume_file_id=resume_file.id,
        status="SUCCESS",
    )
    return JSONResponse(
        content={
            "message": "CV updated successfully",
            "person_id": person.id,
            "resume_file_id": resume_file.id
        },
        status_code=200
    )

@router.post("/search-cv")
async def search_cv(
    payload: CV_SearchRequest = Body(..., embed=True, description="Search query for CVs"),
    embedder: Embedder = Depends(get_embedder),
    crud_module: CRUD = Depends(get_crud_module)                                    
):
    """
    Search for CVs based on a query.
    
    Parameters:
        query (str): The search query.
    
    Returns:
        list: A list of person records and resume files matching the search criteria.
    """
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    filter = {
        "skills": payload.skills or [],
        "years_of_experience": payload.years_of_experience or 0
    }
    results = embedder.search_with_filter(query=payload.query, limit=payload.limit, filter=filter)
    if not results:
        return JSONResponse(
            content={
                "message": "No CVs found",
                "results": []
            },
            status_code=200
        )
    
    person_ids = {point.payload["person_id"] for point in results}
    resume_ids = {point.id for point in results}
    response = [
        {"person_id": point.payload["person_id"], 
         "resume_id": point.id, 
         "person": crud_module.get_person(point.payload["person_id"]), 
         "resume_file": crud_module.get_resume_file(point.id)} 
        for point in results if point.payload["person_id"] in person_ids and point.id in resume_ids
    ]
    
    return JSONResponse(
        content={
            "message": "CVs found",
            "results": response,
        },
        status_code=200
    )

@router.delete("/delete-person/{person_id}")
async def delete_person(
    person_id: int,
    crud_module: CRUD = Depends(get_crud_module),
):
    """
    Delete a person by ID.
    
    Parameters:
        person_id (int): The ID of the person to delete.
    
    Returns:
        str: A success message.
    """
    person = crud_module.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    crud_module.delete_person(person_id)
    
    return JSONResponse(
        content={
            "message": "Person deleted successfully"
        },
        status_code=200
    )

@router.delete("/delete-resume-file/{resume_file_id}")
async def delete_resume_file(
    resume_file_id: int,
    crud_module: CRUD = Depends(get_crud_module),
):
    """
    Delete a resume file by its ID.
    
    Parameters:
        resume_file_id (int): The ID of the resume file to delete.
    
    Returns:
        str: A success message.
    """
    resume_file = crud_module.get_resume_file(resume_file_id)
    if not resume_file:
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    crud_module.delete_resume_file(resume_file_id)
    
    return JSONResponse(
        content={
            "message": "Resume file deleted successfully"
        },
        status_code=200
    )