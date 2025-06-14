from typing import Optional

from openai import OpenAI


class CustomizerService:
    """Service to customize resumes based on job descriptions using OpenAI's LLM API."""

    def __init__(self, model: str = "gpt-4.1", client: Optional[OpenAI] = None):
        """Create the service.

        Parameters
        ----------
        model:
            The OpenAI model to use when customizing.
        client:
            Optional pre-configured ``OpenAI`` client. If ``None`` the service
            operates in passthrough mode.
        """
        self.client = client
        self.instructions = (
            "You are an expert resume editor who can tailors resumes to specific job descriptions. "
            "Your output must be valid TOML format, and it must maintain the resume structure of the TOML provided. "
            "We have layout restrictions, so each section in your edits should be similar in length to the original."
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

Return only the complete TOML document with no additional explanation.
"""
        return prompt
