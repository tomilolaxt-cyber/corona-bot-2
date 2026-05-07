from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import random
import sqlite3
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from corona_data import CORONA_COMPREHENSIVE
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import google.generativeai as genai

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
gemini_model = None

def init_gemini():
    global gemini_model
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini AI initialized!")
        except Exception as e:
            print(f"Gemini init error: {e}")

init_gemini()

# Build Corona Schools context for Gemini
CORONA_CONTEXT = f"""You are Corona School Bot, an AI assistant for Corona Schools Trust Council in Nigeria.
You have deep knowledge about Corona Schools and you are helpful, friendly and professional.

Here is the comprehensive Corona Schools information you must use:

HISTORY: Founded {CORONA_COMPREHENSIVE['history']['founded']}, incorporated {CORONA_COMPREHENSIVE['history']['incorporated']}.
Founding Chairman: {CORONA_COMPREHENSIVE['history']['founding_chairman']}
Total Alumni: {CORONA_COMPREHENSIVE['history']['total_alumni']}, Staff: {CORONA_COMPREHENSIVE['history']['staff_count']}

LEADERSHIP 2026:
- Chairman: {CORONA_COMPREHENSIVE['governance']['chairman']}
- CEO: {CORONA_COMPREHENSIVE['governance']['ceo']}
- Director of Education: {CORONA_COMPREHENSIVE['governance']['director_of_education']}
- Finance Controller: {CORONA_COMPREHENSIVE['governance']['finance_controller']}

SCHOOLS:
- Ikoyi Day Nursery: Head {CORONA_COMPREHENSIVE['schools']['ikoyi_day_nursery']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['ikoyi_day_nursery']['location']}
- Ikoyi Primary: Head {CORONA_COMPREHENSIVE['schools']['ikoyi_primary']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['ikoyi_primary']['location']}, Houses: {', '.join(CORONA_COMPREHENSIVE['schools']['ikoyi_primary']['houses'])}
- Victoria Island: Head {CORONA_COMPREHENSIVE['schools']['victoria_island']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['victoria_island']['location']}
- Gbagada: Head {CORONA_COMPREHENSIVE['schools']['gbagada']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['gbagada']['location']}
- Lekki Primary: Head {CORONA_COMPREHENSIVE['schools']['lekki_primary']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['lekki_primary']['location']}
- Agbara Secondary: Head {CORONA_COMPREHENSIVE['schools']['agbara_secondary']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['agbara_secondary']['location']}, Type: {CORONA_COMPREHENSIVE['schools']['agbara_secondary']['type']}
- Lekki Secondary: Head {CORONA_COMPREHENSIVE['schools']['lekki_secondary']['head']}, Location: {CORONA_COMPREHENSIVE['schools']['lekki_secondary']['location']}

FEES 2024/2025:
- Creche/Playschool: {CORONA_COMPREHENSIVE['fees_2024_2025']['creche_playschool']['annual']} per year
- Nursery: {CORONA_COMPREHENSIVE['fees_2024_2025']['nursery']['annual']} per year
- Primary: {CORONA_COMPREHENSIVE['fees_2024_2025']['primary']['annual']} per year
- Secondary Day: {CORONA_COMPREHENSIVE['fees_2024_2025']['secondary_day']['annual']} per year
- Secondary Boarding: {CORONA_COMPREHENSIVE['fees_2024_2025']['secondary_boarding']['annual']} per year

ACADEMIC CALENDAR 2025/2026:
- First Term: {CORONA_COMPREHENSIVE['academic_calendar_2025_2026']['first_term']['period']}
- Second Term: {CORONA_COMPREHENSIVE['academic_calendar_2025_2026']['second_term']['period']}
- Third Term: {CORONA_COMPREHENSIVE['academic_calendar_2025_2026']['third_term']['period']}

ACCREDITATIONS: {', '.join(CORONA_COMPREHENSIVE['accreditations'])}

MISSION: {CORONA_COMPREHENSIVE['mission']}
VISION: {CORONA_COMPREHENSIVE['vision']}
CORE VALUES: {', '.join(CORONA_COMPREHENSIVE['core_values'])}

ACTIVITIES: {', '.join(CORONA_COMPREHENSIVE['co_curricular']['sports'] + CORONA_COMPREHENSIVE['co_curricular']['academic_clubs'])}

CSR: {CORONA_COMPREHENSIVE['csr']['out_of_school_initiative']}
Scholarships: {CORONA_COMPREHENSIVE['csr']['scholarships']}

WEBSITE: coronaschoolbot.org
BUILT BY: Tomilola Aboderin with Kiro AI

Always respond in a helpful, professional and friendly manner. Keep responses concise but informative.
If asked about something not related to Corona Schools, politely redirect to Corona Schools topics.
Format responses clearly with bullet points where appropriate.
"""

