#crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain.tools import Tool
from .tools.custom_tool import CustomScrapingTool  # Use a relative import

def create_scraping_tool():
    """Create and return a langchain Tool instance for the scraping tool."""
    scraper = CustomScrapingTool()
    return Tool(
        name="product_scraper",
        func=scraper.scrape_product_data,
        description="Scrapes product information from e-commerce websites. Input should be a URL string."
    )

# Main Agent Class
@CrewBase
class EcommerceAgent():
    """Main agent class for e-commerce deal finding and analysis."""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize the agent with necessary tools."""
        self.search_tool = SerperDevTool()
        self.scraping_tool = create_scraping_tool()

    @agent
    def url_finder_agent(self) -> Agent:
        """Create an agent for finding relevant product URLs."""
        return Agent(
            config=self.agents_config['url_finder_agent'],
            tools=[self.search_tool],
            verbose=True
        )

    @agent
    def scraper_agent(self) -> Agent:
        """Create an agent for scraping product information."""
        return Agent(
            config=self.agents_config['scraper_agent'],
            tools=[self.scraping_tool],
            verbose=True
        )

    @agent
    def analyzer_agent(self) -> Agent:
        """Create an agent for analyzing product deals."""
        return Agent(
            config=self.agents_config['analyzer_agent'],
            verbose=True
        )

    @task
    def find_deal_urls(self) -> Task:
        """Task for finding product deal URLs."""
        return Task(
            config=self.tasks_config['find_deal_urls']
        )

    @task
    def scrape_deals(self) -> Task:
        """Task for scraping product deals."""
        return Task(
            config=self.tasks_config['scrape_deals']
        )

    @task
    def analyze_deals(self) -> Task:
        """Task for analyzing scraped deals."""
        return Task(
            config=self.tasks_config['analyze_deals']
        )

    @crew
    def crew(self) -> Crew:
        """Create and return the crew with all agents and tasks."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )