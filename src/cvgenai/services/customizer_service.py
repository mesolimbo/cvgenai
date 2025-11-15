import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI


class CustomizerService:
    """Service to customize resumes based on job descriptions using OpenAI's LLM API."""

    def __init__(self, model: str = "gpt-5.1", client: Optional[OpenAI] = None):
        """Create the service.

        Parameters
        ----------
        model:
            The OpenAI model to use when customizing.
        client:
            Optional pre-configured ``OpenAI`` client. If ``None`` the service
            operates in passthrough mode.
        """
        # Initialize the OpenAI client if not provided and environment variable is set
        load_dotenv()
        key = os.environ.get('OPENAI_API_KEY')
        if client is None and key:
            self.client = OpenAI(
                # This is the default and can be omitted
                api_key=key,
            )
        else:
            self.client = client

        self.instructions = (
            "You are an expert resume editor who can tailors resumes to specific job descriptions. "
            "Your output must be valid TOML format, and it must maintain the resume structure of the TOML provided. "
            "We have very strict layout restrictions, so each sentence/line you modify should be nearly identical in length to the original sentence. You must also keep the length of lists the same, so if you add a new item to a list, you must also remove an item from the list. "
            "You must preserve all the original whitespace and empty lines in the document. "
            "Please do not wrap the content in ```toml and ``` and that will not be parseable. "
            "Under no circumstance may you change job titles or dates, as that information must remain a valid verifiable reference. "
            "The [skills] section is provided for your reference only, so that you may better tailor the content of the cover letter and resume. "
            "Be sure to identify the company name and open role in the JOB DESCRIPTION section, so that you may reference them in the cover letter body (do not change the recepient however). "
        )
        self.model = model


    def customize(self, resume_text: str, job_description: str) -> str:
        """Customize a resume based on a job description.

        Parameters
        ----------
        resume_text:
            TOML formatted resume text.
        job_description:
            Job description text used for customization.

        Returns
        -------
        str
            Customized resume as TOML text.
        """
        if self.client is None:
            return resume_text
        prompt = self._create_customization_prompt(resume_text, job_description)
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=prompt,
        )
        return response.output_text


    @staticmethod
    def _create_customization_prompt(resume_text: str, job_description: str) -> str:
        """
        Create a prompt for the LLM to customize the resume.

        Args:
            resume_text (str): Resume data in TOML format
            job_description (str): Job description text

        Returns:
            str: Prompt for the LLM
        """
        prompt = f"""
I need to customize the following resume in TOML format to better match this job description:

JOB DESCRIPTION:
{job_description}

CURRENT RESUME (TOML format):
{resume_text}

Please provide a customized version of this resume that:
1. Highlights skills and experiences most relevant to the job description
2. Adjusts the wording in the summary and experience sections to better align with the job requirements
3. Prioritizes the most relevant areas of expertise and skills
4. Maintains approximately the same length for each section
5. Preserves the original structure and format

Return only the complete TOML document with no additional explanation or non-TOML mark-up.
"""
        return prompt
