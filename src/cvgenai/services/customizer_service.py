import os
from openai import OpenAI


class CustomizerService:
    def __init__(self):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get('OPENAI_API_KEY'),
        )

    def customize(self, resume_data, job_description, output_path=None):
        """
        Customize a resume based on a job description.

        Args:
            resume_data (dict): Resume data already parsed from TOML
            job_description (str): Job description text
            output_path (str, optional): Path to save the customized resume TOML file.
                                        If None, returns the customized resume as a dict.

        Returns:
            dict or str: Customized resume as a dict if output_path is None,
                        otherwise the path to the saved file
        """
        # Create the prompt for the LLM
        prompt = self._create_customization_prompt(resume_data, job_description)

        # Call the LLM to customize the resume
        response = self.client.responses.create(
            model="gpt-4o",
            instructions="You are an expert resume customizer that tailors resumes to specific job descriptions. You maintain the original structure and approximate length of the resume sections. Your output must be valid TOML format.",
            input=prompt
        )

        # Get the customized resume in TOML format
        customized_resume_toml = response.output_text

        # Save the customized resume if output_path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(customized_resume_toml)
            return output_path

        # Parse the TOML response back to a dictionary and return it
        # Since we need to return a dictionary and can't use tomli_w,
        # we'll have to let the LLM format its response as a Python dictionary
        return self._toml_to_dict(customized_resume_toml)

    def _create_customization_prompt(self, resume_data, job_description):
        """
        Create a prompt for the LLM to customize the resume.

        Args:
            resume_data (dict): Resume data already parsed from TOML
            job_description (str): Job description text

        Returns:
            str: Prompt for the LLM
        """
        # Convert the resume data to TOML format for better context
        resume_toml = self._dict_to_toml(resume_data)

        prompt = f"""
I need to customize the following resume in TOML format to better match this job description:

JOB DESCRIPTION:
{job_description}

CURRENT RESUME (TOML format):
{resume_toml}

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


    def _dict_to_toml(self, data, indent=0):
        """
        Convert a dictionary to TOML format string.

        Args:
            data (dict): Dictionary to convert
            indent (int): Current indentation level

        Returns:
            str: TOML formatted string
        """
        result = []

        for key, value in data.items():
            # Handle nested dictionaries
            if isinstance(value, dict):
                result.append(f"[{key}]")
                result.append(self._dict_to_toml(value, indent + 2))
            # Handle lists of dictionaries (for experience items)
            elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                for item in value:
                    result.append(f"[[{key}]]")
                    for sub_key, sub_value in item.items():
                        formatted_value = self._format_toml_value(sub_value)
                        result.append(f"{sub_key} = {formatted_value}")
                    result.append("")
            # Handle regular lists
            elif isinstance(value, list):
                formatted_list = [self._format_toml_value(item) for item in value]
                result.append(f"{key} = [{', '.join(formatted_list)}]")
            # Handle simple values
            else:
                formatted_value = self._format_toml_value(value)
                result.append(f"{key} = {formatted_value}")

        return "\n".join(result)


    @staticmethod
    def _format_toml_value(value):
        """
        Format a Python value as a TOML value.

        Args:
            value: The value to format

        Returns:
            str: Formatted TOML value
        """
        return f"'''{value}'''"
