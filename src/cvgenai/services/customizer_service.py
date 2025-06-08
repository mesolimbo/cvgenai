import os
from openai import OpenAI


class CustomizerService:
    """Service to customize resumes based on job descriptions using OpenAI's LLM API."""

    def __init__(self, model="gpt-4.1"):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get('OPENAI_API_KEY'),
        )
        self.instructions = (
            "You are an expert resume editor who can tailors resumes to specific job descriptions. "
            "Your output must be valid TOML format, and it must maintain the resume structure of the TOML provided. "
            "We have layout restrictions, so each section in your edits should be similar in length to the original."
        )
        self.model = model


    def customize(self, resume_data, job_description):
        """
        Customize a resume based on a job description.

        Args:
            resume_data (dict): Resume data already parsed from TOML
            job_description (str): Job description text

        Returns:
            dict or str: Customized resume as a dict if output_path is None,
                        otherwise the path to the saved file
        """
        # Create the prompt for the LLM
        prompt = self._create_customization_prompt(resume_data, job_description)

        # Call the LLM to customize the resume
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=prompt
        )

       # Parse the TOML response back to a dictionary and return it
        # we'll have to let the LLM format its response as a Python dictionary
        return response.output_text


    @staticmethod
    def _create_customization_prompt(resume, job_description):
        """
        Create a prompt for the LLM to customize the resume.

        Args:
            resume (dict): Resume data already parsed from TOML
            job_description (str): Job description text

        Returns:
            str: Prompt for the LLM
        """
        prompt = f"""
I need to customize the following resume in TOML format to better match this job description:

JOB DESCRIPTION:
{job_description}

CURRENT RESUME (TOML format):
{resume}

Please provide a customized version of this resume that:
1. Highlights skills and experiences most relevant to the job description
2. Adjusts the wording in the summary and experience sections to better align with the job requirements
3. Prioritizes the most relevant areas of expertise and skills
4. Maintains approximately the same length for each section
5. Preserves the original structure and format

Return only the complete TOML document with no additional explanation.
"""
        return prompt
