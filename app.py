from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load corona.env
load_dotenv('corona.env')

app = Flask(__name__)
CORS(app)

# Corona Schools Knowledge Base - Updated 2026
CORONA_KNOWLEDGE = {
    "leadership": {
        "trust_council": {
            "chairman": "Mr. Olaniyi Yusuf (Appointed early 2026)",
            "director_of_education": "Mrs. Adetokunbo Matilukuro",
            "ceo": "Mrs. Adeyoyin Adesina"
        },
        "schools": {
            "ikoyi_primary": {
                "head": "Mrs. Funlola Olorunishola (Since 2022)",
                "location": "6 Mekunwen Road, Ikoyi",
                "houses": ["Crane", "Weaver", "Kingfisher", "Heron"],
                "curriculum": "Blend of Nigerian National Curriculum and British National Curriculum"
            },
            "lekki_primary": {
                "head": "Mrs. Grace Omo-Egbekuse",
                "location": "Abijo GRA, Lekki",
                "focus": "Technology and innovation, robotics competitions (Pi Wars)"
            },
            "lekki_secondary": {
                "principal": "Mr. Amoo",
                "location": "Abijo GRA, Lekki",
                "type": "Day Secondary School"
            },
            "agbara_secondary": {
                "principal": "Mr. Chijioke Anyanwu",
                "location": "Agbara Estate",
                "type": "Boarding Secondary School",
                "accreditation": "NEASC Accredited - only in Africa"
            },
            "gbagada": {
                "location": "Gbagada, Lagos",
                "specialty": "Foremost Rugby School in Lagos State, 4-time trophy winner"
            }
        }
    },
    "general_info": {
        "years_of_excellence": 70,
        "total_schools": 8,
        "total_students": "35,000+",
        "staff_count": 668,
        "mission": "Provide world-class education with high moral and ethical values",
        "vision": "Be Nigeria's leading educational institution producing well-rounded young men and women"
    },
    "curriculum": {
        "nursery": "Montessori method",
        "primary": "Blend of Nigerian and International Primary Curriculum (IPC)",
        "secondary": "Blend of Nigerian and British curricula"
    },
    "accreditations": [
        "NEASC Accreditation (Corona Secondary School Agbara - only in Africa)",
        "ACCA Foundation Level (only secondary school in Nigeria)",
        "British Council Community Initiative Award 2019",
        "Microsoft Showcase/Incubator Schools",
        "158 Microsoft Innovative Experts",
        "187 Microsoft Certified Experts"
    ],
    "activities": [
        "Music", "Taekwondo", "Athletics", "Ballet", "Golf", "Cheerleading",
        "Dance", "Basketball", "Drama", "French", "Chess", "STEAM",
        "Model United Nations", "Public Speaking", "Debating", "Cooking Club",
        "Rugby", "German", "Hausa", "Igbo", "Yoruba", "Reading", "Football",
        "Robotics (Pi Wars)"
    ],
    "admissions": {
        "year": "2025/2026",
        "levels": "Year 7-11",
        "types": ["Boarding", "Day School"],
        "programs": ["Regular", "Scholarship"]
    }
}

