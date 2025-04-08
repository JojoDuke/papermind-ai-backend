from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import uuid 
import json
import hmac
import hashlib
from supabase import create_client, Client
import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client with service role key
supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not service_key:
    raise ValueError("Missing Supabase configuration. Please check your .env file.")

print(f"Initializing Supabase client with URL: {supabase_url}")
supabase: Client = create_client(supabase_url, service_key)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://usepapermind.com/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wetro API configuration
WETRO_API_URL = "https://api.wetrocloud.com/v1/collection/query/"
WETRO_API_TOKEN = os.getenv("WETRO_API_TOKEN")
COLLECTION_ID = os.getenv("WETRO_COLLECTION_ID")

# Define models
class PDFUploadData(BaseModel):
    fileUrl: str
    fileName: str
    fileId: str

class ChatMessage(BaseModel):
    message: str
    collection_id: str

class DeleteCollection(BaseModel):
    collection_id: str

class QueryCollection(BaseModel):
    collection_id: str
    query: str
    model: str = "llama-3.3-70b"  # Default model

class SubscriptionWebhook(BaseModel):
    event: str
    data: dict

@app.post("/process-pdf")
async def process_pdf(data: PDFUploadData):
    try:
        # Generate a UUID for the collection
        collection_id = str(uuid.uuid4())
        
        # Create Wetro collection
        collection_response = requests.post(
            "https://api.wetrocloud.com/v1/collection/create/",
            headers={"Authorization": f"Token {WETRO_API_TOKEN}"},
            data={"collection_id": collection_id}
        )
        
        if not collection_response.json().get("success"):
            raise HTTPException(status_code=500, detail="Failed to create collection")
        
        # Insert PDF into collection
        print(f"Uploading file with URL: {data.fileUrl}")
        insert_response = requests.post(
            "https://api.wetrocloud.com/v1/resource/insert/",
            headers={
                "Authorization": f"Token {WETRO_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "collection_id": collection_id,
                "resource": data.fileUrl,
                "type": "file"
            }
        )
        
        if not insert_response.json().get("success"):
            raise HTTPException(status_code=500, detail="Failed to process PDF in Wetro")
            
        return {
            "success": True,
            "collection_id": collection_id,
            "resource_id": insert_response.json().get("resource_id")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-collection")
async def delete_collection(data: DeleteCollection):
    try:
        # Delete collection from Wetro
        delete_response = requests.delete(
            "https://api.wetrocloud.com/v1/collection/delete/",
            headers={
                "Authorization": f"Token {WETRO_API_TOKEN}"
            },
            json={
                "collection_id": data.collection_id
            }
        )
        
        if not delete_response.ok:
            raise HTTPException(status_code=500, detail="Failed to delete collection")
            
        return {
            "success": True,
            "message": f"Collection {data.collection_id} deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-collection")
async def query_collection(chat_message: ChatMessage):
    try:
        print(f"Received query request - Message: {chat_message.message}, Collection ID: {chat_message.collection_id}")
        
        # Prepare Wetro API request
        headers = {
            "Authorization": f"Token {WETRO_API_TOKEN}"
        }
        
        data = {
            "collection_id": chat_message.collection_id,
            "request_query": chat_message.message,
            "model": "meta-llama/llama-4-scout-17b-16e-instruct"
        }
        
        print(f"Sending request to Wetro with data: {data}")
        
        # Make request to Wetro
        response = requests.post(WETRO_API_URL, json=data, headers=headers)
        wetro_response = response.json()
        
        print(f"Wetro response: {wetro_response}")
        
        # Extract the text response - adjust this based on Wetro's actual response structure
        response_text = wetro_response.get('response', 'No response from Wetro')
        if isinstance(response_text, dict):
            response_text = str(response_text)
        
        # Return just the text response
        return {"message": response_text}
        
    except Exception as e:
        print(f"Error calling Wetro API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/dodo-payments")
async def dodo_webhook(request: Request):
    raw_body = await request.body()
    print("Webhook endpoint was hit!")

    try:
        payload = json.loads(raw_body)
        print("Raw body:", payload)

        event_type = payload.get("type")
        print(f"Processing event type: {event_type}")

        if event_type == "payment.succeeded":
            print("Payment succeeded detected!")
            
            # Get the reference ID from the payment data
            payment_data = payload.get("data", {})
            reference_id = payment_data.get("reference_id")
            if not reference_id:
                print("No reference_id found in payment data")
                return {"status": "error", "message": "No reference_id found"}

            try:
                # Extract session_id and user_id from reference_id
                session_id, user_id = reference_id.split('_')
                print(f"Extracted session_id: {session_id}, user_id: {user_id}")
            except ValueError:
                print("Invalid reference_id format")
                return {"status": "error", "message": "Invalid reference_id format"}

            # Verify the payment session exists and matches the user
            session_response = supabase.table("payment_sessions").select("*").eq("id", session_id).eq("user_id", user_id).single().execute()
            if session_response.error or not session_response.data:
                print("Error verifying payment session:", session_response.error if session_response.error else "Session not found")
                return {"status": "error", "message": "Invalid payment session"}

            # Update user's subscription status and credits
            user_update = supabase.table("users").update({
                "credits_remaining": 100,  # Reset credits to 100
                "is_premium": True,        # Set premium status
                "subscription_status": "active",
                "subscription_updated_at": datetime.datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            # Update the payment session
            session_update = supabase.table("payment_sessions").update({
                "status": "completed",
                "updated_at": datetime.datetime.utcnow().isoformat(),
                "payment_intent_id": payment_data.get("payment_id"),
                "amount": payment_data.get("total_amount"),
                "currency": payment_data.get("currency")
            }).eq("id", session_id).execute()
            
            print("User update response:", user_update)
            print("Session update response:", session_update)
            
        elif event_type == "subscription.renewed":
            print("Subscription renewed detected!")
            # Handle subscription renewal if needed
            
        elif event_type == "subscription.active":
            print("Subscription activated detected!")
            # Handle subscription activation if needed

        return {"status": "ok"}

    except Exception as e:
        print("Error processing webhook:", e)
        return {"status": "error", "message": str(e)}
