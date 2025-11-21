"""URL scraper for fetching HTML content from Groww mutual fund pages."""
import requests
from typing import Optional
import time
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class URLScraper:
    """Scraper for fetching content from Groww URLs."""
    
    def __init__(self, delay: float = 2.0, timeout: int = 30, use_selenium: bool = True):
        """
        Initialize the scraper.
        
        Args:
            delay: Delay between requests in seconds (default: 2.0)
            timeout: Request timeout in seconds (default: 30)
            use_selenium: Use Selenium for JavaScript rendering (default: True)
        """
        self.delay = delay
        self.timeout = timeout
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        
        # Fallback to requests if Selenium not available
        if not self.use_selenium:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
        else:
            self._init_selenium()
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            print(f"Warning: Could not initialize Selenium: {e}")
            print("Falling back to requests (may not work for JavaScript-rendered content)")
            self.use_selenium = False
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            })
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and valid.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and accessible, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check URL format
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if 'groww.in' not in parsed.netloc:
                return False
            if '/mutual-funds/' not in parsed.path:
                return False
        except Exception:
            return False
        
        # Check if URL is accessible
        try:
            if self.use_selenium and self.driver:
                # For Selenium, we'll validate during fetch
                return True
            else:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                return response.status_code == 200
        except Exception:
            return False
    
    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL (with JavaScript rendering if using Selenium).
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if fetch fails
        """
        if not self.validate_url(url):
            print(f"Invalid or inaccessible URL: {url}")
            return None
        
        try:
            print(f"Fetching: {url}")
            
            if self.use_selenium and self.driver:
                # Use Selenium for JavaScript-rendered content
                self.driver.get(url)
                # Wait for page to load (wait for body or specific content)
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    # Additional wait for dynamic content
                    time.sleep(3)  # Wait for JavaScript to render
                except Exception:
                    pass  # Continue even if wait times out
                
                html = self.driver.page_source
                time.sleep(self.delay)
                return html
            else:
                # Fallback to requests
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                time.sleep(self.delay)
                return response.text
                
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def close(self):
        """Close the session/driver."""
        if self.use_selenium and self.driver:
            self.driver.quit()
        elif hasattr(self, 'session'):
            self.session.close()

