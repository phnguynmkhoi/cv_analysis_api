from sqlalchemy.orm import Session
from sqlalchemy import select

from modules.models import Person, Education, ResumeFile

class CRUD:
    """
    CRUD operations for Person, Education, and ResumeFile models.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def create_person(self, person: Person, educations: list[Education] = None, resume_files: list[ResumeFile] = None) -> Person:
        """
        Create a new person with optional educations and resume files.
        """
        person.email = person.email.lower()  # Normalize email to lowercase
        existing_person = self.get_person_by_email(person.email)
        if existing_person:
            # get the union of existing educations and resume files not duplicated
            educations = existing_person.educations + (educations or [])
            new_resume_files = existing_person.resume_files + (resume_files or [])
            # remove duplicates based on institution and field and degree for educations
            educations = list({(edu.institution, edu.field, edu.degree): edu for edu in educations}.values())
            # update the existing person
            existing_person.educations = educations
            existing_person.resume_files = new_resume_files
            self.db.commit()
            self.db.refresh(existing_person)
            return existing_person, educations, resume_files
        
        person.educations = educations or []
        person.resume_files = resume_files or []
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person, educations, resume_files
    
    def add_education(self, person_id: int, education: Education) -> Education:
        """
        Add an education record for a person.
        """
        person = self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        education.person_id = person_id
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education
    
    def add_resume_file(self, person_id: int, resume_file: ResumeFile) -> ResumeFile:
        """
        Add a resume file for a person.
        """
        person = self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        resume_file.person_id = person_id
        self.db.add(resume_file)
        self.db.commit()
        self.db.refresh(resume_file)
        return resume_file
    
    def get_person(self, person_id: int) -> Person:
        """
        Retrieve a person by ID.
        """
        return self.db.get(Person, person_id)
    
    def get_educations_by_person_id(self, person_id: int) -> list[Education]:
        """
        Retrieve all educations for a person by their ID.
        """
        return self.db.execute(
            select(Education).where(Education.person_id == person_id)
        ).scalars().all()
    
    def get_resume_files_by_person_id(self, person_id: int) -> list[ResumeFile]:
        """
        Retrieve all resume files for a person by their ID.
        """
        return self.db.execute(
            select(ResumeFile).where(ResumeFile.person_id == person_id)
        ).scalars().all()
    
    def update_person(self, person_id: int, updates: dict) -> Person:
        """
        Update a person's details.
        """
        person = self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        for key, value in updates.items():
            setattr(person, key, value)
        
        self.db.commit()
        self.db.refresh(person)
        return person
    
    def update_education(self, education_id: int, updates: dict) -> Education:
        """
        Update an education record by its ID.
        """
        education = self.db.get(Education, education_id)
        if not education:
            raise ValueError("Education not found")
        
        for key, value in updates.items():
            setattr(education, key, value)
        
        self.db.commit()
        self.db.refresh(education)
        return education
    
    def update_education_by_person_id(self, person_id: int, educations: list[Education]) -> Person:
        """
        Update a person's educations.
        """
        person = self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        # Remove duplicates based on institution, field, and degree
        educations = list({(edu.institution, edu.field, edu.degree): edu for edu in educations}.values())
        # Clear existing educations
        person.educations.clear()
        # Add new educations
        for edu in educations:
            edu.person_id = person_id
            person.educations.append(edu)
        # Commit changes
        self.db.commit()
        self.db.refresh(person)
        return person
    
    def update_resume_file_by_id(self, resume_file_id: int, updates: dict) -> ResumeFile:
        """
        Update a resume file by its ID.
        """
        resume_file = self.db.get(ResumeFile, resume_file_id)
        if not resume_file:
            raise ValueError("Resume file not found")
        
        for key, value in updates.items():
            setattr(resume_file, key, value)
        
        self.db.commit()
        self.db.refresh(resume_file)
        return resume_file
    
    def update_resume_file_status(self, resume_file_id: int, status: str) -> ResumeFile:
        """
        Update the status of a resume file.
        """
        resume_file = self.db.get(ResumeFile, resume_file_id)
        if not resume_file:
            raise ValueError("Resume file not found")
        
        resume_file.status = status
        self.db.commit()
        self.db.refresh(resume_file)
        return resume_file
    
    def delete_person(self, person_id: int) -> None:
        """
        Delete a person by ID.
        """
        person = self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        # Delete associated educations and resume files
        for education in person.educations:
            self.db.delete(education)
        for resume_file in person.resume_files:
            self.db.delete(resume_file)
        
        self.db.delete(person)
        self.db.commit()
    
    def delete_education(self, education_id: int) -> None:
        """
        Delete an education record by its ID.
        """
        education = self.db.get(Education, education_id)
        if not education:
            raise ValueError("Education not found")
        
        self.db.delete(education)
        self.db.commit()

    def delete_resume_file(self, resume_file_id: int) -> None:
        """
        Delete a resume file by its ID.
        """
        resume_file = self.db.get(ResumeFile, resume_file_id)
        if not resume_file:
            raise ValueError("Resume file not found")
        
        self.db.delete(resume_file)
        self.db.commit()

def main():
    pass