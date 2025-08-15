from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

# ------------------------------------------------
# Load Gemini API key from .env
# ------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# ------------------------------------------------
# Setup logging
# ------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('support_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------------------------------------
# Define the state schema for LangGraph
# ------------------------------------------------
class State(TypedDict):
    ticket: dict
    category: str
    context: str
    docs: list
    draft: str
    review_status: str
    review_feedback: str
    attempt: int
    messages: Annotated[list, add_messages]

# ------------------------------------------------
# 1. Ticket Classification Node
# ------------------------------------------------
def classify_ticket(state: State):
    ticket = state["ticket"]
    logger.info(f"Starting ticket classification for subject: {ticket.get('subject', '')}")
    
    prompt = (
        f"Classify the following support ticket into one of these categories: "
        f"Billing, Technical, Security, General.\n"
        f"Subject: {ticket.get('subject', '')}\n"
        f"Description: {ticket.get('description', '')}\n"
        f"Category:"
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )

    response = model.invoke(prompt)
    result = response.content.strip().split("\n")[0]  # First line = category
    logger.info(f"Ticket classified as: {result}")
    print(f"Classifying ticket: {ticket['subject']} -> {result}")

    return {"category": result}

# ------------------------------------------------
# 2. Retrieval Node
# ------------------------------------------------
def retrieve_context(state: State):
    category = state["category"].strip().lower()
    subject = state["ticket"].get("subject", "")
    description = state["ticket"].get("description", "")
    
    logger.info(f"Retrieving context for category: {category}")
    
    # Enhanced knowledge base with more comprehensive information
    knowledge_base = {
        "billing": [
            {
                "title": "Payment History Access",
                "content": "How to view your payment history and download invoices. Navigate to Account Settings > Billing > Payment History. You can filter by date range and download PDF invoices.",
                "keywords": ["payment", "invoice", "billing", "history", "download"]
            },
            {
                "title": "Refund Policy",
                "content": "Our refund policy allows for full refunds within 30 days of purchase. For disputes, contact billing support with your order number and reason for refund request.",
                "keywords": ["refund", "policy", "dispute", "30 days", "order"]
            },
            {
                "title": "Payment Methods",
                "content": "We accept Visa, MasterCard, American Express, PayPal, and bank transfers. Update payment methods in Account Settings > Billing > Payment Methods.",
                "keywords": ["credit card", "paypal", "bank transfer", "payment method"]
            },
            {
                "title": "Billing Support Contact",
                "content": "For billing inquiries, contact us at billing@company.com or call 1-800-BILLING. Include your account number for faster service.",
                "keywords": ["contact", "email", "phone", "support", "billing"]
            }
        ],
        "technical": [
            {
                "title": "App Troubleshooting",
                "content": "If the app crashes, try clearing cache, restarting the device, or reinstalling. Check system requirements: iOS 13+ or Android 8+. Common issues include network connectivity and storage space.",
                "keywords": ["crash", "troubleshoot", "cache", "restart", "reinstall", "system requirements"]
            },
            {
                "title": "App Updates",
                "content": "Enable automatic updates in your device settings. Manual updates available in App Store/Google Play. Latest version includes bug fixes and performance improvements.",
                "keywords": ["update", "automatic", "manual", "app store", "google play", "version"]
            },
            {
                "title": "Network Issues",
                "content": "Check your internet connection and firewall settings. Try switching between WiFi and mobile data. VPN users may need to whitelist our servers.",
                "keywords": ["network", "internet", "firewall", "wifi", "mobile data", "vpn"]
            },
            {
                "title": "Technical Support Contact",
                "content": "Technical support available 24/7 at tech@company.com or 1-800-TECH. Include device model, OS version, and error messages for faster resolution.",
                "keywords": ["support", "24/7", "email", "phone", "device", "error"]
            }
        ],
        "security": [
            {
                "title": "Password Reset",
                "content": "Reset password via login page > Forgot Password. Enter email address, check spam folder for reset link. Create strong password with 8+ characters, uppercase, lowercase, numbers, symbols.",
                "keywords": ["password", "reset", "forgot", "email", "strong", "security"]
            },
            {
                "title": "Two-Factor Authentication",
                "content": "Enable 2FA in Account Settings > Security > Two-Factor. Use authenticator app or SMS. Backup codes available for account recovery. Required for admin accounts.",
                "keywords": ["2fa", "two-factor", "authenticator", "sms", "backup codes", "admin"]
            },
            {
                "title": "Account Security",
                "content": "Regular security audits, suspicious activity monitoring, login attempt limits. Report suspicious activity immediately. Never share credentials or click suspicious links.",
                "keywords": ["security", "audit", "monitoring", "suspicious", "credentials", "phishing"]
            },
            {
                "title": "Security Support Contact",
                "content": "Security team available at security@company.com or 1-800-SECURE. For urgent security issues, use emergency hotline. Include incident details and timestamps.",
                "keywords": ["security", "emergency", "hotline", "incident", "urgent", "timeline"]
            }
        ],
        "general": [
            {
                "title": "Account Management",
                "content": "Update profile information in Account Settings. Change email, phone, or address. Download account data or request deletion per GDPR compliance.",
                "keywords": ["account", "profile", "settings", "gdpr", "data", "deletion"]
            },
            {
                "title": "Feature Requests",
                "content": "Submit feature requests via feedback form or email. Include use case, expected benefit, and priority level. Community voting determines development roadmap.",
                "keywords": ["feature", "request", "feedback", "roadmap", "community", "voting"]
            },
            {
                "title": "General Support Contact",
                "content": "General inquiries at support@company.com or 1-800-SUPPORT. Business hours: Mon-Fri 9AM-6PM EST. Include account number and detailed description.",
                "keywords": ["support", "business hours", "account number", "description", "general"]
            }
        ]
    }
    
    # Get relevant documents for the category
    category_docs = knowledge_base.get(category, [])
    
    # Enhanced semantic search using keyword matching and content relevance
    relevant_docs = []
    search_terms = f"{subject} {description}".lower().split()
    
    for doc in category_docs:
        # Calculate relevance score based on keyword matches
        keyword_matches = sum(1 for term in search_terms if term in doc["keywords"])
        content_matches = sum(1 for term in search_terms if term in doc["content"].lower())
        
        # Higher score for more relevant documents
        relevance_score = keyword_matches * 2 + content_matches
        
        if relevance_score > 0:
            relevant_docs.append({
                "doc": doc,
                "score": relevance_score
            })
    
    # Sort by relevance score and take top 3 most relevant
    relevant_docs.sort(key=lambda x: x["score"], reverse=True)
    top_docs = [item["doc"] for item in relevant_docs[:3]]
    
    # If no relevant docs found, provide category-specific general information
    if not top_docs:
        top_docs = category_docs[:2]  # Take first 2 docs from category
    
    # Extract content and create context summary
    doc_contents = [doc["content"] for doc in top_docs]
    context = f"Retrieved {len(top_docs)} relevant documents for category '{category}': {'; '.join(doc_contents)}"
    
    logger.info(f"Retrieved {len(top_docs)} relevant documents")
    
    return {
        "docs": doc_contents,
        "context": context,
        "doc_titles": [doc["title"] for doc in top_docs]
    }

