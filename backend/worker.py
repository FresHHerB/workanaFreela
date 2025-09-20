import asyncio
import json
import logging
import os
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Workana Scraper API")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

EMAIL = os.getenv("WORKANA_EMAIL")
PASSWORD = os.getenv("WORKANA_PASSWORD")

async def scrape_and_return():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page()
        try:
            await page.goto('https://www.workana.com/login', wait_until='networkidle')
            try:
                await page.click('#onetrust-accept-btn-handler', timeout=5000)
                await asyncio.sleep(1)
            except TimeoutError:
                pass
            
            await page.type('#email-input', EMAIL)
            await page.type('#password-input', PASSWORD)
            await page.click('button[name="submit"]')
            await page.wait_for_selector("a:has-text('Meus projetos')", timeout=20000)
            
            target_url = 'https://www.workana.com/jobs?language=en%2Cpt&query=automa%C3%A7%C3%A3o'
            await page.goto(target_url, wait_until='domcontentloaded')
            await page.wait_for_selector('#projects .project-item', timeout=15000)
            
            projects_data = await page.evaluate('''
                async () => {
                    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
                    const projects = document.querySelectorAll('.project-item.js-project');
                    for (const project of projects) {
                        const expandLink = project.querySelector('.html-desc a.link');
                        if (expandLink) { 
                            expandLink.click(); 
                            await sleep(300); 
                        }
                    }
                    await sleep(2000);
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
            
            return {
                "status": "success", 
                "data": projects_data, 
                "total_projects": len(projects_data)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await browser.close()

@app.get("/")
async def root():
    return {"message": "Workana Scraper API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/scrape")
async def scrape_endpoint():
    result = await scrape_and_return()
    if result["status"] == "success":
        return result
    else:

        raise HTTPException(status_code=500, detail=result.get("message"))
