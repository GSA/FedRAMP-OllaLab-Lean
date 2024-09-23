# Streamlit Application Development Prompt Template
This document will guide you through the steps of working with LLMs to build a professional and secure basic Streamlit application. The goal is to help you jump start your project and you may need to add more steps and prompts. We hope you'll find this document useful and contribute your prompts to improve it.

## Step 1 - Construct Application Context
In this step, you will write the description of the variable **{{Context}}** with the following details.
- Goal: Clearly state the project’s objectives. Explain why this project is important and what problems it aims to solve.
- The Key Components: Introduce the services used and why they were chosen, but focus on their role in achieving the project’s goal.
- Explain Service Interactions: Briefly describe how these components interact and how the architecture fits together.
- Target Audience & Usage: Mention the intended users or use cases, especially if it has beginner-friendly features or advanced customization for experienced users.

### Step 1a - Identify the Goals
Think carefully about all the goals and objectives and concisely write it down to the **{{goal}}** variable.
Here is an example:
```
goal = "The application 'Chat with API' allows users to chat with data received from API requests. Via a Streamlit web interface, users will be able to provide information for successful API connection, put in a search query to pull data from API requests, and be able to chat with the pulled data."
```
### Step 1b - Generate Application Architecture
In this step, you will provide an AI bot with the identified goal and ask for a recommended application architecture. The template is:

{{goal}}

In plain language, describe in as much detail as possible the most reliable and secure structure for this application.

Here is an example of a prompt:
```
The application 'Chat with API' allows users to chat with data received from API requests. Via a Streamlit web interface, users will be able to provide information for successful API connection, put in a search query to pull data from API requests, and be able to chat with the pulled data. In plain language, describe in as much detail as possible the most reliable and secure structure for this application.
```

You will then analyze the recommended application architecture, make necessary changes/improvements, and write the result to the **{{architecture}}** variable. Here is an example:
```
architecture = "The application can be broken down into the following key modules: User Authentication and API Setup, Data Retrieval from API, Data Storage and Processing, Chat Interface with API Data, and Security and Error Handling. In User Authentication and API Setup, users will need to provide information to connect to the API (such as API keys, OAuth tokens, or other credentials) via the Streamlit interface. In Data Retrieval from API, users can provide a search query (e.g., keywords or specific criteria) via the interface. The application will send a request to the API, retrieve the data, and display it in the Streamlit UI. Once the data is pulled from the API, it needs to be stored in a temporary format that allows users to interact with it (e.g., a Pandas DataFrame or Python dictionary). Once the data is available, the user will interact with it using a chat interface. The system should intelligently respond based on user queries related to the API data."
```
### Step 1c - Provide Sample Usecases
Think carefully about the key usecases and related stakeholders. Concisely write it down to the **{{use_cases}}** variable.
Here is an example:
```
use_cases = Sample use cases are as follows. Case 1: A cybersecurity analyst can put in the needed information to query the National Vulnerability Database REST API. S/he then put in search queries to retreive the related CVEs in JSON format. S/he can then chat with the retreived data to investigate further the CVEs of interest. Case 2: A developer puts in an API access token and necessary informtion to connect to an internal API. Via the API, the developer received data from multiple data sources that the API has access to. The developer can now can chat with the received data to assist the developer's own data driven software development.
```

## Step 2 - Identify Project Requirements
In this step, you will write the description of the variable **{{requirements}}** by first asking the AI bot to recommend a robust set of requirements. The template is as follows:

{{goal}}

{{architecture}}

{{use_cases}}

You are an experienced solution architect and project manager. Please help me write a robust set of requirements for the application I am trying to build. Please be as rigorous and specific as possible.

An example prompt can be:
```
The application 'Chat with API' allows users to chat with data received from API requests. Via a Streamlit web interface, users will be able to provide information for successful API connection, put in a search query to pull data from API requests, and be able to chat with the pulled data. In plain language, describe in as much detail as possible the most reliable and secure structure for this application.

The application can be broken down into the following key modules: User Authentication and API Setup, Data Retrieval from API, Data Storage and Processing, Chat Interface with API Data, and Security and Error Handling. In User Authentication and API Setup, users will need to provide information to connect to the API (such as API keys, OAuth tokens, or other credentials) via the Streamlit interface. In Data Retrieval from API, users can provide a search query (e.g., keywords or specific criteria) via the interface. The application will send a request to the API, retrieve the data, and display it in the Streamlit UI. Once the data is pulled from the API, it needs to be stored in a temporary format that allows users to interact with it (e.g., a Pandas DataFrame or Python dictionary). Once the data is available, the user will interact with it using a chat interface. The system should intelligently respond based on user queries related to the API data.

Sample use cases are as follows. Case 1: A cybersecurity analyst can put in the needed information to query the National Vulnerability Database REST API. S/he then put in search queries to retreive the related CVEs in JSON format. S/he can then chat with the retreived data to investigate further the CVEs of interest. Case 2: A developer puts in an API access token and necessary informtion to connect to an internal API. Via the API, the developer received data from multiple data sources that the API has access to. The developer can now can chat with the received data to assist the developer's own data driven software development.

You are an experienced solution architect and project manager. Please help me write a robust set of requirements for the application I am trying to build. Please be as rigorous and specific as possible.
```