# ------------------------------------------------
# 3. Draft Generation Node
# ------------------------------------------------
def generate_draft(state: State):
    ticket = state["ticket"]
    category = state["category"]
    docs = state["docs"]
    attempt = state.get("attempt", 1)
    feedback = state.get("review_feedback", "")
    
    logger.info(f"Generating draft response (Attempt {attempt}) for category: {category}")
    
    # If this is a retry, increment the attempt counter
    if feedback and attempt == 1:
        attempt = 2
        logger.info(f"Retry attempt detected, incrementing to attempt {attempt}")
    
    prompt = (
        "You are a professional support agent. Read the support ticket below and the relevant information provided. "
        "Draft a clear, empathetic, and actionable response for the customer. "
        "Directly address the user's issue, reference the relevant info, and provide step-by-step guidance or next actions. "
        "If the issue is security-related, advise on immediate steps to protect the account. "
        "If billing, explain refund/dispute process. "
        "If technical, offer troubleshooting steps. "
        "If general, answer the inquiry clearly. "
        "Do not make promises you cannot keep.\n"
        f"Category: {category}\n"
        f"Subject: {ticket.get('subject', '')}\n"
        f"Description: {ticket.get('description', '')}\n"
        f"Relevant Info: {'; '.join(docs)}\n"
        f"Previous Reviewer Feedback: {feedback}\n"
        f"Attempt: {attempt}\n"
        "\nCustomer Response:"
    )
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    response = model.invoke(prompt)
    draft = response.content.strip()
    logger.info(f"Draft response generated successfully (Attempt {attempt})")
    print(f"Drafted response (Attempt {attempt}): {draft}")
    return {"draft": draft, "attempt": attempt}

