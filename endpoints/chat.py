from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import Tool, create_tool_calling_agent, AgentExecutor
from langchain_community.chat_message_histories import SQLChatMessageHistory
import os

from modules import coin_market_cap
from tools import api

class Agent():
    def __init__(self) -> None:
        api_instance = api.API()
        self.llm = api_instance.llm_config()
        cmc_instance = coin_market_cap.api_list()
        
        self.tools = [
            Tool(
                name='categories',
                func=lambda *args: cmc_instance.categories(),
                description="""Returns information about all coin categories/naratives available on CoinMarketCap.
                            Includes a paginated list of cryptocurrency quotes and metadata from each category.
                            this tool can be used for narrative analysis""",
            ),
            Tool(
                name='category',
                func=cmc_instance.category,
                description="""Returns information about a single coin category on CoinMarketCap.
                            Requires category ID as input. Returns cryptocurrency quotes and metadata for that category.
                            you can find the input_id from categories tool""",
            ),
            Tool(
                name='fear_and_greed_latest',
                func=lambda *args: cmc_instance.fearngreed_latest(),
                description="Returns the latest CMC Crypto Fear and Greed Index value.",
            ),
            Tool(
                name='fear_and_greed_historical',
                func=cmc_instance.fearngreed_historical,
                description="""Returns historical CMC Crypto Fear and Greed values at 12am UTC.
                            Requires limit parameter to specify number of historical entries.""",
            ),
            Tool(
                name='crypto_metadata',
                func=cmc_instance.metadata,
                description="""Returns static metadata for cryptocurrencies including logo, description,
                            website URL, social links, and technical documentation. Requires crypto symbol as input.""",
            ),
            Tool(
                name='market_metrics',
                func=lambda *args: cmc_instance.metrics_latest(),
                description="Returns the latest global cryptocurrency market metrics.",
            ),
            Tool(
                name='cmc_top_100',
                func=cmc_instance.top100,
                description="Returns the latest CoinMarketCap 100 Index value, constituents, and their weights.",
            ),
            Tool(
                name='current_price',
                func=cmc_instance.current_price,
                description="return the latest price of 1 amount of cryptocurrency"
            )
        ]
        self.prompt_template = """You are a professional cryptocurrency market data analyst assistant. Your responses must be based SOLELY on the data provided through the CoinMarketCap tools available to you.

        CORE RESPONSIBILITIES:
        1. Provide market analysis using ONLY the data from CoinMarketCap tools
        2. Always cite specific metrics and data points in your responses
        3. When analyzing trends, use concrete numbers and percentages
        4. If data is not available through the tools, explicitly state "I cannot provide that information as it's not available through my current tools"
        5. YOU MUST USE AT LEAST ONE TOOL FOR EVERY RESPONSE - never respond without checking current data

        RESPONSE STRUCTURE:
        1. Use relevant tools to gather current market data
        2. Present the specific data points obtained from tools
        3. Provide analysis based purely on the retrieved data
        4. Conclude with data-backed insights

        STRICT GUIDELINES:
        - Never make price predictions
        - Never give financial advice
        - Never use historical knowledge not provided by the tools
        - If multiple tools are needed, clearly separate the data from each tool
        - NEVER respond without using at least one tool"""

        self.persona = """You are Satoshi, a data-driven cryptocurrency market analyst. You communicate primarily in Indonesian, but can respond in other languages when requested. Your responses should be formal, professional, and strictly based on CoinMarketCap data."""
        
        self.rules = """CRITICAL RULES:
        1. MANDATORY: Use at least one tool call for EVERY user question - no exceptions
        2. ALWAYS use tool calls to fetch real-time data - never rely on base knowledge
        3. Before making any statement about crypto markets, verify it with tool data
        4. If asked about topics beyond CoinMarketCap data scope, respond with "Maaf, saya hanya dapat memberikan informasi berdasarkan data CoinMarketCap yang tersedia"
        5. For any market analysis, minimum use 2 different tools to provide comprehensive data
        6. Always specify timestamps for any market data provided
        7. If you cannot determine which tool to use, default to checking market_metrics
        8. Change the time to WIB        
        """
         
        # Create database directory if it doesn't exist
        db_dir = "data"
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.db_path = os.path.join(db_dir, "chat_history.db")
        
    def agent(self, user_input):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt_template),
            ("system", self.persona),
            ("system", self.rules),
            MessagesPlaceholder(variable_name='history'),
            ("user", f"{user_input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

        agent_with_history = RunnableWithMessageHistory(
            agent_executor,
            lambda sid: SQLChatMessageHistory(
                session_id = sid,
                connection_string = f"sqlite:///{self.db_path}",
            ),
            input_messages_key="user_input",
            history_messages_key="history",
        )

        return agent_with_history