Record the results to the variable 

## Step 3 - Generate the Initial Application Codes
In this step, you will ask the AI bot to write the initial application codes. The template is as follows:

{{goal}}

{{architecture}}

{{use_cases}}

{{requirements}}

You are an experienced programmer. Please help me write the application. Please make sure it is as robust and secure as possible. 

> **Warning**
> Make sure the length of the prompt is way below the active LLM's context window. 

A sample prompt is as follows:
```
The application 'Chat with API' allows users to chat with data received from API requests. Via a Streamlit web interface, users will be able to provide information for successful API connection, put in a search query to pull data from API requests, and be able to chat with the pulled data. In plain language, describe in as much detail as possible the most reliable and secure structure for this application.

The application can be broken down into the following key modules: User Authentication and API Setup, Data Retrieval from API, Data Storage and Processing, Chat Interface with API Data, and Security and Error Handling. In User Authentication and API Setup, users will need to provide information to connect to the API (such as API keys, OAuth tokens, or other credentials) via the Streamlit interface. In Data Retrieval from API, users can provide a search query (e.g., keywords or specific criteria) via the interface. The application will send a request to the API, retrieve the data, and display it in the Streamlit UI. Once the data is pulled from the API, it needs to be stored in a temporary format that allows users to interact with it (e.g., a Pandas DataFrame or Python dictionary). Once the data is available, the user will interact with it using a chat interface. The system should intelligently respond based on user queries related to the API data.

Sample use cases are as follows. Case 1: A cybersecurity analyst can put in the needed information to query the National Vulnerability Database REST API. S/he then put in search queries to retreive the related CVEs in JSON format. S/he can then chat with the retreived data to investigate further the CVEs of interest. Case 2: A developer puts in an API access token and necessary informtion to connect to an internal API. Via the API, the developer received data from multiple data sources that the API has access to. The developer can now can chat with the received data to assist the developer's own data driven software development.

1. Functional Requirements
1.1 User Authentication and API Setup

    API Authentication: The application must allow users to securely provide authentication information to connect to external APIs. Supported authentication mechanisms should include:
        API keys (via user input fields).
        OAuth2 (via client ID, client secret, and redirect URL).
        Bearer tokens (for internal APIs).

    Input Fields: The system must provide appropriate input fields for:
        API URL or endpoint.
        API Key or Access Token (input must be masked for security).
        OAuth2 credentials (client ID, client secret, etc.).

    Credential Validation: The application must validate credentials by testing the API connection before allowing users to proceed.

    Session-based Credentials Management: Store API credentials securely in the session state. Ensure that credentials are cleared when the session ends or when the user logs out.

1.2 Data Retrieval from API

    Search Query Input: The application must allow users to input search queries that can be used to retrieve data from the connected API. This query should support the following:
        String-based queries (e.g., keywords).
        API-specific query parameters (e.g., filters, pagination).

    Request Handling:
        Send a GET or POST request to the specified API using the provided credentials and query.
        Handle different data formats, including JSON, XML, or CSV, based on the API’s response.

    Data Display: Once the API response is received, display the data in a user-friendly format. For JSON responses:
        Format the response into a table or structured format (e.g., Pandas DataFrame).
        Allow users to download the raw response as a file (CSV, JSON, etc.).

    Pagination: Support APIs that return large datasets by handling pagination, allowing users to navigate through multiple pages of results without overloading the session.

1.3 Data Storage and Processing

    Temporary In-Memory Data Storage: Store the data retrieved from the API temporarily in memory during the session. This data should be processed into appropriate data structures, such as:
        Pandas DataFrame: For tabular data.
        Python dictionary: For more complex JSON responses.

    Data Operations: The system must allow users to perform operations on the retrieved data, such as:
        Filtering based on criteria (e.g., dates, IDs, severity for CVEs).
        Sorting data by columns (e.g., sorting CVEs by severity or publication date).

    Data Integrity: Ensure that data integrity is maintained throughout the session. If there are any issues with the API response (e.g., data format errors), provide clear and actionable error messages.

1.4 Chat Interface with API Data

    Chat Input: The system must provide a chat-style interface where users can input natural language queries or commands to interact with the retrieved data. For example:
        Example: "Show all CVEs with severity higher than medium."
        Example: "List vulnerabilities from 2023."

    Natural Language Processing (NLP): Implement a lightweight NLP or rule-based query system to interpret user input. Consider these approaches:
        Basic keyword matching for simple queries (e.g., "list", "filter", "sort").
        More advanced parsing using libraries such as SpaCy, NLTK, or leveraging pre-trained LLMs (like GPT).

    Response Generation: Based on the chat input, the system must:
        Process the query and return a meaningful response (e.g., filtered or sorted data).
        Respond to simple follow-up questions like "Show the latest 5 records" or "What is the highest severity?"

    Conversation History: Maintain a visible chat history during the session so that users can see previous queries and system responses.

2. Security Requirements
2.1 User Data and Credential Security

    Secure Transmission: Ensure all API requests and data transmission happen over HTTPS to protect data in transit.

    Encryption of Sensitive Data: Any sensitive data (e.g., API keys, OAuth tokens) must be encrypted while stored in memory or session state.

    Session Expiry and Cleanup: Implement session timeouts and automatically clean up any sensitive data after the session expires or the user logs out.

    Environment Variables for Default Values: If default credentials or tokens are used (e.g., for internal APIs), these must be stored securely in environment variables or a secret management service.

    Input Validation and Sanitization:
        Validate all user inputs (e.g., API endpoints, search queries, chat queries) to prevent injection attacks and other malicious inputs.
        Properly sanitize all inputs that are used in API requests or in database queries (if applicable).

2.2 API Rate Limiting and Throttling

    Rate Limiting: Implement rate-limiting mechanisms to avoid API overuse or abuse, particularly for public APIs like the National Vulnerability Database (NVD).

    Error Handling for Rate Limits: Detect when rate limits are hit (e.g., HTTP 429 status code) and provide meaningful feedback to the user, suggesting they try again later or change the query.

2.3 OAuth Token Expiration and Refresh

    Token Expiry Management: For APIs using OAuth2, manage token expiration and provide automatic token refresh when possible. Notify users if they need to reauthenticate when tokens expire.

    User Logout: Provide a secure logout functionality that clears all sensitive data and credentials, ending the user’s session.

3. Performance Requirements
3.1 Scalability

    Efficient Memory Usage: Ensure that the data stored in session (in-memory) is efficiently managed to prevent excessive memory usage, especially when handling large datasets from APIs.

    Asynchronous API Requests: If the API supports it, implement asynchronous API requests to improve response times and handle multiple queries efficiently.

3.2 Handling Large API Responses

    Pagination Support: Handle large datasets using pagination, retrieving small portions of data at a time.

    Batch Processing: For large datasets, allow users to batch process data (e.g., retrieving 100 records at a time) to avoid timeouts and delays.

4. User Experience (UX) Requirements
4.1 Streamlined User Interface

    API Setup Section: The credentials input fields must be clear and intuitive. Provide helper text or examples for each input field (e.g., "Enter your API Key here").

    Search Query Section: Provide a simple, user-friendly text box for users to input search queries or filters. Clearly label this section with examples of valid queries.

    Data Display: Once the API data is retrieved, display it in a clean, interactive table format. Provide options for users to:
        Sort and filter data in the table.
        Download the data as a CSV, JSON, or other file formats.

4.2 Chat Interface

    Chat Box: Provide a persistent, clearly visible chat box where users can interact with the data. Make sure the chat box:
        Has placeholder text guiding the user (e.g., "Ask about the retrieved data...").
        Is resizable and supports multiline queries.

    Quick Action Buttons: Consider adding pre-configured quick action buttons or dropdowns for common queries (e.g., "Sort by severity", "Filter by date").

    Responsive Feedback: Provide immediate feedback to user queries, with a visible progress spinner if data processing or retrieval takes time.

4.3 Error and Success Messages

    User-Friendly Error Messages: When API requests fail, or invalid inputs are detected, provide clear, actionable error messages (e.g., "Invalid API Key", "No data found for this query").

    Loading Indicators: When making API requests or processing user queries, show a loading spinner or progress indicator to inform users that the system is working on their request.

5. Error Handling Requirements
5.1 API Request Errors

    Handle Common API Errors:
        Connection timeouts, invalid credentials, rate-limited requests, and missing data should be properly caught and reported to the user with suggestions on how to resolve the issue.
    Graceful Failures: If the API fails to return data (e.g., server is down), the system should display a non-intrusive error message and allow the user to retry without refreshing the whole app.

6. Compliance Requirements
6.1 Privacy and Data Protection

    Ensure that user credentials and any personal data remain private and are not shared with third parties.
    Comply with relevant data protection laws (e.g., GDPR) when storing or transmitting sensitive information, especially in the case of sensitive internal APIs.

You are an experienced programmer. Please help me write the application. Please make sure it is as robust and secure as possible. 
```

## Step 4 - Optimize the Application Codes
The AI bot will not generate production-ready codes. It is essential that we always review the generated codes, trouble shoot issues, and optimize the codes. There are ways to involve the AI bot in this process and the prompt templates for optimizing application codes will be available in a separate file.