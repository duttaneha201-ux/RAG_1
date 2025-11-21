"""Data extractor for parsing HTML and extracting mutual fund scheme data."""
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
from datetime import datetime


class DataExtractor:
    """Extract structured data from Groww mutual fund HTML pages."""
    
    def __init__(self):
        """Initialize the data extractor."""
        pass
    
    def extract_data(self, html: str, url: str, scheme_name: str, category: str) -> Dict:
        """
        Extract all required data fields from HTML.
        
        Args:
            html: HTML content from the page
            url: Source URL
            scheme_name: Name of the scheme
            category: Category of the scheme
            
        Returns:
            Dictionary containing extracted data
        """
        soup = BeautifulSoup(html, 'lxml')
        
        data = {
            'scheme_name': scheme_name,
            'category': category,
            'source_url': url,
            'expense_ratio': self._extract_expense_ratio(soup),
            'minimum_sip': self._extract_minimum_sip(soup),
            'exit_load': self._extract_exit_load(soup),
            'nav': self._extract_nav(soup),
            'tax_implication': self._extract_tax_implication(soup),
            'extracted_at': datetime.now().isoformat(),
        }
        
        return data
    
    def _extract_expense_ratio(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract expense ratio from the page."""
        # Look for expense ratio in various possible locations
        patterns = [
            r'expense\s+ratio[:\s]*([0-9.]+%?)',
            r'expense\s+ratio[:\s]*([0-9.]+\s*%)',
            r'([0-9.]+%?)\s*expense\s+ratio',
        ]
        
        # Search in text content
        text = soup.get_text(separator=' ', strip=True)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ratio = match.group(1).strip()
                # Ensure it has % if it's a percentage
                if '%' not in ratio and '.' in ratio:
                    ratio = f"{ratio}%"
                return ratio
        
        # Try to find in specific elements - look for divs/spans with expense ratio
        for element in soup.find_all(['div', 'span', 'p', 'td', 'li']):
            text_content = element.get_text(strip=True)
            if re.search(r'expense\s+ratio', text_content, re.I):
                # Look for percentage in the same element or nearby
                match = re.search(r'([0-9.]+%?)', text_content)
                if match:
                    ratio = match.group(1).strip()
                    if '%' not in ratio and '.' in ratio:
                        ratio = f"{ratio}%"
                    return ratio
                # Check next sibling
                if element.next_sibling:
                    next_text = element.next_sibling.get_text(strip=True) if hasattr(element.next_sibling, 'get_text') else str(element.next_sibling)
                    match = re.search(r'([0-9.]+%?)', next_text)
                    if match:
                        ratio = match.group(1).strip()
                        if '%' not in ratio and '.' in ratio:
                            ratio = f"{ratio}%"
                        return ratio
        
        return None
    
    def _extract_minimum_sip(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract minimum SIP amount from the page. Handles both ₹ and Rs. Format: ₹100"""
        # ₹ symbol (Unicode \u20b9) and Rs are equivalent
        patterns = [
            r'minimum\s+sip[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)',
            r'min\s+sip[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)',
            r'sip\s+minimum[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)',
            r'minimum\s+investment[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)',
            r'(?:₹|Rs?\.?)\s*([0-9,]+).*?minimum\s+sip',
        ]
        
        text = soup.get_text(separator=' ', strip=True)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                # Validate it's a reasonable SIP amount (typically 100-10000)
                try:
                    amount_int = int(amount)
                    if 50 <= amount_int <= 100000:
                        return f"Rs {amount}"
                except ValueError:
                    pass
        
        # Look for elements containing "Minimum SIP" or "SIP"
        for element in soup.find_all(['div', 'span', 'p', 'td', 'li']):
            text_content = element.get_text(strip=True)
            if re.search(r'minimum\s+sip|min\s+sip', text_content, re.I):
                # Look for ₹ or Rs amount in the same element - be more specific
                # Look for amount right after "minimum sip" or nearby
                match = re.search(r'minimum\s+sip[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)', text_content, re.I)
                if match:
                    amount = match.group(1).replace(',', '')
                    try:
                        amount_int = int(amount)
                        if 50 <= amount_int <= 100000:
                            return f"Rs {amount}"
                    except ValueError:
                        pass
                
                # Also check for standalone ₹ or Rs followed by number
                match = re.search(r'(?:₹|Rs?\.?)\s*([0-9]{2,5})', text_content, re.I)
                if match:
                    amount = match.group(1).replace(',', '')
                    try:
                        amount_int = int(amount)
                        if 50 <= amount_int <= 100000:
                            return f"Rs {amount}"
                    except ValueError:
                        pass
                
                # Check parent or next sibling
                if element.parent:
                    parent_text = element.parent.get_text(strip=True)
                    match = re.search(r'minimum\s+sip[:\s]*(?:₹|Rs?\.?)\s*([0-9,]+)', parent_text, re.I)
                    if match:
                        amount = match.group(1).replace(',', '')
                        try:
                            amount_int = int(amount)
                            if 50 <= amount_int <= 100000:
                                return f"Rs {amount}"
                        except ValueError:
                            pass
        
        return None
    
    def _extract_exit_load(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract exit load information from the page. Format: 'Exit load of 1% if redeemed within 1 year'."""
        patterns = [
            r'exit\s+load\s+of\s+([0-9.%]+)\s+if\s+redeemed\s+within\s+([0-9]+\s+year[s]?)',
            r'exit\s+load[:\s]*([0-9.%]+).*?redeemed.*?([0-9]+\s+year[s]?)',
            r'exit\s+load[:\s]*(.*?)(?:\.|\n|$)',
        ]
        
        text = soup.get_text(separator=' ', strip=True)
        
        # Look for "Exit load" text in elements - prioritize the specific format
        for element in soup.find_all(['div', 'span', 'p', 'td', 'li']):
            text_content = element.get_text(strip=True)
            if re.search(r'exit\s+load', text_content, re.I):
                # Try the specific format first: "Exit load of X% if redeemed within Y year"
                match = re.search(r'exit\s+load\s+of\s+([0-9.%]+)\s+if\s+redeemed\s+within\s+([0-9]+\s+year[s]?)', text_content, re.IGNORECASE)
                if match:
                    percentage = match.group(1)
                    period = match.group(2).strip()
                    # Clean up period (remove extra 's' or spaces, fix "yearS" -> "year")
                    period = re.sub(r'\s+', ' ', period)
                    period = re.sub(r'yearS+$', 'year', period, flags=re.I)
                    return f"Exit load of {percentage} if redeemed within {period}"
                
                # Extract the sentence/paragraph containing exit load
                match = re.search(r'exit\s+load[:\s]*(.*?)(?:\.|$)', text_content, re.IGNORECASE | re.DOTALL)
                if match:
                    load_info = match.group(1).strip()
                    load_info = re.sub(r'\s+', ' ', load_info)
                    # Clean up: remove trailing 'S' from "yearS"
                    load_info = re.sub(r'yearS+$', 'year', load_info, flags=re.I)
                    # Validate it's reasonable (contains % or number or time period)
                    if load_info and len(load_info) < 200 and (re.search(r'%|year|month|day', load_info, re.I) or len(load_info) > 10):
                        return load_info
                # If no match, get the full element text if it's short and contains exit load info
                if len(text_content) < 200 and re.search(r'exit\s+load', text_content, re.I):
                    cleaned = re.sub(r'\s+', ' ', text_content)
                    if len(cleaned) > 10 and re.search(r'%|year|month|day', cleaned, re.I):
                        return cleaned
        
        # Try pattern matching in full text
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                if len(match.groups()) == 2:
                    # Specific format matched
                    percentage = match.group(1)
                    period = match.group(2)
                    return f"Exit load of {percentage} if redeemed within {period}"
                else:
                    load_info = match.group(1).strip()
                    load_info = re.sub(r'\s+', ' ', load_info)
                    # Clean up: remove trailing 'S' from "yearS"
                    load_info = re.sub(r'yearS+$', 'year', load_info, flags=re.I)
                    if load_info and len(load_info) < 200 and len(load_info) > 5:
                        return load_info
        
        return None
    
    def _extract_nav(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract NAV (Net Asset Value) from the page. Handles both ₹ and Rs. Format: ₹ 2273.63"""
        # ₹ symbol (Unicode \u20b9) and Rs are equivalent
        patterns = [
            r'nav[:\s]*(?:₹|Rs?\.?)\s*([0-9,.]+)',
            r'net\s+asset\s+value[:\s]*(?:₹|Rs?\.?)\s*([0-9,.]+)',
            r'current\s+nav[:\s]*(?:₹|Rs?\.?)\s*([0-9,.]+)',
        ]
        
        text = soup.get_text(separator=' ', strip=True)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nav_value = match.group(1).replace(',', '')
                # Validate it's a reasonable NAV (typically 10-10000 for equity funds)
                try:
                    nav_float = float(nav_value)
                    if 1 <= nav_float <= 100000:  # Expanded range
                        return f"Rs {nav_value}"
                except ValueError:
                    pass
        
        # Look for NAV in specific elements - often in large numbers or price displays
        for element in soup.find_all(['div', 'span', 'h1', 'h2', 'h3', 'p']):
            text_content = element.get_text(strip=True)
            # Look for elements that might contain NAV
            if re.search(r'nav|net\s+asset', text_content, re.I):
                match = re.search(r'(?:₹|Rs?\.?)\s*([0-9,.]+)', text_content)
                if match:
                    nav_value = match.group(1).replace(',', '')
                    try:
                        nav_float = float(nav_value)
                        if 1 <= nav_float <= 100000:
                            return f"Rs {nav_value}"
                    except ValueError:
                        pass
        
        # Look for large numbers that might be NAV (often displayed prominently)
        # This is a fallback - look for numbers in the range that could be NAV
        # Match both ₹ and Rs
        large_numbers = re.findall(r'(?:₹|Rs?\.?)\s*([0-9]{2,6}(?:\.[0-9]{2})?)', text)
        for num_str in large_numbers:
            try:
                num_float = float(num_str.replace(',', ''))
                if 100 <= num_float <= 100000:  # Reasonable NAV range for equity funds
                    # Check if it's near NAV-related text
                    nav_context = text[max(0, text.find(num_str) - 50):text.find(num_str) + 50]
                    if re.search(r'nav|price|value', nav_context, re.I):
                        return f"Rs {num_str}"
            except ValueError:
                pass
        
        return None
    
    def _extract_tax_implication(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract tax implication information from the page. Handles both ₹ and Rs."""
        # Look for tax-related sections
        tax_keywords = [
            r'tax\s+implication',
            r'tax\s+on\s+redemption',
            r'taxation',
            r'capital\s+gains\s+tax',
            r'tax\s+liability',
        ]
        
        text = soup.get_text(separator=' ', strip=True)
        
        # Find tax-related content in elements
        for keyword in tax_keywords:
            for element in soup.find_all(['div', 'span', 'p', 'li', 'section']):
                text_content = element.get_text(strip=True)
                if re.search(keyword, text_content, re.I):
                    # Extract tax information - look for sentences with percentages or amounts
                    # Try to get a complete sentence or paragraph
                    sentences = re.split(r'[.!?]\s+', text_content)
                    for sentence in sentences:
                        if re.search(keyword, sentence, re.I) and (
                            '%' in sentence or 'Rs' in sentence or '₹' in sentence or 'lakh' in sentence.lower() or 
                            'year' in sentence.lower() or 'redeem' in sentence.lower()
                        ):
                            cleaned = re.sub(r'\s+', ' ', sentence.strip())
                            # Remove "Tax implication" prefix if present
                            cleaned = re.sub(r'^tax\s+implication\s*', '', cleaned, flags=re.I)
                            if len(cleaned) > 20 and len(cleaned) < 500:
                                return cleaned
                    
                    # If no good sentence found, return the element text if reasonable
                    cleaned = re.sub(r'\s+', ' ', text_content)
                    if len(cleaned) > 20 and len(cleaned) < 500 and (
                        '%' in cleaned or 'Rs' in cleaned or '₹' in cleaned or 'lakh' in cleaned.lower()
                    ):
                        return cleaned
        
        # Try to find tax information in the full text with context
        # Look for patterns like "If you redeem within one year, returns are taxed at 20%"
        tax_patterns = [
            r'if\s+you\s+redeem\s+within\s+one\s+year.*?taxed\s+at\s+([0-9]+%)',
            r'if\s+you\s+redeem\s+after\s+one\s+year.*?taxed\s+at\s+([0-9.]+%)',
            r'tax.*?(?:redeem|redemption).*?(?:year|financial).*?(?:\.|$)',
            r'(?:redeem|redemption).*?tax.*?(?:year|financial).*?(?:\.|$)',
            r'tax.*?[0-9]+%.*?(?:year|financial).*?(?:\.|$)',
        ]
        
        for pattern in tax_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                tax_info = match.group(0).strip()
                tax_info = re.sub(r'\s+', ' ', tax_info)
                # Check if it contains percentage or amount
                if ('%' in tax_info or 'Rs' in tax_info or '₹' in tax_info or 'lakh' in tax_info.lower()) and len(tax_info) < 500 and len(tax_info) > 20:
                    return tax_info
        
        return None

