Install the SDK
Anthropic provides SDKs for Python (3.7+) and TypeScript (4.5+).

Python
TypeScript
In your project directory, create a virtual environment.


python -m venv claude-env
Activate the virtual environment using

On macOS or Linux, source claude-env/bin/activate
On Windows, claude-env\Scripts\activate

pip install anthropic
​
Set your API key
Every API call requires a valid API key. The SDKs are designed to pull the API key from an environmental variable ANTHROPIC_API_KEY. You can also supply the key to the Anthropic client when initializing it.


macOS and Linux

Windows

export ANTHROPIC_API_KEY='your-api-key-here'
​
Call the API
Call the API by passing the proper parameters to the /messages endpoint.

Note that the code provided by the Workbench sets the API key in the constructor. If you set the API key as an environment variable, you can omit that line as below.


Python

TypeScript

import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1000,
    temperature=1,
    system="You are a world-class poet. Respond only with short poems.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Why is the ocean salty?"
                }
            ]
        }
    ]
)
print(message.content)
Run the code using python3 claude_quickstart.py or node claude_quickstart.js.


Output (Python)

Output (TypeScript)

[
  {
    type: 'text',
    text: "The ocean's vast expanse,\n" +
      'Tears of ancient earth,\n' +
      "Minerals released through time's long dance,\n" +
      'Rivers carry worth.\n' +
      '\n' +
      'Salt from rocks and soil,\n' +
      'Washed into the sea,\n' +
      'Eons of this faithful toil,\n' +
      'Briny destiny.'
  }
]
The Workbench and code examples use default model settings for: model (name), temperature, and max tokens to sample.
This quickstart shows how to develop a basic, but functional, Claude-powered application using the Console, Workbench, and API. You can use this same workflow as the foundation for much more powerful use cases.