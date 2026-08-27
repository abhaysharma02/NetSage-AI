# NetSage AI

NetSage AI is an AI-based network diagnostic system that identifies common network problems and provides possible root causes and recommendations.

## Technologies Used

- Python
- Ollama Local AI
- Streamlit
- Computer Networking

## Project Links

### GitHub Repository
https://github.com/abhaysharma02/NetSage-AI

### Live Streamlit Application
https://netsage-ai-bvclxjststt39jzzd5qn7c.streamlit.app/

## Project Structure

- app.py - Streamlit interface
- src/checker.py - Network rule checker
- src/ai_engine.py - AI diagnosis engine
- src/llm_engine.py - Local Ollama integration
- src/report_generator.py - Report generation
- src/main.py - Main execution file
- data/ - Network diagnostic cases
- logs/ - Generated results
- prompts/ - AI prompts

## How to Run

python src/main.py

To start the Streamlit interface:

python -m streamlit run app.py

## Project Status

The system successfully processes 30 network diagnostic cases using deterministic rules and local AI-based diagnosis.
