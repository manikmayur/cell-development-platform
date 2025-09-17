# Multi-Agent Integration Guide

This guide explains how to use the integrated Google ADK multi-agent system with the Cell Development Platform.

## Overview

The Cell Development Platform now includes a sophisticated multi-agent system powered by Google ADK that provides specialized assistance for different aspects of battery cell development:

- **🎯 Task Coordinator**: Main coordinator for cell design tasks, workflow management, and overall planning
- **🔧 Cell Designer**: Specialized in cell design, architecture planning, and component selection
- **📚 Cell Library**: Manages cell design library, storage, search, and retrieval
- **📊 Cell Simulator**: Performs cell simulation, performance analysis, and modeling

## Quick Start

### 1. Environment Setup

First, copy the environment template and configure your API keys:

```bash
cp .env.template .env
```

Edit the `.env` file and add your API keys:

```bash
# Required for multi-agent system
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for fallback

# Optional: Customize model and ports
DEFAULT_MODEL=anthropic/claude-4-sonnet-20250514
AGENT_PORT=9003
MCP_PORT=9004
```

### 2. Install Dependencies

Install the required dependencies:

```bash
pip install -r cell_development_requirements.txt
```

### 3. Launch the Platform

#### Option A: Complete Platform (Recommended)
Launch both Streamlit and multi-agent system together:

```bash
python start_platform.py
```

This starts:
- Streamlit App at: http://localhost:8501
- Multi-Agent API at: http://localhost:9003

#### Option B: Separate Services
Start services individually:

```bash
# Terminal 1: Start multi-agent system
python start_multi_agent.py

# Terminal 2: Start Streamlit app
streamlit run main.py
```

## Using the Multi-Agent System

### 1. Access the Chat Interface

1. Open the Cell Development Platform in your browser (http://localhost:8501)
2. Look for the chat interface in the right sidebar
3. Select "Multi-Agent System" from the chat mode dropdown

### 2. Agent Selection

The system will automatically suggest the best agent based on your question, but you can manually select:

- **Task Coordinator** for general questions and workflow coordination
- **Cell Designer** for design-related questions ("How do I design a cylindrical cell?")
- **Cell Library** for storage and retrieval questions ("Save this design", "Find similar designs")
- **Cell Simulator** for analysis questions ("Simulate this cell performance")

### 3. Context Awareness

The multi-agent system is aware of your current context in the platform:
- Current page/workflow step
- Selected materials and components
- Previous design decisions
- Workflow state

### 4. Example Interactions

**Cell Design Questions:**
```
User: "I need to design a high-energy density lithium-ion cell for EV applications"
System: [Routes to Cell Designer Agent]
Agent: "I'll help you design an EV cell. Based on your requirements, I recommend..."
```

**Library Management:**
```
User: "Save this cell design to the library with the name 'EV-High-Energy-v1'"
System: [Routes to Cell Library Agent]  
Agent: "I'll save your current cell design. The design has been stored..."
```

**Performance Analysis:**
```
User: "What's the expected cycle life of this NMC811/Graphite cell?"
System: [Routes to Cell Simulation Agent]
Agent: "Based on the materials and design parameters, I estimate..."
```

## Integration Features

### Seamless Platform Integration

- **Context Preservation**: Agents understand your current workflow state
- **Material Awareness**: Agents know what materials you've selected
- **Workflow Continuity**: Agents can guide you through the design process
- **Real-time Updates**: Changes made through agents update the platform state

### Fallback Options

- If the multi-agent system is unavailable, the platform falls back to the traditional AI assistant
- You can switch between chat modes at any time
- Both systems share the same conversation history

## Troubleshooting

### Multi-Agent System Offline

If you see "❌ Multi-agent system offline":

1. Check that you have the required API keys in your `.env` file
2. Verify dependencies are installed: `pip install -r cell_development_requirements.txt`
3. Start the multi-agent server: `python start_multi_agent.py`
4. Click "🔄 Refresh Status" in the chat interface

### Common Issues

**ImportError: No module named 'google.adk'**
```bash
pip install google-adk==1.10.0
```

**Connection Error**
- Ensure the agent server is running on port 9003
- Check your firewall settings
- Verify the `.env` configuration

**API Key Issues**
- Ensure your Anthropic API key is valid and has sufficient credits
- Check the `.env` file format (no quotes around values)

## Advanced Configuration

### Custom Models

You can use different models by updating your `.env` file:

```bash
# Use OpenAI instead of Anthropic
DEFAULT_MODEL=openai/gpt-4o-mini

# Use Google's Gemini
DEFAULT_MODEL=gemini-2.5-pro
```

### Custom Ports

Change the default ports if needed:

```bash
AGENT_PORT=9005
MCP_PORT=9006
```

### Database Configuration

For persistent storage of cell designs:

```bash
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=cell_design
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│                 Streamlit App                   │
│                (Port 8501)                     │
└─────────────────┬───────────────────────────────┘
                  │ HTTP Requests
┌─────────────────▼───────────────────────────────┐
│           Multi-Agent Router                    │
│              (Port 9003)                       │
├─────────────────────────────────────────────────┤
│  🎯 Task Coordinator  │  🔧 Cell Designer      │
│  📚 Cell Library      │  📊 Cell Simulator     │
└─────────────────┬───────────────────────────────┘
                  │ MCP Tools
┌─────────────────▼───────────────────────────────┐
│              MCP Server                         │
│              (Port 9004)                       │
│  • Cell Design Tools  • Database Tools         │
│  • Simulation Tools   • Analysis Tools         │
└─────────────────────────────────────────────────┘
```

### Folder Structure

```
cell-development-platform/
├── adk_agent/                    # Multi-agent system
│   ├── agent.py                  # Main agent orchestrator
│   └── sub_agents/               # Individual agents
│       ├── cell_designer_agent/
│       ├── cell_library_agent/
│       └── cell_simulation_agent/
├── mcp_server/                   # MCP tools server
│   ├── cell_design_mcp.py       # Main MCP server
│   └── cell_designer/           # Cell design tools
├── modules/
│   └── multi_agent_chat.py      # Chat interface
├── start_platform.py            # Complete launcher
├── start_multi_agent.py         # Agent server only
└── .env.template                # Configuration template
```

## Support

For issues with the multi-agent integration:

1. Check the console output for error messages
2. Verify your `.env` configuration
3. Ensure all dependencies are installed
4. Test with the traditional AI first to isolate issues

The multi-agent system enhances the platform's capabilities but the core Cell Development Platform functionality remains available even if the agents are offline.