# Load environment variables
load_dotenv('corona.env')
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'corona-school-bot-secret-key-2026')
CORS(app)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Resend API Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '').strip()
MAIL_FROM = 'Corona School Bot <onboarding@resend.dev>'

# OTP storage: {email: {code, expires_at}}
otp_store = {}

def send_otp_email(to_email, otp_code, user_name=""):
    """Send OTP code using Resend API"""
    try:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #dc143c, #8b0000); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
                <h1 style="color: white; margin: 0;">🤖 Corona School Bot</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0;">Your Login Code</p>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 12px 12px; text-align: center;">
                {"<p style='font-size: 1.1em;'>Hi <strong>" + user_name + "</strong>!</p>" if user_name else ""}
                <p style="color: #555;">Your one-time login code is:</p>
                <div style="background: white; border: 3px solid #dc143c; border-radius: 12px; padding: 20px; margin: 20px 0; display: inline-block;">
                    <span style="font-size: 3em; font-weight: 700; letter-spacing: 10px; color: #dc143c;">{otp_code}</span>
                </div>
                <p style="color: #888; font-size: 0.9em;">⏰ This code expires in <strong>10 minutes</strong></p>
                <p style="color: #888; font-size: 0.85em;">If you didn't request this, ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #aaa; font-size: 0.8em;">Corona School Bot • Built by Tomilola Aboderin & Kiro AI</p>
            </div>
        </div>
        """

        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': MAIL_FROM,
                'to': [to_email],
                'subject': f'🔐 Your Corona School Bot Login Code: {otp_code}',
                'html': html
            }
        )

        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            print(f"Resend error: {response.status_code} - {response.text}")
            # If restricted, send to owner email instead and log the code
            if response.status_code == 403:
                print(f"OTP for {to_email}: {otp_code}")
            return False

    except Exception as e:
        print(f"Email error: {e}")
        return False

# ============================================================
# USER ROLE SYSTEM
# ============================================================
OWNER_EMAILS = [
    'tomilolaxt@gmail.com',
    'tomilola.aboderin@coronaschool.org',
    'tomilolaxt-cyber@gmail.com'
]
CORONA_DOMAIN = '@coronaschool.org'
DB_FILE = 'users_db.json'

# ============================================================
# SQLITE DATABASE FOR PERSISTENT CHAT HISTORY
# ============================================================
DB_PATH = 'corona_bot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        time TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_message(user_id, role, message, time):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO chat_history (user_id, role, message, time) VALUES (?, ?, ?, ?)',
                  (user_id, role, message, time))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB save error: {e}")

def get_user_history(user_id, limit=100):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT role, message, time FROM chat_history WHERE user_id = ? ORDER BY id ASC LIMIT ?',
                  (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{'role': r[0], 'message': r[1], 'time': r[2]} for r in rows]
    except Exception as e:
        print(f"DB read error: {e}")
        return []

def clear_user_history(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB clear error: {e}")

init_db()

def load_db():
    """Load user database from file"""
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"approved_staff": [], "pending_requests": [], "denied_users": []}

def save_db(db):
    """Save user database to file"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def get_user_role(email, user_id):
    """Determine user role based on email and approval status"""
    if not email:
        return 'guest'
    # Owner always gets owner role
    if email.lower() in [e.lower() for e in OWNER_EMAILS]:
        return 'owner'
    # Check if approved staff
    db = load_db()
    approved_ids = [u['id'] for u in db['approved_staff']]
    if user_id in approved_ids:
        return 'corona_staff'
    # Check if has corona email but not yet approved
    if email.lower().endswith(CORONA_DOMAIN):
        denied_ids = [u['id'] for u in db['denied_users']]
        if user_id in denied_ids:
            return 'denied'
        pending_ids = [u['id'] for u in db['pending_requests']]
        if user_id not in pending_ids:
            return 'corona_unverified'  # Has corona email, needs to request
        return 'pending'  # Already requested, waiting
    return 'user'

