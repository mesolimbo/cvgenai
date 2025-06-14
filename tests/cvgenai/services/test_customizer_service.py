from unittest.mock import MagicMock, patch

from cvgenai.services.customizer_service import CustomizerService


class TestCustomizerService:
    @staticmethod
    @patch("os.environ.get", return_value=None)
    def test_customize_passthrough(*_):
        service = CustomizerService(client=None)
        resume = "name = 'Test'"
        result = service.customize(resume, "job")
        assert result == resume

    @staticmethod
    def test_customize_with_client():
        mock_response = MagicMock()
        mock_response.output_text = "name = 'custom'"
        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response

        service = CustomizerService(client=mock_client, model="gpt-test")
        resume = "name = 'Test'"
        job_desc = "desc"
        result = service.customize(resume, job_desc)

        expected_prompt = service._create_customization_prompt(resume, job_desc)
        mock_client.responses.create.assert_called_once_with(
            model="gpt-test",
            instructions=service.instructions,
            input=expected_prompt,
        )
        assert result == "name = 'custom'"
