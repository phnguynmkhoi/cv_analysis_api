from fastapi import Depends
from sqlalchemy.orm import Session
from functools import partial

from modules.db import create_get_db
from modules.crud import CRUD

from modules.ingestor import CV_Local_Ingestor, CV_GDrive_Ingestor
from modules.extractor import CVInformationExtractor
from modules.embedder import Embedder
from config.db_config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD
from config.db_config import QDRANT_HOST, QDRANT_PORT
from config.config import settings

get_db = create_get_db(
    username=POSTGRES_USERNAME,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    db=POSTGRES_DB
)
def get_crud_module(db: Session = Depends(get_db)):
    """
    Dependency to get the CRUD module with a database session.
    
    Parameters:
        db (Session): The database session.
    
    Returns:
        CRUD: The CRUD module instance.
    """
    return CRUD(db)

def get_local_ingestor():
    """
    Dependency to get the local CV ingestor.
    
    Returns:
        CV_Local_Ingestor: The local CV ingestor instance.
    """
    return CV_Local_Ingestor()

def get_gdrive_ingestor():
    """
    Dependency to get the Google Drive CV ingestor.
    
    Returns:
        CV_Google_Drive_Ingestor: The Google Drive CV ingestor instance.
    """
    return CV_GDrive_Ingestor()

def get_extractor():
    """
    Dependency to get the extractor for processing CV files.
    
    Returns:
        Extractor: The extractor instance.
    """
    return CVInformationExtractor(
        google_api_key=settings.GOOGLE_API_KEY,
    )

def get_embedder():
    """
    Dependency to get the embedder for processing CV files.
    Returns:
        Embedder: The embedder instance.
    """
    return Embedder(
        google_api_key=settings.GOOGLE_API_KEY,
        qdrant_host=QDRANT_HOST,
        qdrant_port=QDRANT_PORT
    )