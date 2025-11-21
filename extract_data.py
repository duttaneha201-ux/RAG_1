"""Main script to extract data from Groww mutual fund URLs."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.url_scraper import URLScraper
from src.scraper.data_extractor import DataExtractor
from src.scraper.data_storage import DataStorage
from src.utils.config import load_urls_config, validate_url


def extract_all_data():
    """Extract data from all configured URLs."""
    print("=" * 60)
    print("HDFC Mutual Fund Data Extraction")
    print("=" * 60)
    
    # Load configuration
    try:
        schemes = load_urls_config()
        print(f"\nLoaded {len(schemes)} schemes from configuration")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Initialize components
    scraper = URLScraper(delay=2.0)
    extractor = DataExtractor()
    storage = DataStorage()
    
    all_extracted_data = []
    success_count = 0
    failure_count = 0
    
    # Process each scheme
    for idx, scheme in enumerate(schemes, 1):
        url = scheme['url']
        scheme_name = scheme['name']
        category = scheme['category']
        
        print(f"\n[{idx}/{len(schemes)}] Processing: {scheme_name}")
        print(f"URL: {url}")
        
        # Validate URL
        if not validate_url(url):
            print(f"[ERROR] Invalid URL format: {url}")
            failure_count += 1
            continue
        
        # Fetch HTML
        html = scraper.fetch_html(url)
        if not html:
            print(f"[ERROR] Failed to fetch HTML from: {url}")
            failure_count += 1
            continue
        
        # Save raw HTML
        raw_file = storage.save_raw_html(url, html)
        print(f"[OK] Saved raw HTML: {raw_file}")
        
        # Extract data
        try:
            extracted_data = extractor.extract_data(html, url, scheme_name, category)
            
            # Validate extracted data
            if not extracted_data.get('source_url'):
                print(f"[ERROR] Missing source URL in extracted data")
                failure_count += 1
                continue
            
            # Print extracted data for validation
            print("\nExtracted Data:")
            print(f"  Expense Ratio: {extracted_data.get('expense_ratio', 'Not found')}")
            print(f"  Minimum SIP: {extracted_data.get('minimum_sip', 'Not found')}")
            print(f"  Exit Load: {extracted_data.get('exit_load', 'Not found')}")
            print(f"  NAV: {extracted_data.get('nav', 'Not found')}")
            print(f"  Tax Implication: {extracted_data.get('tax_implication', 'Not found')}")
            
            # Save extracted data
            processed_file = storage.save_extracted_data(extracted_data)
            print(f"[OK] Saved extracted data: {processed_file}")
            
            all_extracted_data.append(extracted_data)
            success_count += 1
            print(f"[OK] Successfully processed: {scheme_name}")
            
        except Exception as e:
            print(f"[ERROR] Error extracting data: {e}")
            import traceback
            traceback.print_exc()
            failure_count += 1
    
    # Save consolidated data
    if all_extracted_data:
        consolidated_file = storage.save_all_data(all_extracted_data)
        print(f"\n[OK] Saved consolidated data: {consolidated_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Extraction Summary")
    print("=" * 60)
    print(f"Total schemes: {len(schemes)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print("=" * 60)
    
    # Cleanup
    scraper.close()
    
    if failure_count > 0:
        print(f"\n[WARNING] {failure_count} scheme(s) failed to extract")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All schemes extracted successfully!")


if __name__ == "__main__":
    extract_all_data()