# ------------------------------------------------
# 4. Review Node (LLM-powered)
# ------------------------------------------------
def review_draft(state: State):
    ticket = state["ticket"]
    category = state["category"]
    docs = state["docs"]
    draft = state["draft"]
    attempt = state.get("attempt", 1)
    
    logger.info(f"Reviewing draft response (Attempt {attempt}) for category: {category}")
    
    prompt = (
        "You are a support QA reviewer. Read the support ticket, relevant info, and the draft response below. "
        "Evaluate if the response is accurate, helpful, and compliant with support guidelines. "
        "If approved, reply with 'approved' and a short comment. If rejected, reply with 'rejected' and specific feedback for revision.\n"
        f"Category: {category}\n"
        f"Subject: {ticket.get('subject', '')}\n"
        f"Description: {ticket.get('description', '')}\n"
        f"Relevant Info: {'; '.join(docs)}\n"
        f"Draft Response: {draft}\n"
        f"Attempt: {attempt}\n"
        "\nReview Result:"
    )
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    response = model.invoke(prompt)
    review_text = response.content.strip().lower()
    if "approved" in review_text:
        status = "approved"
        feedback = review_text
        logger.info(f"Draft approved on attempt {attempt}")
    else:
        status = "rejected"
        feedback = review_text
        logger.info(f"Draft rejected on attempt {attempt}. Feedback: {feedback[:100]}...")
    
    print(f"Review result (Attempt {attempt}): {status}\nFeedback: {feedback}")
    return {"review_status": status, "review_feedback": feedback}

# ------------------------------------------------
# 5. Escalation Node
# ------------------------------------------------
def escalate_ticket(state: State):
    """Log failed tickets to CSV for human review"""
    import csv
    from datetime import datetime
    
    ticket = state["ticket"]
    category = state["category"]
    docs = state["docs"]
    draft = state["draft"]
    review_feedback = state.get("review_feedback", "")
    attempt = state.get("attempt", 1)
    
    escalation_data = {
        "timestamp": datetime.now().isoformat(),
        "subject": ticket.get("subject", ""),
        "description": ticket.get("description", ""),
        "category": category,
        "attempts": attempt,
        "final_draft": draft,
        "reviewer_feedback": review_feedback,
        "retrieved_context": "; ".join(docs)
    }
    
    # Write to CSV file
    csv_file = "escalation_log.csv"
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = escalation_data.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(escalation_data)
    
    print(f"Ticket escalated to {csv_file} for human review")
    logger.info(f"Ticket escalated to {csv_file}")
    
    return {
        "escalation_status": "logged",
        "escalation_file": csv_file
    }

# ------------------------------------------------
# Build LangGraph Workflow
# ------------------------------------------------
graph = StateGraph(State)

# Add nodes
graph.add_node("classify", classify_ticket)
graph.add_node("retrieve", retrieve_context)
graph.add_node("draft", generate_draft)
graph.add_node("review", review_draft)
graph.add_node("escalate", escalate_ticket)

