#!/usr/bin/env python3
"""
Accessibility Checker

This script checks a website URL for accessibility issues based on predefined criteria
using the Anthropic API. It uses Playwright to fully render the webpage including
JavaScript content before analysis.
"""

import os
import json
import argparse
import requests
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import anthropic
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

def load_accessibility_rules(file_path: str = "docs/survey_checks.json") -> Dict[str, Any]:
    """
    Load accessibility rules from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing accessibility rules
    
    Returns:
        Dictionary of accessibility rules
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading accessibility rules: {e}")
        exit(1)

def validate_url(url: str) -> bool:
    """
    Validate if the provided URL is properly formatted and accessible.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid and accessible, False otherwise
    """
    # Check URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            print(f"Invalid URL format: {url}")
            return False
    except Exception:
        print(f"Invalid URL: {url}")
        return False
    
    # Check if website is accessible
    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {e}")
        return False

async def fetch_rendered_content(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the fully rendered content of a webpage using Playwright.
    
    Args:
        url: URL of the webpage to fetch
    
    Returns:
        Dictionary containing HTML content, accessibility tree, and screenshots
    """
    try:
        print("Launching browser to render webpage...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set longer timeout and wait for network idle
            print(f"Navigating to {url} and waiting for page to fully load...")
            await page.goto(url, timeout=60000, wait_until="networkidle")
            
            # Wait additional time to ensure JS renders
            await page.wait_for_timeout(5000)
            
            # Take screenshot
            screenshot_path = "webpage_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Get HTML content after JS execution
            html_content = await page.content()
            
            # Get accessibility tree (useful for analysis)
            accessibility_snapshot = await page.accessibility.snapshot()
            
            await browser.close()
            
            return {
                "html": html_content,
                "accessibility_tree": accessibility_snapshot,
                "screenshot_path": screenshot_path
            }
    except Exception as e:
        print(f"Error rendering webpage: {e}")
        return None

def format_rules_for_prompt(rules: Dict[str, Any]) -> str:
    """
    Format accessibility rules for inclusion in the Anthropic prompt.
    
    Args:
        rules: Dictionary of accessibility rules
    
    Returns:
        Formatted string of accessibility rules
    """
    formatted_rules = "Accessibility criteria to check:\n\n"
    
    for key, criteria in rules.get("surveyToolAccessibilityCriteria", {}).items():
        formatted_rules += f"- {key}:\n"
        formatted_rules += f"  Description: {criteria.get('description', 'N/A')}\n"
        formatted_rules += f"  Compliance: {criteria.get('compliance', 'N/A')}\n\n"
    
    return formatted_rules

async def check_accessibility(url: str, rules: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Check the webpage at the given URL for accessibility issues using Anthropic API.
    
    Args:
        url: URL of the webpage to check
        rules: Dictionary of accessibility rules
        api_key: Anthropic API key (optional, defaults to env var)
    
    Returns:
        Dictionary of accessibility check results
    """
    # Fetch fully rendered webpage content
    rendered_content = await fetch_rendered_content(url)
    if not rendered_content:
        return {"error": "Failed to render webpage content"}
    
    html_content = rendered_content["html"]
    accessibility_tree = rendered_content["accessibility_tree"]
    
    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Prepare system prompt with the rules
    system_prompt = """
    You are an accessibility expert tasked with evaluating a webpage against WCAG guidelines and specific accessibility criteria.
    You have been provided with the fully rendered HTML after JavaScript execution and the accessibility tree of the page.
    
    Analyze the HTML content and accessibility tree to identify any accessibility issues based on the criteria.
    For each criteria, provide:
    1. A pass/fail assessment
    2. Detailed explanation of any issues found
    3. Specific recommendations for fixing the issues
    4. Code examples where applicable
    
    Be thorough and precise in your analysis. Focus on practical issues that affect real users with disabilities.
    Pay special attention to how the page would work with screen readers and keyboard-only navigation.
    """
    
    # Format the user message with the URL, rules, and content
    formatted_rules = format_rules_for_prompt(rules)
    
    # Convert accessibility tree to string with nice formatting for better analysis
    accessibility_tree_str = json.dumps(accessibility_tree, indent=2)
    
    user_message = f"""
    Please analyze the following webpage for accessibility issues:
    
    URL: {url}
    
    {formatted_rules}
    
    Here is the fully rendered HTML content to analyze:
    ```html
    {html_content[:100000]}  # Truncate to avoid token limits
    ```
    
    Here is the accessibility tree of the page:
    ```json
    {accessibility_tree_str[:50000]}  # Truncate to avoid token limits
    ```
    
    For each accessibility criteria, provide:
    1. PASS/FAIL status
    2. Issues found (if any)
    3. Recommendations for improvement
    4. Code examples for fixes where applicable
    
    Format your response as a structured JSON object with keys for each criteria and nested fields for status, issues, and recommendations.
    """
    
    # Make API call to Anthropic
    try:
        print("Sending request to Anthropic API for accessibility analysis...")
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4000,
            temperature=0,  # Use 0 for more deterministic responses
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        # Extract the response content
        response_text = message.content[0].text
        
        # Try to parse JSON from the response
        try:
            # Look for JSON content in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                results = json.loads(json_str)
            else:
                # If no JSON found, return the full text response
                results = {"full_response": response_text}
        except json.JSONDecodeError:
            # If JSON parsing fails, return the full text response
            results = {"full_response": response_text}
        
        return results
    
    except Exception as e:
        return {"error": f"Error during Anthropic API call: {str(e)}"}

def save_results(results: Dict[str, Any], output_file: str = "accessibility_results.json") -> None:
    """
    Save accessibility check results to a JSON file.
    
    Args:
        results: Dictionary of accessibility check results
        output_file: Path to save the results
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

async def main_async(args):
    """Asynchronous main function to run the accessibility check."""
    # Validate URL
    if not validate_url(args.url):
        return
    
    # Load accessibility rules
    rules = load_accessibility_rules(args.rules)
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or use --api-key")
        return
    
    print(f"Checking accessibility for {args.url}...")
    results = await check_accessibility(args.url, rules, api_key)
    
    # Save results
    save_results(results, args.output)
    
    # Print summary
    if "error" in results:
        print(f"Error: {results['error']}")
    elif "full_response" in results:
        print("Analysis completed but could not be parsed into JSON format.")
        print("See the output file for the full response.")
    else:
        print("\nAccessibility Check Summary:")
        for criteria, data in results.items():
            if isinstance(data, dict) and "status" in data:
                status = data["status"]
                print(f"- {criteria}: {status}")
        
    print(f"\nDetailed results saved to {args.output}")

def main():
    """Main function to parse arguments and run the accessibility check."""
    parser = argparse.ArgumentParser(description='Check a website for accessibility issues.')
    parser.add_argument('url', help='URL of the website to check')
    parser.add_argument('--rules', default='docs/survey_checks.json',
                        help='Path to JSON file containing accessibility rules')
    parser.add_argument('--output', default='accessibility_results.json',
                        help='Path to save the results')
    parser.add_argument('--api-key', help='Anthropic API key (overrides environment variable)')
    
    args = parser.parse_args()
    
    # Run the async main function
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main() 