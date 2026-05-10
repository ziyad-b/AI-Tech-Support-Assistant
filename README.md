# AI Tech Support Assistant

AI Tech Support Assistant is a simple Streamlit web application that helps users understand and troubleshoot common technology problems. A user enters a problem, and the app uses the Groq API to generate a beginner-friendly support response.

## Project Idea

Many users face common technical issues such as slow laptops, unstable WiFi, overheating phones, printer problems, and blank screens. This project provides a chat-style AI assistant that explains possible causes, safe troubleshooting steps, risk level, and a helpful recommendation.

## Objectives

- Build a clean Python web application using Streamlit.
- Use a free LLM API through the Groq Python SDK.
- Keep the API key private by storing it in a `.env` file.
- Generate technical support answers that are clear for beginners.
- Encourage safe and responsible troubleshooting.
- Provide a simple ChatGPT-style interface with message bubbles.
- Support English and Arabic UI alignment.

## Tools Used

- Python
- Streamlit
- Groq Python SDK
- Groq LLM API
- python-dotenv

## Project Files

- `app.py`: Main Streamlit application.
- `styles.css`: Custom CSS for the chat interface, layout, buttons, and Arabic/English alignment.
- `.streamlit/config.toml`: Streamlit theme and toolbar settings.
- `requirements.txt`: Required Python packages.
- `.env.example`: Example environment variable file.
- `README.md`: Project documentation.

## How to Run the Project

1. Open the project folder in the terminal.

```bash
cd "Project file Path"
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages.

```bash
python -m pip install -r requirements.txt
```

If `python` does not work on Windows, use:

```bash
py -m pip install -r requirements.txt
```

4. Create a `.env` file in the project folder.

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

5. Run the Streamlit application.

```bash
python -m streamlit run app.py
```

If `python` does not work on Windows, use:

```bash
py -m streamlit run app.py
```

6. Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Main Features

- Chat-style interface with user and assistant bubbles.
- Press Enter in the chat box to send a problem.
- English and Arabic UI language switch.
- Correct left-to-right alignment for English and right-to-left alignment for Arabic.
- The assistant answers in the same language as the user's problem, even if the UI language is different.
- Example problem buttons for quick testing.

## Example Inputs

- My laptop is very slow
- My WiFi disconnects frequently
- My phone overheats while charging
- My printer is not printing
- My computer screen is black

## Example Output

For the input:

```text
My WiFi disconnects frequently
```

The app may return:

```text
Problem Summary:
Your WiFi connection keeps dropping during use.

Possible Causes:
- Weak signal from the router
- Router firmware or configuration issue
- Interference from other devices
- Problem with the computer or phone network adapter

Step-by-Step Solutions:
1. Move closer to the router and test the connection.
2. Restart the router and your device.
3. Forget the WiFi network and reconnect.
4. Check if other devices have the same issue.
5. Contact your internet provider or a technician if the issue continues.

Risk Level:
Low

Helpful Recommendation:
If the problem happens on all devices, the router or internet service may need professional support.
```

## Responsible AI Practices

- The assistant gives general troubleshooting guidance, not guaranteed repairs.
- The prompt instructs the AI to avoid dangerous electrical or hardware repair instructions.
- Users are advised to contact a qualified technician for serious, unsafe, electrical, overheating, or hardware-related problems.
- The app is designed for educational use and beginner-friendly support.
- API keys are kept outside the code in a private `.env` file.


## Author Information

Made By: Ziyad Bandar Alotaibi

Course: SELECTED TOPICS IN COMPUTER SCIENCE 491

Instuctor: Dr. Mohammed Al-Gabri

Date: May 2026

Project: AI Tech Support Assistant

## License

Educational use only.

## Acknowledgments

Groq - For providing access to fast LLM API services

Meta Llama - For the Llama model used through Groq

Streamlit - For the web framework