def get_greeting(user):
    """Generate personalized greeting based on role"""
    if not user:
        return "Hello! Welcome to Corona School Bot. Sign in for a personalized experience!"
    
    role = user.get('role', 'user')
    name = user.get('name', '').split()[0]  # First name only
    
    if role == 'owner':
        return f"Welcome back, {name}! 👑 You have full owner access to Corona School Bot. How can I assist you today?"
    elif role == 'corona_staff':
        return f"Welcome, {name}! 🏫 As a Corona Schools staff member, you have special access. How can I help you today?"
    else:
        return f"Welcome back, {name}! 😊 Great to see you again. What would you like to know about Corona Schools?"

def generate_response(user_message, user=None):
    """Generate intelligent response using Gemini AI with Corona Schools knowledge"""
    role = user.get('role', 'guest') if user else 'guest'
    name = user.get('name', '').split()[0] if user else ''

    # Try Gemini AI first
    if gemini_model:
        try:
            # Add user context to prompt
            user_context = ""
            if user:
                if role == 'owner':
                    user_context = f"\nNote: You are talking to {name}, the OWNER and creator of this bot. Give them special respect and treat them as a VIP."
                elif role == 'corona_staff':
                    user_context = f"\nNote: You are talking to {name}, a verified Corona Schools staff member."
                else:
                    user_context = f"\nNote: You are talking to {name}, a registered user."

            prompt = f"{CORONA_CONTEXT}{user_context}\n\nUser question: {user_message}"
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            # Fall back to local knowledge base
            return generate_local_response(user_message, user)
    else:
        return generate_local_response(user_message, user)


def generate_local_response(user_message, user=None):
    message = user_message.lower().strip()
    data = CORONA_COMPREHENSIVE
    role = user.get('role', 'guest') if user else 'guest'
    name = user.get('name', '').split()[0] if user else ''

    # Greeting
    if any(word in message for word in ['hi', 'hello', 'hey', 'greetings']):
        if role == 'owner':
            return f"Hey {name}! 👑 Your Corona School Bot is running perfectly. What do you need?"
        elif role == 'corona_staff':
            return f"Hello {name}! 🏫 Welcome back. How can I assist you today?"
        elif name:
            return f"Hello {name}! Welcome to Corona School Bot. What would you like to know?"
        return "Hello! Welcome to Corona School Bot. I have comprehensive information about all Corona Schools campuses. What would you like to know?"

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


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
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
    authorization_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
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
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        email = id_info.get('email', '')
        user_id = id_info['sub']
        role = get_user_role(email, user_id)

        session.permanent = True
        session['user'] = {
            'id': user_id,
            'name': id_info.get('name', ''),
            'email': email,
            'picture': id_info.get('picture', ''),
            'role': role
        }
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Login error: {e}")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify({'authenticated': True, **user})
    return jsonify({'authenticated': False})

@app.route('/api/greeting')
def get_greeting_api():
    user = session.get('user')
    return jsonify({'greeting': get_greeting(user)})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        user = session.get('user')

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        bot_response = generate_response(user_message, user)

        # Save to chat history if logged in
        if user:
            user_id = user['id']
            now = datetime.now().strftime('%H:%M')
            save_message(user_id, 'user', user_message, now)
            save_message(user_id, 'bot', bot_response, now)

        return jsonify({'success': True, 'response': bot_response})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    user = session.get('user')
    if not user:
        return jsonify({'authenticated': False})
    history = get_user_history(user['id'])
    return jsonify({'authenticated': True, 'history': history})

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    user = session.get('user')
    if user:
        clear_user_history(user['id'])
    return jsonify({'success': True, 'message': 'Chat cleared'})

