# SOMERA Voice Setup Guide

## Overview

SOMERA Voice enables users to have coaching conversations with SOMERA via phone call, using:
- **VAPI** - Voice orchestration and call handling
- **Deepgram** - Speech-to-Text (STT)
- **ElevenLabs** - Text-to-Speech (TTS) with Shweta's cloned voice

## Architecture

```
User calls → VAPI (phone) → Deepgram (STT) → Our Webhook → SOMERA Engine → Response → ElevenLabs (TTS) → User hears
```

## Required API Keys & Secrets

| Service | Environment Variable | How to Get |
|---------|---------------------|------------|
| VAPI | `VAPI_API_KEY` | https://vapi.ai/dashboard → API Keys |
| Deepgram | `DEEPGRAM_API_KEY` | https://console.deepgram.com → API Keys |
| ElevenLabs | `ELEVENLABS_API_KEY` | https://elevenlabs.io → Profile → API Key |
| ElevenLabs Voice | `ELEVENLABS_VOICE_ID` | After cloning Shweta's voice, copy the Voice ID |
| Webhook Security | `VAPI_WEBHOOK_SECRET` | Generate a random string (32+ chars) and configure in VAPI dashboard |

## Security Configuration

For production, set up webhook authentication:

1. Generate a secret: `openssl rand -hex 32`
2. Add as `VAPI_WEBHOOK_SECRET` environment variable in Replit
3. In VAPI Dashboard → Assistant → Advanced → Server Authentication:
   - Select "Custom"
   - Add header: `x-vapi-secret` with your secret value
   
If `VAPI_WEBHOOK_SECRET` is not set, the webhook accepts all requests (dev mode only).

## Webhook Endpoint

The VAPI webhook is available at:
```
https://<your-domain>/api/vapi/webhook
```

For Replit, this will be:
```
https://<repl-name>.<username>.repl.co/api/vapi/webhook
```

## VAPI Assistant Configuration

When setting up the VAPI assistant in the dashboard:

### 1. Create New Assistant
- Name: "SOMERA Voice"
- First Message: "Hello, this is Somera. I'm here to listen and support you. What's on your mind today?"

### 2. Transcriber Settings
- Provider: **Deepgram**
- Model: **nova-2**
- Language: **English**

### 3. Voice Settings
- Provider: **ElevenLabs (11labs)**
- Voice ID: Use Shweta's cloned voice ID

### 4. Server URL
Set the Server URL to your webhook endpoint:
```
https://<your-domain>/api/vapi/webhook
```

### 5. Model Settings
- Provider: **OpenAI**
- Model: **gpt-4o-mini**

### 6. Custom Tool (Important!)
Add this custom tool to enable SOMERA responses:

```json
{
  "type": "function",
  "function": {
    "name": "get_somera_response",
    "description": "Get a coaching response from SOMERA based on what the user shared. Call this for every user message.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_message": {
          "type": "string",
          "description": "What the user said"
        }
      },
      "required": ["user_message"]
    }
  }
}
```

## Phone Number Setup

1. In VAPI Dashboard, go to **Phone Numbers**
2. Click **Buy Number**
3. Select **Country: US**
4. Choose a number
5. Assign the SOMERA Voice assistant to this number

## Testing

### Local Testing
Use VAPI's CLI for local testing:
```bash
vapi listen --port 4242 --forward http://localhost:8080
```

### Production Testing
1. Call the VAPI phone number
2. Speak to SOMERA
3. Check Webhook Server logs for `[VAPI]` entries

## Logs

All VAPI interactions are logged with the `[VAPI]` prefix:
- `[VAPI] Received <message_type> for call <call_id>`
- `[VAPI] Tool call: get_somera_response with params: {...}`
- `[VAPI] Call <call_id> ended. Reason: <reason>, Duration: <seconds>s`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No response from webhook | Check Webhook Server is running on port 8080 |
| Voice sounds robotic | Adjust ElevenLabs voice stability settings |
| Long response times | Optimize SOMERA engine response time (<1 second) |
| Call disconnects | Check VAPI credits, verify webhook is accessible |

## Cost Estimates

| Service | Cost |
|---------|------|
| VAPI | ~$0.05/min base + provider costs |
| Deepgram | ~$0.0043/min (Nova-2) |
| ElevenLabs | ~$0.30/1000 chars |
| **Total** | ~$0.15-0.25/min conversation |
