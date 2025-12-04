# How to Use the API with Swagger UI

## Accessing Swagger UI

1. Open your browser and navigate to: `http://localhost:1999/docs`

## Authenticating with API Key

### Step 1: Click the "Authorize" Button
- Look for the **"Authorize"** button at the top right of the Swagger UI page
- It usually has a lock icon 🔒

### Step 2: Enter Your API Key
1. Click the "Authorize" button
2. A modal will appear with a field labeled **"X-API-Key"**
3. Enter your API key from the `.env` file (default: `your-secret-api-key-here`)
4. Click **"Authorize"**
5. Click **"Close"**

### Step 3: Test the Endpoints
Now all endpoints will automatically include your API key in the headers!

## Testing Text Model Endpoint

1. Scroll down to **"POST /text_model/chat/completion"**
2. Click on it to expand
3. Click **"Try it out"**
4. Edit the request body (example):
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```
5. Click **"Execute"**
6. View the response below

## Testing Image Model Endpoint

1. Scroll down to **"POST /image_model/chat/completion"**
2. Click on it to expand
3. Click **"Try it out"**
4. Click **"Choose File"** to upload an image
5. Enter a prompt (e.g., "What is in this image?")
6. Optionally set parameters like `temperature`, `max_tokens`
7. Click **"Execute"**
8. View the response below

## Testing Streaming Endpoints

For streaming endpoints (`/text_model/chat/stream` and `/image_model/chat/stream`):
- The response will stream in real-time
- Swagger UI will show the complete streamed response
- For better streaming visualization, use `curl -N` in terminal

## Common Issues

### "Missing API Key" Error
- Make sure you clicked "Authorize" and entered your API key
- The lock icon should be closed 🔒 (not open 🔓)

### "Invalid API Key" Error
- Check that your API key matches the one in `.env`
- Default key: `your-secret-api-key-here`

### Changing the API Key
1. Update `API_KEY` in `.env` file
2. Restart the server
3. Re-authorize in Swagger UI with the new key

## Security Note
- Never share your API key publicly
- Keep your `.env` file secure
- Rotate your API key regularly for better security
