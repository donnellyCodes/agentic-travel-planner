# Agentic RAG Travel Budget Planner

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green?logo=langchain)
![OpenAI GPT-4o](https://img.shields.io/badge/OpenAI-GPT--4o-black?logo=openai)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?logo=fastapi)

An intelligent, agentic travel assistant that creates personalized travel plans based on your destination, budget, and trip duration. This project leverages a Retrieval-Augmented Generation (RAG) architecture where an LLM-powered agent uses live APIs as tools to gather information and reason about it.

---

## 🚀 Core Features

This agent acts as a smart assistant that:

- Accepts a destination, total budget, and trip duration as input.
- Dynamically calls external APIs (tools) to retrieve real-time data for hotels and weather.
- Reasons about the data to create a practical, personalized travel plan with a cost breakdown.
- Provides a clear, summarized response with actionable suggestions.

| Feature               | Description                                                                                 |
|-----------------------|---------------------------------------------------------------------------------------------|
| User Inputs           | Country/City, Budget (e.g. $1000), Duration (e.g. 5 days)                                  |
| RAG Retrieval         | Fetches live data from hotel search APIs (Booking.com) and weather APIs.                    |
| Agentic Reasoning     | Calculates a daily budget, filters affordable hotels, and summarizes weather.               |
| Response Output       | Suggests hotels, provides a cost estimate, and includes weather information.                |

---

## 💡 Demonstration

**Sample interaction via CLI:**

```
You: I want to go to Tokyo, Japan for 5 days with a $1500 budget.

> Entering new AgentExecutor chain...

I need to plan a trip to Tokyo, Japan for 5 days with a total budget of $1500.

1.  **Deconstruct the Query**: Destination: Tokyo, Japan. Budget: $1500. Duration: 5 days.
2.  **Calculate Accommodation Budget**: A reasonable hotel budget is 45% of the total. Max nightly price = ($1500 * 0.45) / 5 days = $135/night.
3.  **Search for Hotels**: I will call the `find_hotels` tool with `city='Tokyo'` and `max_price=135`.
4.  **Estimate Daily Spend**: I will call the `get_daily_spend_estimate` tool for Tokyo.
5.  **Get Weather**: I will call the `get_weather_info` tool for Tokyo.
6.  **Synthesize Plan**: Combine all results into a final response.

Action: find_hotels(city='Tokyo', max_price=135)
...
Action: get_daily_spend_estimate(city='Tokyo')
...
Action: get_weather_info(city='Tokyo')
...
I have gathered all the necessary information to create a travel plan.

> Finished chain.

Agent: Here is a suggested travel plan for your trip to Tokyo based on a $1500 budget for 5 days:

* **Budget Overview**:
    * **Max Hotel Budget**: I have allocated approximately $135 per night for accommodation.
    * **Estimated Daily Spend**: For food and local transport in Tokyo, a reasonable daily budget is around $60-$80.

* **Hotel Suggestions (under $135/night)**:
    - **HOTEL MYSTAYS Ueno East** (Price: ~$125/night, Rating: 8.1/10)
    - **Sotetsu Fresa Inn Higashi Shinjuku** (Price: ~$130/night, Rating: 8.2/10)
    - **APA Hotel Asakusa Ekimae** (Price: ~$110/night, Rating: 7.9/10)

* **Weather in Tokyo**:
    The current weather in Tokyo is: Mainly clear with a temperature of 24°C.

* **Total Estimated Cost**:
    * Accommodation: ~$625 (for 5 nights)
    * Food & Transport: ~$350 (at $70/day)
    * **Total**: ~**$975**. This leaves you with a comfortable buffer in your budget for activities and shopping.
```

---

## 🛠️ Tech Stack

- **Backend Logic:** Python
- **LLM Framework:** 🦜️🔗 LangChain
- **LLM:** OpenAI GPT-4o
- **API Server:** FastAPI
- **Dependencies:** python-dotenv, requests, uvicorn

---

## ⚙️ Setup and Installation

Follow these steps to set up the project locally.

### 1. Prerequisites

- Python 3.10+
- An OpenAI API Key.
- A RapidAPI Account and Key.

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/travel-agentic-rag.git
cd travel-agentic-rag
```

### 3. Create and Activate a Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up API Keys

Create a file named `.env` by copying the example:

```bash
cp .env.example .env
```

Open the `.env` file and add your secret keys:

```ini
# .env
OPENAI_API_KEY="sk-..."
RAPIDAPI_KEY="..."
```

#### Get Your Keys

- **OpenAI:** Get your key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- **RapidAPI:**
    - Sign up at [RapidAPI.com](https://rapidapi.com/).
    - Subscribe to the Booking Scraper API on the free BASIC plan.
    - Find your X-RapidAPI-Key on the API's "Endpoints" page.

> **Security Note:** The `.env` file is included in `.gitignore` to prevent you from accidentally committing your secret keys.

---

## ▶️ How to Run

You can run the agent in two ways: as a command-line tool or as a FastAPI web server.

### 1. Run the Command-Line Interface (CLI)

```bash
python app.py cli
```
You will be prompted to enter your travel query. Type `exit` to quit.

### 2. Run the FastAPI Server

```bash
uvicorn app:app --reload
```
- The server will be running at [http://127.0.0.1:8000](http://127.0.0.1:8000).
- Access the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Example POST request:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/plan-trip' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "destination": "Rome, Italy",
  "budget": 1000,
  "duration_days": 4
}'
```

---

## 🧠 Agent Logic Flow

The agent's "thought process" is guided by a system prompt in `app.py`:

1. **Deconstruct User Query:** Identify destination, total_budget, and duration_days.
2. **Calculate Budgets:** Allocate a portion of the total budget for hotels (e.g., 45%).
3. **Invoke Tools:**
    - `find_hotels(city, max_price)`: Booking Scraper API.
    - `get_weather_info(city)`: Open-Meteo API.
    - `get_daily_spend_estimate(city)`: Mock estimation tool.
4. **Synthesize the Plan:** Aggregate the information.
5. **Generate Final Response:** Present a comprehensive travel plan.

---

## 📁 Project Structure

```
/travel-agentic-rag
|-- .env                 # Secret API keys (ignored by Git)
|-- .env.example         # Template for environment variables
|-- app.py               # Main application logic: Agent setup, FastAPI server, CLI runner
|-- tools.py             # Tools (API-calling functions) for the agent
|-- requirements.txt     # Python dependencies
`-- README.md            # You are here!
```

---

## 🗺️ Future Improvements

- **Integrate Real Cost of Living API:** Replace the mock `get_daily_spend_estimate` with a real API like Numbeo.
- **Add Flight Search Tool:** Incorporate a flight search API (e.g., Skyscanner).
- **Build a Web UI:** Create a frontend using Streamlit or React.
- **Implement Caching:** Store API responses for popular destinations.
- **Add Conversation Memory:** Enable the agent to remember conversation context for follow-ups.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.