from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class CVInformationExtractor:
    """
    Uses Gemini via LangChain to extract structured candidate information from raw CV text.
    """
    def __init__(self, google_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=google_api_key,
            model="gemini-2.0-flash-lite",
            temperature=0  # Update if using Gemini 1.5 or custom variant
        )
        
    def extract(self, cv_text: str) -> Dict[str, Any]:
        prompt_template = """
        You are an expert HR assistant. Extract structured data from the provided resume text.
        Return the result in JSON with the following fields:
        - name, email, phone (number, remove all the non-numeric characters except +)
        - summary (short summary of the candidate)
        - education (list of: institution, degree, field, start_date, end_date)
        - skills (list)
        - work_experience: list(years_of_experience (integer) + company + positions (title) + description): Return the total years of experience in each specific position. If empty, return 0 with the position title and other attributes is None.
        - total_work_experience (integer): Total years of work experience.
        - certifications (list of: title, date, description): Relevant certifications.
        - achievements (list of: title, date): Honours, awards, publications, etc.
        <Constraint> 
        - Only rely on the provided resume text.  
        - Do not make assumptions but you can infer information from the text and rewrite it more fluent.
        - Return in valid JSON format.
        - Summarize the projects and papers in a concise manner. Keep all the statistics and dates.
        - Only include the fields mentioned above.
        - work_experience_for_embedding must at least return 0 with the position title and other attributes as None if no work experience is found.
        - Do not include any additional information or explanations.
        - You can extract information from projects, certifications and rewrite them as skills with descriptions. Only extract the skills not the title of those.
        - Always return every field in the JSON with approriate field types even if they are empty.
        </Constraint>
        Resume text: {cv_text}
        """
        prompt = PromptTemplate(
                input_variables=["cv_text"],
                template= prompt_template
            )
        chain = prompt | self.llm | JsonOutputParser()
        response = chain.invoke({"cv_text": cv_text})
        return response
    
    def transform(self, cv_text: str) -> Dict[str, Any]:
        extracted_json = self.extract(cv_text)
        prompt_template = """
        You are an expert HR assistant. Given the extracted JSON data from a CV: {extracted_json}.
        Transform the extracted JSON data into following format:
        - name: Full name of the candidate.
        - email: Email address of the candidate.
        - phone: Phone number of the candidate (only numeric characters, keep +).
        - summary: Short summary of the candidate.
        - education: List of education details with institution, degree, field, start_date, end_date.
        - skills: skills (list, lowercase): extracted from skills, projects, achievements, certifications).
        - skills_description: str (write a description for skills that extracted from skills, projects, achievements, certifications)
        - years_of_experience: total_years_of_experience (integer).
        - work_description: str (write a description for all of the work experience combined include of role, description, time)
        Ensure that the output is valid JSON and includes all fields from the original extraction.
        <Constraint>
        - Only rely on the provided extracted JSON data.
        - Do not make assumptions but you can infer information from the text and rewrite it more fluent.
        - Return in valid JSON format.
        - Transform achievements and certifications as well as publications into skills and remove them from answer
        - Extract the skill more abstract as well as not duplicated
        - Do not include any key that is not mentioned above.
        </Constraint>
        """
        prompt = PromptTemplate(
            input_variables=["extracted_json"],
            template=prompt_template
        )
        chain = prompt | self.llm | JsonOutputParser()
        response = chain.invoke({
            "extracted_json": extracted_json
        })

        return response
    
    def extract_and_transform(self, cv_text: str) -> Dict[str, Any]:
        """
        Extracts and transforms CV information in one step.
        
        Parameters:
            cv_text (str): The raw text of the CV.
        
        Returns:
            dict: Transformed structured data from the CV.
        """
        print(f"Extracting data from CV...")
        extracted_data = self.extract(cv_text)
        print(f"Extract data sucessfully. Now transforming it...")
        # import time
        # time.sleep(15)
        transformed_data = self.transform(extracted_data)
        return transformed_data
    

if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    import os
    from ingestor import CV_Local_Ingestor
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    extractor = CVInformationExtractor(google_api_key)
    ingestor = CV_Local_Ingestor()
    response = ingestor.ingest("data/resume.pdf")
    raw_text = response['raw_text']
    # print(f"Raw text extracted from CV: {raw_text[:500]}...")  # Print first 500 chars for brevity
    response = extractor.extract_and_transform(raw_text)
    print(f"Transformed data: {response}")
    print(f"Type of response: {type(response)}")