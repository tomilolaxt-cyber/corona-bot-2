from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load corona.env instead of .env
load_dotenv('corona.env')

app = Flask(__name__)
CORS(app)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Corona Schools Knowledge Base
CORONA_CONTEXT = """
You are Corona Bot, an AI assistant for Corona Schools' Trust Council. You have comprehensive knowledge about Corona Schools.

CORONA SCHOOLS INFORMATION:
- 70 years of excellence in education
- 8 schools across Nigeria
- Over 35,000+ students (current and past)
- 668 experienced academic and non-academic staff
- Mission: Provide world-class education with high moral and ethical values
- Vision: Be Nigeria's leading educational institution producing well-rounded young men and women

SCHOOLS & LOCATIONS:
- Corona Secondary School Agbara (NEASC Accredited - only in Africa)
- Corona School Gbagada (foremost Rugby School in Lagos)
- Multiple primary and nursery schools

CURRICULUM:
- Nursery: Montessori method
- Primary: Blend of Nigerian and International Primary Curriculum (IPC)
- Secondary: Blend of Nigerian and British curricula

ACCREDITATIONS & AWARDS:
- NEASC Accreditation (Corona Secondary School Agbara)
- ACCA Foundation Level (only secondary school in Nigeria)
- British Council Community Initiative Award 2019
- Microsoft Showcase/Incubator Schools
- 158 Microsoft Innovative Experts
- 187 Microsoft Certified Experts

CO-CURRICULAR ACTIVITIES:
Music, Taekwondo, Athletics, Ballet, Golf, Cheerleading, Dance, Basketball, Drama, French, Chess, STEAM, Model United Nations, Public Speaking, Debating, Cooking Club, Rugby, and more.

ADMISSIONS:
- 2025/2026 admissions ongoing for Year 7-11
- Both Boarding & Day School options
- Entrance Examination Registration available
- Scholarship programs available

FACILITIES:
- Modern libraries
- Advanced technology infrastructure
- Sports facilities
- State-of-the-art learning spaces
- World-class infrastructure

When answering questions:
1. Be helpful and informative
2. Focus on Corona Schools information
3. If asked about something not in your knowledge base, acknowledge it and offer to help with Corona Schools topics
4. Be friendly and professional
5. Provide accurate information only
"""

# Initialize conversation history
conversation_history = []

def get_ai_response(user_message):
    """Get response from Gemini AI with Corona Schools context"""
    try:
        # Create the model with correct API version
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        
        # Send message with context
        full_prompt = f"{CORONA_CONTEXT}\n\nUser Question: {user_message}"
        response = model.generate_content(full_prompt)
        
        bot_response = response.text
        
        return bot_response
    
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get AI response
        bot_response = get_ai_response(user_message)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'success': True, 'message': 'Chat cleared'})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
