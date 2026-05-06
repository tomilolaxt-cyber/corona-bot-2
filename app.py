from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from dotenv import load_dotenv
from corona_data import CORONA_COMPREHENSIVE
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import json

# Load environment variables
load_dotenv('corona.env')
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'corona-school-bot-secret-key-2026')
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, name, email, picture):
        self.id = id
        self.name = name
        self.email = email
        self.picture = picture

# In-memory user storage (in production, use a database)
users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

def generate_response(user_message):
    """Generate intelligent response based on comprehensive Corona Schools knowledge"""
    message = user_message.lower().strip()
    data = CORONA_COMPREHENSIVE
    
    # Greeting
    if any(word in message for word in ['hi', 'hello', 'hey', 'greetings']):
        return "Hello! Welcome to Corona School Bot. I have comprehensive information about all Corona Schools campuses, leadership, curriculum, fees, and more. What would you like to know?"
    
    # History and founding
    if any(word in message for word in ['history', 'founded', 'established', 'when', 'how old', 'years']):
        return f"""**Corona Schools History:**

• Founded: {data['history']['founded']}
• Incorporated: {data['history']['incorporated']}
• Founding Chairman: {data['history']['founding_chairman']}
• Total Alumni: {data['history']['total_alumni']}
• Staff: {data['history']['staff_count']}
• Heritage: 70 years of educational excellence in Nigeria"""
    
    # Leadership and governance
    if any(word in message for word in ['chairman', 'ceo', 'director', 'leadership', 'governance', 'who leads']):
        gov = data['governance']
        return f"""**Corona Schools Leadership (2026):**
aqawdszADFV VDX VCSX
**Governing Board:**
• Chairman: {gov['chairman']}
• Previous Chairman: {gov['previous_chairman']}

**Executive Team:**
• CEO: {gov['ceo']}
• Director of Education: {gov['director_of_education']}
• Finance Controller: {gov['finance_controller']}
• Head of Corporate Services: {gov['head_corporate_services']}
• HR Manager: {gov['hr_manager']}
• Infrastructure Manager: {gov['infrastructure_manager']}

**Office Location:** {gov['office_location']}"""
    
    # Ikoyi schools
    if 'ikoyi' in message:
        nursery = data['schools']['ikoyi_day_nursery']
        primary = data['schools']['ikoyi_primary']
        return f"""**Corona Schools, Ikoyi:**

**Day Nursery:**
• Head: {nursery['head']}
• Location: {nursery['location']}
• Method: {nursery['method']}
• Description: {nursery['description']}

**Primary School:**
• Head: {primary['head']}
• Location: {primary['location']}
• Established: {primary['established']}
• Students: {primary['students']}
• Houses: {', '.join(primary['houses'])}
• Notable Alumni: {primary['notable_alumni']}
• Curriculum: {primary['curriculum']}"""
    
    # Victoria Island
    if 'victoria' in message or 'vi ' in message:
        school = data['schools']['victoria_island']
        return f"""**{school['name']}:**

• Head: {school['head']}
• Location: {school['location']}
• Established: {school['established']}
• Students: {school['students']}
• Classrooms: {school['classrooms']}
• Demographic: {school['demographic']}"""
    
    # Gbagada
    if 'gbagada' in message:
        school = data['schools']['gbagada']
        return f"""**{school['name']}:**

• Head: {school['head']}
• Location: {school['location']}
• Sections: {', '.join(school['sections'])}
• Specialty: {school['specialty']}"""
    
    # Lekki
    if 'lekki' in message:
        primary = data['schools']['lekki_primary']
        secondary = data['schools']['lekki_secondary']
        return f"""**Corona Schools, Lekki:**

**Primary School:**
• Name: {primary['name']}
• Head: {primary['head']}
• Location: {primary['location']}
• Established: {primary['established']} (Permanent site: {primary['permanent_site']})
• Specialty: {primary['specialty']}
• Competitions: {primary['competitions']}

**Day Secondary School:**
• Name: {secondary['name']}
• Head: {secondary['head']}
• Location: {secondary['location']}
• Established: {secondary['established']}
• Type: {secondary['type']}
• Serves: {secondary['serves']}"""
    
    # Agbara
    if 'agbara' in message:
        school = data['schools']['agbara_secondary']
        return f"""**{school['name']}:**

• Head: {school['head']}
• Location: {school['location']}
• Established: {school['established']}
• Type: {school['type']}
• Accreditation: {school['accreditation']}
• Technology: {school['wifi']}, {school['learning_platform']}

**Special Recognition:** Only secondary school in Africa with NEASC accreditation"""
    
    # Curriculum
    if any(word in message for word in ['curriculum', 'subjects', 'program', 'what do you teach', 'scheme of work']):
        curr = data['curriculum']
        return f"""**Corona Schools Curriculum:**

**Early Years (Montessori Method):**
• Creche 1 (0-18 months): {curr['early_years']['age_groups']['creche_1']['focus']}
• Creche 2 (2 years): {', '.join(curr['early_years']['age_groups']['creche_2']['subjects'][:5])}
• Nursery One (3 years): {', '.join(curr['early_years']['age_groups']['nursery_one']['subjects'][:4])}
• Nursery Two (4 years): {', '.join(curr['early_years']['age_groups']['nursery_two']['subjects'][:4])}

**Primary ({curr['primary']['system']}):**
• Core: {', '.join(curr['primary']['core_subjects'])}
• Languages: {', '.join(curr['primary']['languages'])}
• Technical: {', '.join(curr['primary']['technical'][:3])}

**Secondary:**
• Local Exams: {', '.join(curr['secondary']['local_exams'])}
• International: {', '.join(curr['secondary']['international_exams'])}
• Special: {curr['secondary']['special_program']}"""
    
    # Fees
    if any(word in message for word in ['fee', 'cost', 'tuition', 'price', 'how much', 'payment']):
        fees = data['fees_2024_2025']
        return f"""**Corona Schools Fees (2024/2025):**

**Creche/Playschool:**
• Annual: {fees['creche_playschool']['annual']}
• Per Term: {fees['creche_playschool']['per_term']}
• Application: {fees['creche_playschool']['application_form']}

**Nursery:**
• Annual: {fees['nursery']['annual']}
• Per Term: {fees['nursery']['per_term']}
• Application: {fees['nursery']['application_form']}

**Primary:**
• Annual: {fees['primary']['annual']}
• Per Term: {fees['primary']['per_term']}
• Application: {fees['primary']['application_form']}

**Secondary Day:**
• Annual: {fees['secondary_day']['annual']}
• Per Term: {fees['secondary_day']['per_term']}

**Secondary Boarding:**
• Annual: {fees['secondary_boarding']['annual']}
• Per Term: {fees['secondary_boarding']['per_term']}"""
    
    # Activities
    if any(word in message for word in ['activities', 'sports', 'clubs', 'co-curricular', 'extracurricular']):
        activities = data['co_curricular']
        return f"""**Co-Curricular Activities:**

**Sports:** {', '.join(activities['sports'][:8])}

**Academic Clubs:** {', '.join(activities['academic_clubs'])}

**Creative Arts:** {', '.join(activities['creative'])}

**Life Skills:** {', '.join(activities['life_skills'][:5])}

**Languages:** {', '.join(activities['languages'])}

**Special Achievements:** {activities['special_achievements']}"""
    
    # Calendar
    if any(word in message for word in ['calendar', 'term', 'resumption', 'when does school', 'holiday']):
        cal = data['academic_calendar_2025_2026']
        return f"""**Academic Calendar 2025/2026:**

**First Term:** {cal['first_term']['period']}
Events: {', '.join(cal['first_term']['events'][:3])}

**Second Term:** {cal['second_term']['period']}
Events: {', '.join(cal['second_term']['events'][:3])}

**Third Term:** {cal['third_term']['period']}
Events: {', '.join(cal['third_term']['events'])}"""
    
    # Accreditations
    if any(word in message for word in ['accreditation', 'award', 'certified', 'recognition', 'neasc', 'acca']):
        return "**Corona Schools Accreditations & Awards:**\n\n• " + "\n• ".join(data['accreditations'])
    
    # Staff/Employment
    if any(word in message for word in ['staff', 'teacher', 'employment', 'job', 'work', 'salary', 'recruit']):
        staff = data['staff']
        return f"""**Corona Schools Staff Information:**

• Total Staff: {staff['total']}
• Recruitment Program: {staff['recruitment_program']}
• Requirements: {staff['requirements']}
• Average Salary: {staff['average_salary']}
• Benefits: {', '.join(staff['benefits'])}"""
    
    # CSR
    if any(word in message for word in ['csr', 'social responsibility', 'community', 'scholarship', 'public school']):
        csr = data['csr']
        return f"""**Corporate Social Responsibility:**

• Out-of-School Initiative: {csr['out_of_school_initiative']}
• Public School Adoption: {csr['public_school_adoption']}
• Scholarships: {csr['scholarships']}"""
    
    # Facilities
    if any(word in message for word in ['facilities', 'infrastructure', 'building', 'library', 'lab']):
        fac = data['facilities']
        return f"""**Corona Schools Facilities:**

**Technology:** {', '.join(fac['technology'])}

**Safety & Security:** {', '.join(fac['safety'])}

**Sports Facilities:** {', '.join(fac['sports'])}

**Learning Spaces:** {', '.join(fac['learning'])}"""
    
    # Mission/Vision
    if any(word in message for word in ['mission', 'vision', 'values', 'purpose', 'goal']):
        return f"""**Corona Schools Mission & Vision:**

**Mission:** {data['mission']}

**Vision:** {data['vision']}

**Core Values:** {', '.join(data['core_values'])}"""
    
    # About/General
    if any(word in message for word in ['about', 'what is corona', 'tell me about']):
        return f"""**About Corona Schools Trust Council:**

Founded in {data['history']['founded']}, Corona Schools has {data['history']['current_year'] - data['history']['founded']} years of educational excellence in Nigeria.

**Key Stats:**
• {len(data['schools'])} schools across Lagos and Ogun States
• {data['history']['total_alumni']} alumni
• {data['history']['staff_count']} staff members

**Mission:** {data['mission']}

**Vision:** {data['vision']}"""
    
    # Default
    return """I can help you with comprehensive information about Corona Schools including:

• Leadership & Governance (2026 updates)
• All 7 School Locations & Heads
• Curriculum & Schemes of Work
• Fees & Admissions
• Co-Curricular Activities
• Academic Calendar 2025/2026
• Accreditations & Awards
• Staff & Employment
• Facilities & Infrastructure
• CSR Initiatives

What would you like to know?"""


@app.route('/')
def index():
    return render_template('index.html', user=current_user if current_user.is_authenticated else None)

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('callback', _external=True)]
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = url_for('callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Handle Google OAuth callback"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [url_for('callback', _external=True)]
                }
            },
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            state=session['state']
        )
        flow.redirect_uri = url_for('callback', _external=True)
        
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        request_session = google_requests.Request()
        
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            GOOGLE_CLIENT_ID
        )
        
        # Create user
        user = User(
            id=id_info['sub'],
            name=id_info.get('name', ''),
            email=id_info.get('email', ''),
            picture=id_info.get('picture', '')
        )
        
        users[user.id] = user
        login_user(user)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        print(f"Login error: {e}")
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/user')
def get_user():
    """Get current user info"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'name': current_user.name,
            'email': current_user.email,
            'picture': current_user.picture
        })
    return jsonify({'authenticated': False})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
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
