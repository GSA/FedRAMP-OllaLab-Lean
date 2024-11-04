# Obtaining API Keys for Different Providers

To use the Simple Chat application with various large language models (LLMs), you need to obtain API keys or credentials for each provider you wish to use. This document provides instructions for obtaining API keys for OpenAI, Google Vertex AI, Amazon Bedrock, and Anthropic.

## OpenAI

1. Go to [OpenAI's API page](https://platform.openai.com/signup).
2. Log in with your OpenAI account or create a new one if you don’t have an account.
3. After logging in, go to the [API Keys section](https://platform.openai.com/account/api-keys).
4. Click on **Create new secret key** and copy the generated API key.
5. Store this key securely, as it will only be displayed once. You will need this key to configure OpenAI in the application.

## Google Vertex AI

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your Google Cloud project or create a new one if necessary.
3. Enable the **Vertex AI API**:
   - Go to **APIs & Services** > **Library**.
   - Search for "Vertex AI" and click on **Enable**.
4. Create a service account for authentication:
   - Go to **IAM & Admin** > **Service Accounts**.
   - Click on **+ Create Service Account**.
   - Follow the prompts to create a service account.
   - Assign the **Vertex AI User** role to the service account.
5. Download the Service Account Key:
   - Go to **Keys** for your service account.
   - Click on **Add Key** > **Create new key**.
   - Choose **JSON** format and click **Create** to download the key file.
6. Upload this JSON key file to the application to configure Google Vertex AI.

## Amazon Bedrock

1. Go to the [AWS Management Console](https://aws.amazon.com/console/).
2. Sign in with your AWS account.
3. Navigate to **IAM** (Identity and Access Management) to create credentials:
   - Go to **Users** and click **Add user**.
   - Set a username and select **Programmatic access**.
4. Set permissions:
   - Attach the **AmazonBedrockFullAccess** policy to your user (or create a custom policy with the necessary permissions).
5. Complete the user creation process and download the **Access Key ID** and **Secret Access Key**.
6. Store these keys securely. You will need them to configure Amazon Bedrock in the application.

## Anthropic

1. Visit [Anthropic's API page](https://www.anthropic.com/) and sign up or log in with your account.
2. Contact Anthropic or apply through their website to gain access to the API.
3. After access is granted, go to the API settings section on your [Anthropic Console - API Keys](https://console.anthropic.com/settings/keys).
4. Copy the **API Key** provided and store it securely. This key will be required to configure Anthropic in the application.

---

**Note:** Ensure that each key or credential is stored securely and not shared publicly. Each provider may charge for API usage, so refer to their pricing policies for details.
