# Corona Bot - AI Assistant for Corona Schools

Corona Bot is an intelligent AI-powered chatbot that provides comprehensive information about Corona Schools. Built with Python Flask backend and powered by Google's Gemini AI.

## Features

- 🤖 **AI-Powered**: Uses Google Gemini AI for intelligent responses
- 💬 **Real-time Chat**: Instant responses to user queries
- 📚 **Comprehensive Knowledge**: Extensive information about Corona Schools
- 🎨 **Modern UI**: Beautiful, responsive interface
- 📱 **Mobile Friendly**: Works seamlessly on all devices
- ⚡ **Fast & Reliable**: Quick response times with error handling

## Project Structure

```
corona-bot/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (with API key)
├── .env.example          # Environment variables template
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # CSS styling
    └── script.js         # Frontend JavaScript
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API Key

### 2. Installation

1. Clone or download this project
2. Navigate to the project directory:
   ```bash
   cd corona-bot
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

Open your browser and navigate to `http://localhost:5000` to start chatting with Corona Bot!

## Usage

1. **Ask Questions**: Type any question about Corona Schools in the chat input
2. **Quick Links**: Use the quick question buttons on the sidebar for common topics
3. **Clear Chat**: Click the "Clear Chat" button to start a new conversation
4. **Mobile**: The interface is fully responsive and works on mobile devices

## Topics Corona Bot Can Help With

- About Corona Schools
- Mission and Vision
- Admissions and Registration
- Curriculum and Programs
- Facilities and Infrastructure
- Co-curricular Activities
- Accreditations and Awards
- Staff Information
- Alumni Network
- And much more!

## Adding Schemes of Work

To add schemes of work documents:

1. Update the `CORONA_CONTEXT` variable in `app.py` with curriculum details
2. Add document content to the knowledge base
3. Restart the application

Example:
```python
CORONA_CONTEXT = """
... existing content ...

SCHEMES OF WORK:
[Add your schemes of work details here]
"""
```

## Customization

### Modify Styling
Edit `static/styles.css` to customize colors, fonts, and layout

### Update Knowledge Base
Edit the `CORONA_CONTEXT` variable in `app.py` to add or modify information

## Troubleshooting

### API Key Error
- Ensure your `.env` file is in the project root
- Verify the API key is correct
- Check that the API key has Gemini API enabled

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port number
```

### Module Not Found
Ensure you've activated the virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

## Future Enhancements

- Document upload for schemes of work
- Multi-language support
- User authentication
- Chat history persistence
- Advanced search functionality
- Integration with Corona Schools website
- Admin dashboard for knowledge base management

## Support

For issues or questions, please contact the development team.

## License

This project is proprietary to Corona Schools' Trust Council.
