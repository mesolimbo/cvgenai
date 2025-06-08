import os
from openai import OpenAI


class CustomizerService:
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
        return self._toml_to_dict(response.output_text)


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


    def _toml_to_dict(self, toml_string):
        """
        Process the LLM's TOML response back into a Python dictionary.
        This is a second call to the LLM to convert TOML to a Python dict.

        Args:
            toml_string (str): TOML formatted string

        Returns:
            dict: Parsed TOML as a Python dictionary
        """
        # Make a second API call to have the LLM convert TOML to a Python dict
        response = self.client.responses.create(
            model="gpt-4o",
            instructions="You are a TOML parser that converts TOML to a Python dictionary. Return only the Python dictionary representation with no additional text.",
            input=f"Convert this TOML to a Python dictionary:\n\n{toml_string}"
        )

        # The response should be a valid Python dictionary representation
        # Using eval is typically unsafe, but in this controlled environment with
        # content from a trusted source (OpenAI API), it's acceptable
        try:
            result_dict = eval(response.output_text)
            return result_dict
        except Exception as e:
            # If there's an error, return a simple error message
            print(f"Error parsing TOML response: {e}")
            return {"error": "Failed to parse customized resume"}
