# Support Ticket Resolution Agent with Multi-Step Review Loop

## 🎯 Project Overview
.
This project implements an AI-powered support ticket resolution agent using the **LangGraph framework**. The agent follows a sophisticated multi-step workflow that mirrors real-world support operations

1. **Ticket Classification** → 2. **Context Retrieval** → 3. **Response Drafting** → 4. **Quality Review** → 5. **Retry/Approval Loop**

The system incorporates intelligent retry logic with feedback incorporation and automatic escalation for complex cases.

## Explanation video link:
https://drive.google.com/file/d/1cd5kdbQ7kxdY5afpr38irdRgvyIEf_kx/view?usp=drive_link


## 🏗️ Architecture

### Core Components

- **Classification Node**: LLM-powered ticket categorization (Billing, Technical, Security, General)
- **Retrieval Node**: Category-specific knowledge base retrieval with relevance filtering
- **Draft Generation Node**: Context-aware response generation with retry handling
- **Review Node**: Quality assurance and policy compliance checking
- **Escalation Node**: CSV-based logging for human review of failed cases

### LangGraph Workflow

```
[Input] → [Classify] → [Retrieve] → [Draft] → [Review]
                                    ↑         ↓
                                    ← [Retry] ← [Rejected]
                                    ↓
                              [Escalation] → [End]
```

### State Management

The system maintains comprehensive state tracking including:
- Ticket information (subject, description)
- Classification results
- Retrieved context and documents
- Draft responses and review outcomes
- Attempt counters and feedback loops

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Gemini API key from Google AI Studio

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Zikra_Assessment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install langgraph langchain langchain-google-genai python-dotenv
   ```

4. **Configure environment**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

5. **Run the agent**
   ```bash
   python src/main.py
   ```

## 📖 Usage

### Basic Operation

1. **Start the agent**: Run `python src/main.py`
2. **Enter ticket details**:
   - Subject: Brief description of the issue
   - Description: Detailed explanation
3. **Watch the workflow**: The system will automatically process through all steps
4. **Review results**: Final response or escalation details

### Example Ticket

```
Subject: Login failure on mobile app
Description: I'm unable to log into my account on the mobile app. 
I keep getting "Invalid credentials" error even though my password is correct.
```

### Expected Flow

1. **Classification**: Technical (based on login/mobile app keywords)
2. **Retrieval**: Technical support documents and troubleshooting guides
3. **Draft**: Professional response with troubleshooting steps
4. **Review**: Quality check and approval/rejection
5. **Output**: Final response or retry with feedback incorporation

## 🔧 Technical Implementation

### Key Features

- **Multi-Attempt Logic**: Maximum 2 attempts with intelligent feedback incorporation
- **Category-Specific Knowledge**: Tailored responses based on ticket classification
- **Comprehensive Logging**: Detailed logs in `support_agent.log` for debugging
- **Error Handling**: Graceful failure handling with escalation paths
- **State Persistence**: Full workflow state tracking throughout the process

### LangGraph Integration

- **StateGraph**: Manages complex workflow state
- **Conditional Edges**: Dynamic routing based on review outcomes
- **Node Modularity**: Clean separation of concerns
- **Message Handling**: Structured communication between nodes

### LLM Integration

- **Gemini 2.0 Flash**: Fast, reliable response generation
- **Prompt Engineering**: Carefully crafted prompts for each node
- **Temperature Control**: Consistent, deterministic outputs
- **Error Resilience**: Graceful handling of API failures

## 📊 Output Files

### Logs
- **`support_agent.log`**: Comprehensive execution logs with timestamps
- **Console Output**: Real-time progress and results display

### Escalation
- **`escalation_log.csv`**: Failed tickets requiring human review
- **Columns**: Timestamp, Subject, Description, Category, Attempts, Draft, Feedback, Context

## 🧪 Testing Scenarios

### Happy Path
- Simple technical question → Quick classification → Relevant context → Approved response

### Retry Scenario
- Complex billing issue → Initial draft rejected → Feedback incorporation → Successful retry

### Escalation Path
- Security concern → Multiple failed attempts → Automatic escalation to human review

## 🎨 Design Decisions

### Why LangGraph?
- **Workflow Orchestration**: Natural fit for multi-step processes
- **State Management**: Built-in state handling and persistence
- **Conditional Logic**: Easy implementation of retry and escalation paths
- **Production Ready**: Designed for real-world deployment

### Architecture Choices
- **Modular Nodes**: Easy to modify, test, and extend
- **State-Driven**: Clear data flow and dependency management
- **Logging-First**: Comprehensive observability for debugging
- **Error-Resilient**: Graceful degradation and escalation paths

### LLM Integration
- **Gemini 2.0 Flash**: Fast, cost-effective, and reliable
- **Structured Prompts**: Clear instructions and expected outputs
- **Feedback Loop**: Continuous improvement through review cycles

## 🔮 Future Enhancements

- **Vector Database**: Replace static knowledge base with semantic search
- **Multi-Modal**: Support for image attachments and screenshots
- **Integration APIs**: Connect to real ticketing systems
- **Performance Metrics**: Track response times and success rates
- **A/B Testing**: Compare different prompt strategies

## 📝 Assessment Requirements Met

✅ **LangGraph Framework**: Complete implementation using StateGraph
✅ **Multi-Step Process**: Classification → Retrieval → Draft → Review → Retry
✅ **Retry Logic**: Maximum 2 attempts with feedback incorporation
✅ **Escalation**: CSV logging for human review
✅ **Modular Architecture**: Clean separation of concerns
✅ **Error Handling**: Comprehensive logging and graceful failures
✅ **Documentation**: Detailed setup and usage instructions

## 🤝 Contributing

This is an assessment project demonstrating LangGraph capabilities. The code is structured for clarity and educational purposes, with comprehensive comments explaining each component.

## 📄 License

This project is created for assessment purposes. Please refer to the original assessment requirements for usage guidelines.

---

**Built with ❤️ using LangGraph, LangChain, and Gemini AI**