# ============================================================
# STAFF VERIFICATION SYSTEM
# ============================================================

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email"""
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'})

    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=10)

    # Store OTP
    otp_store[email] = {
        'code': otp_code,
        'expires_at': expires_at
    }

    # Send email
    success = send_otp_email(email, otp_code)

    if success:
        return jsonify({'success': True, 'message': f'Code sent to {email}!'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send email. Please try again.'})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and log in user"""
    data = request.json
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    name = data.get('name', email.split('@')[0].title())

    if email not in otp_store:
        return jsonify({'success': False, 'error': 'No code found. Please request a new one.'})

    stored = otp_store[email]

    # Check expiry
    if datetime.now() > stored['expires_at']:
        del otp_store[email]
        return jsonify({'success': False, 'error': 'Code expired. Please request a new one.'})

    # Check code
    if code != stored['code']:
        return jsonify({'success': False, 'error': 'Wrong code. Please try again.'})

    # Code is correct - log in!
    del otp_store[email]

    user_id = f"email_{email.replace('@', '_').replace('.', '_')}"
    role = get_user_role(email, user_id)

    session.permanent = True
    session['user'] = {
        'id': user_id,
        'name': name,
        'email': email,
        'picture': f'https://ui-avatars.com/api/?name={name}&background=dc143c&color=fff',
        'role': role
    }

    return jsonify({
        'success': True,
        'message': f'Welcome, {name}!',
        'role': role
    })
def request_staff():
    """User requests staff verification"""
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    db = load_db()
    user_id = user['id']

    # Check if already approved
    if any(u['id'] == user_id for u in db['approved_staff']):
        return jsonify({'success': False, 'error': 'Already approved!'})

    # Check if already pending
    if any(u['id'] == user_id for u in db['pending_requests']):
        return jsonify({'success': False, 'error': 'Request already pending!'})

    # Add to pending
    db['pending_requests'].append({
        'id': user_id,
        'name': user['name'],
        'email': user['email'],
        'picture': user['picture'],
        'requested_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    save_db(db)

    # Update session role
    session['user']['role'] = 'pending'
    session.modified = True

    return jsonify({'success': True, 'message': 'Request submitted! Waiting for admin approval.'})

@app.route('/admin')
def admin_panel():
    """Admin panel - only for owner"""
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return redirect(url_for('index'))
    db = load_db()
    return render_template('admin.html', user=user, db=db)

@app.route('/api/admin/approve/<user_id>', methods=['POST'])
def approve_staff(user_id):
    """Approve a staff request"""
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    db = load_db()

    # Find in pending
    pending_user = next((u for u in db['pending_requests'] if u['id'] == user_id), None)
    if not pending_user:
        return jsonify({'success': False, 'error': 'User not found in pending'})

    # Move to approved
    db['pending_requests'] = [u for u in db['pending_requests'] if u['id'] != user_id]
    pending_user['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    db['approved_staff'].append(pending_user)
    save_db(db)

    return jsonify({'success': True, 'message': f'{pending_user["name"]} approved!'})

@app.route('/api/admin/deny/<user_id>', methods=['POST'])
def deny_staff(user_id):
    """Deny a staff request"""
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    db = load_db()

    # Find in pending
    pending_user = next((u for u in db['pending_requests'] if u['id'] == user_id), None)
    if not pending_user:
        return jsonify({'success': False, 'error': 'User not found'})

    # Move to denied
    db['pending_requests'] = [u for u in db['pending_requests'] if u['id'] != user_id]
    pending_user['denied_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    db['denied_users'].append(pending_user)
    save_db(db)

    return jsonify({'success': True, 'message': f'{pending_user["name"]} denied.'})

@app.route('/api/admin/stats')
def admin_stats():
    """Get admin stats"""
    user = session.get('user')
    if not user or user.get('role') != 'owner':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    db = load_db()
    return jsonify({
        'approved_count': len(db['approved_staff']),
        'pending_count': len(db['pending_requests']),
        'denied_count': len(db['denied_users']),
        'pending_requests': db['pending_requests'],
        'approved_staff': db['approved_staff']
    })

if __name__ == '__main__':
    app.run(debug=True, port=3000)
