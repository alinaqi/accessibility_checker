# Accessibility Checker

A Python tool that checks websites for accessibility issues using the Anthropic API, based on predefined accessibility criteria. It uses Playwright to fully render webpages including JavaScript content before analyzing them.

## Features

- Evaluates websites against WCAG guidelines and specific accessibility criteria
- Uses Playwright to fully render webpages with JavaScript before analysis
- Captures screenshots of the rendered page for visual reference
- Extracts the accessibility tree for more accurate assessment
- Uses Anthropic's Claude model for intelligent accessibility analysis
- Provides detailed pass/fail assessments for each accessibility criterion
- Generates specific recommendations for fixing accessibility issues
- Outputs results in JSON format for easy integration with other tools

## Requirements

- Python 3.7 or higher
- Anthropic API key
- Playwright browsers (installed automatically)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/accessibility-check.git
cd accessibility-check
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

4. Set up your Anthropic API key:

Create a `.env` file in the root directory with the following content:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Anthropic API key.

## Usage

### Basic Usage

Run the script with a URL to check:

```bash
python accessibility_checker.py https://example.com
```

### Advanced Options

```bash
python accessibility_checker.py URL [--rules RULES_FILE] [--output OUTPUT_FILE] [--api-key API_KEY]
```

- `URL`: The website URL to check for accessibility issues
- `--rules`: Path to a JSON file containing accessibility rules (default: docs/survey_checks.json)
- `--output`: Path to save the accessibility check results (default: accessibility_results.json)
- `--api-key`: Anthropic API key (overrides the environment variable)

### Example

```bash
python accessibility_checker.py https://zenresponses.zenloop.com/?orgId=4145&surveyId=603 --output zenloop_accessibility.json
```

## How It Works

1. The tool launches a headless browser using Playwright to fully render the webpage
2. It waits for all network requests to complete and for JavaScript to execute
3. Once rendered, it captures:
   - The complete HTML after JavaScript execution
   - The accessibility tree of the page
   - A screenshot of the fully rendered page
4. This information is sent to the Anthropic API for analysis
5. The API evaluates the content against the specified accessibility criteria
6. Results are returned as a structured JSON response
7. A summary is displayed and detailed results are saved to a file

## Output

The script generates three output files:
1. A JSON file with detailed accessibility check results
2. A screenshot of the fully rendered webpage (`webpage_screenshot.png`)
3. Console output summarizing the findings

## Accessibility Criteria

The tool evaluates websites against the following accessibility criteria:

1. **Semantic Structure**: Use of semantic HTML elements and proper document structure
2. **Keyboard Navigation**: Keyboard operability and focus management
3. **Visual Design**: Color contrast, responsive layout, and text scaling
4. **Form Controls and Error Handling**: Proper form labeling and error messaging
5. **Dynamic Content**: Accessible handling of dynamic changes and multi-step processes
6. **ARIA and Custom Controls**: Proper implementation of ARIA roles and custom components
7. **Mobile Accessibility**: Responsive design and support for mobile assistive technologies
8. **Documentation and Support**: Accessibility statements and help options
9. **Testing and Compliance**: Integration of automated and manual testing

## Troubleshooting

If you encounter issues:

1. **Playwright Installation**: If you experience problems with Playwright, try reinstalling:
   ```bash
   playwright install --force
   ```

2. **Timeout Errors**: For complex pages, try increasing the timeout in the script.

3. **API Key**: Ensure your Anthropic API key is correctly set in the `.env` file or passed as an argument.

## License

[MIT License](LICENSE) 