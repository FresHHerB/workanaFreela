"""
Workana scraper service.
Handles all web scraping operations for Workana projects.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, TimeoutError, Page

from ..config import config

logger = logging.getLogger(__name__)

class WorkanaScraper:
    """Workana web scraper service."""

    def __init__(self):
        self.email = config.WORKANA_EMAIL
        self.password = config.WORKANA_PASSWORD

    async def scrape_projects(self) -> Dict[str, Any]:
        """
        Scrape projects from Workana.

        Returns:
            Dict containing status, data, and project count.
        """
        if not self.email or not self.password:
            return {
                "status": "error",
                "message": "Missing Workana credentials"
            }

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            page = await browser.new_page()

            try:
                # Login to Workana
                await self._login(page)

                # Navigate to target page and scrape projects
                projects_data = await self._scrape_project_list(page)

                return {
                    "status": "success",
                    "data": projects_data,
                    "total_projects": len(projects_data)
                }

            except Exception as e:
                logger.error(f"Scraping error: {str(e)}")
                return {
                    "status": "error",
                    "message": str(e)
                }
            finally:
                await browser.close()

    async def _login(self, page: Page) -> None:
        """Handle Workana login process."""
        await page.goto('https://www.workana.com/login', wait_until='networkidle')

        # Accept cookies if present
        try:
            await page.click('#onetrust-accept-btn-handler', timeout=5000)
            await asyncio.sleep(1)
        except TimeoutError:
            pass

        # Fill login form
        await page.type('#email-input', self.email)
        await page.type('#password-input', self.password)
        await page.click('button[name="submit"]')

        # Wait for successful login
        await page.wait_for_selector("a:has-text('Meus projetos')", timeout=20000)
        logger.info("Successfully logged in to Workana")

    async def _scrape_project_list(self, page: Page) -> List[Dict[str, Any]]:
        """Scrape the project list from Workana."""
        target_url = 'https://www.workana.com/jobs?language=en%2Cpt&query=automa%C3%A7%C3%A3o'
        await page.goto(target_url, wait_until='domcontentloaded')
        await page.wait_for_selector('#projects .project-item', timeout=15000)

        # Execute JavaScript to expand project descriptions and extract data
        projects_data = await page.evaluate('''
            async () => {
                const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

                // Expand all project descriptions
                const projects = document.querySelectorAll('.project-item.js-project');
                for (const project of projects) {
                    const expandLink = project.querySelector('.html-desc a.link');
                    if (expandLink) {
                        expandLink.click();
                        await sleep(300);
                    }
                }
                await sleep(2000);

                // Extract project data
                return Array.from(document.querySelectorAll('.project-item.js-project')).map(p => {
                    const title_element = p.querySelector('.project-title a');
                    const bids_element = p.querySelector('.bids');
                    const date_element = p.querySelector('.date');
                    const budget_element = p.querySelector('.budget .values span');
                    const contact_element = p.querySelector('span.bid');
                    const countryElement = p.querySelector('.country-name a');
                    const is_contacted = contact_element ? contact_element.innerText.includes('Em contato') : false;

                    let description = 'N/A';
                    const desc_element = p.querySelector('.html-desc.project-details');
                    if (desc_element) {
                        const clonedDesc = desc_element.cloneNode(true);
                        clonedDesc.querySelectorAll('a.link').forEach(link => link.remove());
                        description = clonedDesc.innerText.replace(/\\s+/g, ' ').trim();
                    }

                    return {
                        title: title_element ? title_element.innerText.trim() : null,
                        url: title_element ? title_element.href : null,
                        bids: bids_element ? bids_element.innerText.replace('Propostas:', '').trim() : null,
                        published_date: date_element ? date_element.innerText.replace('Publicado:', '').trim() : null,
                        budget: budget_element ? budget_element.innerText.trim() : null,
                        contacted: is_contacted,
                        description: description,
                        country: countryElement ? countryElement.innerText.trim() : 'N/A'
                    };
                });
            }
        ''')

        logger.info(f"Scraped {len(projects_data)} projects")
        return projects_data

# Create a singleton instance
scraper = WorkanaScraper()