def generate_response(user_message):
    """Generate intelligent response based on Corona Schools knowledge"""
    message = user_message.lower().strip()
    
    # Leadership questions
    if any(word in message for word in ['chairman', 'ceo', 'director', 'leadership', 'who leads', 'who runs']):
        return f"""**Corona Schools Leadership (2026):**

**Trust Council:**
• Chairman: {CORONA_KNOWLEDGE['leadership']['trust_council']['chairman']}
• Director of Education: {CORONA_KNOWLEDGE['leadership']['trust_council']['director_of_education']}
• CEO/Trust Council Secretary: {CORONA_KNOWLEDGE['leadership']['trust_council']['ceo']}

**School Heads:**
• Ikoyi Primary: {CORONA_KNOWLEDGE['leadership']['schools']['ikoyi_primary']['head']}
• Lekki Primary: {CORONA_KNOWLEDGE['leadership']['schools']['lekki_primary']['head']}
• Lekki Secondary: Principal {CORONA_KNOWLEDGE['leadership']['schools']['lekki_secondary']['principal']}
• Agbara Secondary: Principal {CORONA_KNOWLEDGE['leadership']['schools']['agbara_secondary']['principal']}"""
    
    # Ikoyi questions
    if 'ikoyi' in message:
        school = CORONA_KNOWLEDGE['leadership']['schools']['ikoyi_primary']
        return f"""**Corona School, Ikoyi:**

• Head of School: {school['head']}
• Location: {school['location']}
• Curriculum: {school['curriculum']}
• Houses: {', '.join(school['houses'])}
• Known for: "Total Child" approach and strong tradition
• Type: Flagship primary school"""
    
    # Lekki questions
    if 'lekki' in message:
        primary = CORONA_KNOWLEDGE['leadership']['schools']['lekki_primary']
        secondary = CORONA_KNOWLEDGE['leadership']['schools']['lekki_secondary']
        return f"""**Corona Schools, Lekki:**

**Primary School:**
• Head of School: {primary['head']}
• Location: {primary['location']}
• Focus: {primary['focus']}

**Day Secondary School (CDSS):**
• Principal: {secondary['principal']}
• Location: {secondary['location']}
• Type: {secondary['type']}
• Context: Day-school option for families in Lekki/Ajah axis"""
    
    # Agbara questions
    if 'agbara' in message:
        school = CORONA_KNOWLEDGE['leadership']['schools']['agbara_secondary']
        return f"""**Corona Secondary School, Agbara:**

• Principal: {school['principal']}
• Location: {school['location']}
• Type: {school['type']}
• Accreditation: {school['accreditation']}
• Special: Only secondary school in Africa with NEASC accreditation"""
    
    # Gbagada questions
    if 'gbagada' in message:
        school = CORONA_KNOWLEDGE['leadership']['schools']['gbagada']
        return f"""**Corona School, Gbagada:**

• Location: {school['location']}
• Specialty: {school['specialty']}
• Known for: Excellence in Rugby sports"""
    
    # About/General info
    if any(word in message for word in ['about', 'what is corona', 'tell me about', 'introduce']):
        info = CORONA_KNOWLEDGE['general_info']
        return f"""**About Corona Schools:**

Corona Schools' Trust Council is a prestigious educational institution in Nigeria with {info['years_of_excellence']} years of excellence.

**Key Stats:**
• {info['total_schools']} schools across Nigeria
• {info['total_students']} students (current and past)
• {info['staff_count']} experienced staff members

**Mission:** {info['mission']}

**Vision:** {info['vision']}"""
    
    # Curriculum questions
    if any(word in message for word in ['curriculum', 'subjects', 'program', 'what do you teach']):
        curr = CORONA_KNOWLEDGE['curriculum']
        return f"""**Corona Schools Curriculum:**

**Nursery:** {curr['nursery']}

**Primary:** {curr['primary']}

**Secondary:** {curr['secondary']}

All programs focus on developing well-rounded students with strong academic foundations and moral values."""
    
    # Activities questions
    if any(word in message for word in ['activities', 'sports', 'clubs', 'co-curricular', 'extracurricular']):
        activities = CORONA_KNOWLEDGE['activities']
        return f"""**Co-Curricular Activities at Corona Schools:**

We offer 30+ diverse activities including:

{', '.join(activities[:15])}

And many more! These activities develop leadership, teamwork, creativity, and diverse talents."""
    
    # Accreditations
    if any(word in message for word in ['accreditation', 'award', 'certified', 'recognition']):
        accreds = CORONA_KNOWLEDGE['accreditations']
        return "**Corona Schools Accreditations & Awards:**\n\n• " + "\n• ".join(accreds)
    
    # Admissions
    if any(word in message for word in ['admission', 'enroll', 'register', 'apply', 'how to join']):
        adm = CORONA_KNOWLEDGE['admissions']
        return f"""**Admissions Information:**

• Academic Year: {adm['year']}
• Levels: {adm['levels']}
• School Types: {', '.join(adm['types'])}
• Programs: {', '.join(adm['programs'])}

Entrance Examination Registration is ongoing. Contact the admissions office for more details."""
    
    # Default response
    return f"""I can help you with information about Corona Schools including:

• Leadership and school heads
• School locations (Ikoyi, Lekki, Agbara, Gbagada)
• Curriculum and programs
• Admissions process
• Co-curricular activities
• Accreditations and awards
• General information

What would you like to know?"""

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
        
        # Get response from knowledge base
        bot_response = generate_response(user_message)
        
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
    return jsonify({'success': True, 'message': 'Chat cleared'})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
