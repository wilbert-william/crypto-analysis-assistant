from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv
import os

class API():
    def __init__(self):
        # Load environment variables from .env file
        dotenv.load_dotenv()
        
        # Mengakses API key dari .env
        self.cmc_api_key = os.environ["CMC_API_KEY"]
        self.llm = os.environ["LLM_API"]
        self.model = 'gemini-2.0-flash'

    def cmc_api(self):
        return self.cmc_api_key

    def llm_config(self):
        llm = ChatGoogleGenerativeAI(
            api_key=self.llm,
            model=self.model
        )
        return llm
