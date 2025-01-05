# Smart Meal Planner

An intelligent meal planning system that uses LangGraph and LangChain to process shopping receipts and existing inventory to generate personalized meal plans.

## Features

- OCR processing of shopping receipts (images/PDFs)
- Inventory management
- Intelligent meal planning with LLM
- Modular architecture with sub-graphs
- State management and checkpointing
- Human-in-the-loop capabilities
- Streaming and replay support
- LLM provider agnostic

## Project Structure

```
meal_planner/
├── config/                 # Configuration files
├── core/                   # Core application logic
│   ├── llm/               # LLM abstraction layer
│   ├── state/             # State management
│   └── schemas/           # Pydantic models
├── agents/                # Agent definitions
│   ├── receipt_parser/    # Receipt processing agent
│   ├── inventory/         # Inventory management agent
│   └── meal_planner/      # Meal planning agent
├── tools/                 # Custom tools
├── graphs/                # LangGraph definitions
├── storage/              # Data persistence
└── ui/                   # Streamlit interface
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
streamlit run meal_planner/ui/app.py
```

## Architecture

The application uses a modular architecture with multiple sub-graphs:

1. Receipt Processing Graph
   - OCR processing
   - Item extraction
   - Categorization

2. Inventory Management Graph
   - Item tracking
   - Stock updates
   - Expiry management

3. Meal Planning Graph
   - Recipe generation
   - Nutritional balance
   - Preference matching

Each graph implements proper state management, checkpointing, and human-in-the-loop capabilities where needed. 