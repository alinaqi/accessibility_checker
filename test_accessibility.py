#!/usr/bin/env python3
"""
Test script for accessibility checker.

This script demonstrates how to use the accessibility_checker module programmatically
with the updated async implementation that uses Playwright for full page rendering.
"""

import asyncio
import os
from dotenv import load_dotenv
from accessibility_checker import (
    load_accessibility_rules,
    validate_url,
    check_accessibility,
    save_results
)

# Load environment variables
load_dotenv()

async def run_test():
    """Run a test accessibility check on the specified URL asynchronously."""
    # URL to check
    test_url = "https://zenresponses.zenloop.com/?orgId=4145&surveyId=603"
    
    # Load API key from environment variables
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    # Validate URL
    print(f"Validating URL: {test_url}")
    if not validate_url(test_url):
        print("URL validation failed. Exiting.")
        return
    
    # Load accessibility rules
    print("Loading accessibility rules...")
    rules = load_accessibility_rules()
    
    # Run accessibility check
    print(f"Running accessibility check on {test_url}...")
    results = await check_accessibility(test_url, rules, api_key)
    
    # Save results
    output_file = "test_accessibility_results.json"
    print(f"Saving results to {output_file}...")
    save_results(results, output_file)
    
    # Print summary
    print("\nAccessibility Check Summary:")
    if "error" in results:
        print(f"Error: {results['error']}")
    elif "full_response" in results:
        print("Analysis completed, but results were not in expected JSON format.")
        print(f"Check {output_file} for full response.")
    else:
        for criteria, data in results.items():
            if isinstance(data, dict) and "status" in data:
                status = data["status"]
                print(f"- {criteria}: {status}")
    
    print(f"\nDetailed results saved to {output_file}")
    print("A screenshot of the rendered page has been saved to 'webpage_screenshot.png'")

def main():
    """Main function to run the accessibility test."""
    # Run the async test function
    asyncio.run(run_test())

if __name__ == "__main__":
    main() 