# Add linear edges for the main flow
graph.add_edge("classify", "retrieve")
graph.add_edge("retrieve", "draft")
graph.add_edge("draft", "review")

# Add conditional edges for review outcomes
def retry_condition(state: State):
    return state["review_status"] == "rejected" and state.get("attempt", 1) < 2

def success_condition(state: State):
    return state["review_status"] == "approved"

def escalation_condition(state: State):
    return state["review_status"] == "rejected" and state.get("attempt", 1) >= 2

# Add conditional edges with proper routing
graph.add_conditional_edges(
    "review",
    {
        "draft": retry_condition,      # Go back to draft if rejected and attempts < 2
        "__end__": success_condition,  # End if approved
        "escalate": escalation_condition  # Escalate if both attempts failed
    }
)

# Add edge from escalate to end
graph.add_edge("escalate", "__end__")

# Set the entry point
graph.set_entry_point("classify")

# Compile the graph
app = graph.compile()

# ------------------------------------------------
# Main Execution
# ------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Support Ticket Resolution Agent with Multi-Step Review Loop")
    print("=" * 60)
    print()
    
    try:
        # Get user input
        subject = input("Enter ticket subject: ").strip()
        description = input("Enter ticket description: ").strip()
        
        if not subject or not description:
            print("❌ Error: Both subject and description are required.")
            exit(1)
        
        # Initialize state
        initial_state = {
            "ticket": {
                "subject": subject,
                "description": description
            },
            "category": "",
            "context": "",
            "docs": [],
            "draft": "",
            "review_status": "",
            "review_feedback": "",
            "attempt": 1,
            "messages": []
        }
        
        logger.info(f"Starting new ticket processing: {subject}")
        
        # Run the complete workflow using pre-compiled graph
        print("\n🚀 Processing ticket through LangGraph workflow...")
        
        # Execute the workflow with explicit retry handling
        current_state = initial_state
        max_attempts = 2
        attempt = 1
        
        while attempt <= max_attempts:
            print(f"\n🔄 Attempt {attempt} of {max_attempts}")
            
            # Run the workflow up to the review step
            if attempt == 1:
                # First attempt: run through the entire workflow
                result = app.invoke(current_state)
            else:
                # Retry: start from draft with feedback
                retry_state = current_state.copy()
                retry_state["attempt"] = attempt
                retry_state["review_feedback"] = current_state.get("review_feedback", "")
                
                # Run from draft to review
                result = app.invoke(retry_state)
            
            # Check the result
            if result.get("review_status") == "approved":
                print("✅ Response approved! Workflow completed successfully.")
                break
            elif result.get("review_status") == "rejected" and attempt < max_attempts:
                print(f"🔄 Response rejected on attempt {attempt}. Retrying with feedback...")
                current_state = result
                attempt += 1
            else:
                print(f"🚨 Response rejected on attempt {attempt}. Escalating to human review...")
                # Manually trigger escalation
                escalation_result = escalate_ticket(result)
                result.update(escalation_result)
                break
        
        # Display final results
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"🎫 Ticket Subject: {result.get('ticket', {}).get('subject', 'N/A')}")
        print(f"📝 Description: {result.get('ticket', {}).get('description', 'N/A')}")
        print(f"🏷️  Category: {result.get('category', 'N/A')}")
        print(f"📚 Context: {result.get('context', 'N/A')}")
        print(f"📄 Final Draft: {result.get('draft', 'N/A')}")
        print(f"✅ Review Status: {result.get('review_status', 'N/A')}")
        print(f"🔄 Total Attempts: {result.get('attempt', 'N/A')}")
        
        # Check if escalation occurred
        if result.get('escalation_status'):
            print(f"🚨 Escalation: {result.get('escalation_status')}")
            print(f"📁 Escalation File: {result.get('escalation_file', 'N/A')}")
        
        logger.info("Ticket processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}", exc_info=True)
        print(f"\n❌ Error processing ticket: {str(e)}")
        print("Check the logs for more details.")
