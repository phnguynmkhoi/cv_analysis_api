from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Person, Education, ResumeFile
from db import get_db
class CRUD:
    """
    CRUD operations for Person, Education, and ResumeFile models.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_person(self, person: Person, educations: list[Education] = None, resume_files: list[ResumeFile] = None) -> Person:
        """
        Create a new person with optional educations and resume files.
        """
        person.educations = educations or []
        person.resume_files = resume_files or []
        self.db.add(person)
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def get_person(self, person_id: int) -> Person:
        """
        Retrieve a person by ID.
        """
        return await self.db.get(Person, person_id)
    
    async def get_person_by_email(self, email: str) -> Person:
        """
        Retrieve a person by email.
        """
        return await self.db.execute(
            select(Person).where(Person.email == email)
        ).scalar_one_or_none()
    
    async def get_educations_by_person_id(self, person_id: int) -> list[Education]:
        """
        Retrieve all educations for a person by their ID.
        """
        return await self.db.execute(
            select(Education).where(Education.person_id == person_id)
        ).scalars().all()

    async def get_educations_by_person_email(self, email: str) -> list[Education]:
        """
        Retrieve all educations for a person by their email.
        """
        return await self.db.execute(
            select(Education).join(Person).where(Person.email == email)
        ).scalars().all()
    
    async def get_resume_files_by_person_id(self, person_id: int) -> list[ResumeFile]:
        """
        Retrieve all resume files for a person by their ID.
        """
        return await self.db.execute(
            select(ResumeFile).where(ResumeFile.person_id == person_id)
        ).scalars().all()
    
    async def get_resume_files_by_person_email(self, email: str) -> list[ResumeFile]:
        """
        Retrieve all resume files for a person by their email.
        """
        return await self.db.execute(
            select(ResumeFile).join(Person).where(Person.email == email)
        ).scalars().all()
    
    async def update_person(self, person_id: int, updates: dict) -> Person:
        """
        Update a person's details.
        """
        person = await self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        for key, value in updates.items():
            setattr(person, key, value)
        
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def update_person_by_email(self, email: str, updates: dict) -> Person:
        """
        Update a person's details by email.
        """
        person = await self.get_person_by_email(email)
        if not person:
            raise ValueError("Person not found")
        
        for key, value in updates.items():
            setattr(person, key, value)
        
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def update_person_educations(self, person_id: int, educations: list[Education]) -> Person:
        """
        Update a person's educations.
        """
        person = await self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        person.educations = educations
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def update_person_educations_by_email(self, email: str, educations: list[Education]) -> Person:
        """
        Update a person's educations by email.
        """
        person = await self.get_person_by_email(email)
        if not person:
            raise ValueError("Person not found")
        
        person.educations = educations
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def update_person_resume_files(self, person_id: int, resume_files: list[ResumeFile]) -> Person:
        """
        Update a person's resume files.
        """
        person = await self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        person.resume_files = resume_files
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def update_person_resume_files_by_email(self, email: str, resume_files: list[ResumeFile]) -> Person:
        """
        Update a person's resume files by email.
        """
        person = await self.get_person_by_email(email)
        if not person:
            raise ValueError("Person not found")
        
        person.resume_files = resume_files
        await self.db.commit()
        await self.db.refresh(person)
        return person
    
    async def delete_person(self, person_id: int) -> None:
        """
        Delete a person by ID.
        """
        person = await self.get_person(person_id)
        if not person:
            raise ValueError("Person not found")
        
        await self.db.delete(person)
        await self.db.commit()

async def main():
    from functools import partial
    from db import get_db
    
    db = partial(
        get_db,
        username="admin",
        password="example",
        host="localhost:5432",
        db="cv_db"
    )
    print("Starting CRUD operations...")
    async with db() as session:
        crud = CRUD(session)
        
        # Example usage
        new_person = Person(full_name="John Doe", email="pnmk0811@gmail.com", phone="1234567890", summary="Software Engineer")
        education = Education(institution="University A", degree="BSc", field="Computer Science", start_date=None, end_date=None)
        resume_file = ResumeFile(filename="resume.pdf", storage_url="/path/to/resume.pdf", status="QUEUED")
        created_person = await crud.create_person(new_person, [education], [resume_file])
        print(f"Created Person: {created_person.full_name}, Email: {created_person.email}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())