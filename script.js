// Corona Schools Knowledge Base
const coronaKnowledge = {
    about: {
        keywords: ['about', 'corona schools', 'who are you', 'what is corona'],
        response: `Corona Schools' Trust Council is a prestigious educational institution in Nigeria with 70 years of excellence. We operate 8 schools representing over 35,000+ students. Our mission is to provide world-class education to children, inculcating high moral and ethical values as we prepare them for lifelong learning, service and fulfillment.`
    },
    mission: {
        keywords: ['mission', 'vision', 'goal'],
        response: `Our Mission: To provide world-class education to children. We inculcate high moral and ethical values in our students as we prepare them for lifelong learning, service and fulfillment.\n\nOur Vision: To be Nigeria's leading educational institution focused on and dedicated to producing well-rounded and proudly Nigerian young men and women equipped for continuous learning, personal mastery and leadership.`
    },
    admissions: {
        keywords: ['admission', 'enroll', 'register', 'apply', 'entrance exam'],
        response: `Corona Schools is currently accepting admissions for 2025/2026 into Year 7-11 for both Boarding & Day School. Entrance Examination Registration is ongoing for both regular and scholarship programs. Visit our website or contact the admissions office for more details on requirements and registration.`
    },
    curriculum: {
        keywords: ['curriculum', 'subjects', 'program', 'course'],
        response: `We offer comprehensive curricula tailored to each level:\n\n• Nursery: Montessori method supporting learning in all curriculum areas\n• Primary: Blend of Nigerian and International Primary Curriculum (IPC)\n• Secondary: Blend of Nigerian and British curricula preparing students for top undergraduate programmes worldwide`
    },
    facilities: {
        keywords: ['facilities', 'infrastructure', 'campus', 'library', 'technology'],
        response: `Corona Schools boasts world-class facilities including modern libraries, advanced technology infrastructure, sports facilities, and state-of-the-art learning spaces. We are Microsoft Showcase/Incubator Schools with 158 Microsoft Innovative Experts and 187 Microsoft Certified Experts on staff.`
    },
    activities: {
        keywords: ['activities', 'co-curricular', 'sports', 'clubs', 'music', 'drama'],
        response: `We offer diverse co-curricular activities including: Music, Taekwondo, Athletics, Ballet, Golf, Cheerleading, Dance, Basketball, Drama, French, Chess, STEAM, Model United Nations, Public Speaking, Debating, Cooking Club, Rugby, and many more. These activities develop well-rounded students with diverse talents.`
    },
    accreditation: {
        keywords: ['accreditation', 'award', 'neasc', 'acca', 'british council'],
        response: `Corona Schools holds prestigious accreditations:\n\n• NEASC Accreditation: Corona Secondary School Agbara is the only Secondary School in Africa accredited by NEASC\n• ACCA: Only secondary school in Nigeria where students pass the foundation level of Association of Chartered Certified Accountants\n• British Council Award: Won Community Initiative Award 2019 for student-led water borehole initiative`
    },
    staff: {
        keywords: ['staff', 'teachers', 'employees', 'faculty'],
        response: `Corona Schools employs 668 experienced academic and non-academic staff dedicated to providing world-class education. Our team includes Microsoft Certified Experts and innovative educators committed to student success.`
    },
    alumni: {
        keywords: ['alumni', 'graduates', 'past students'],
        response: `Corona Schools has a most influential alumni network with over 35,000+ current and past students. Our alumni excel globally, contributing to various fields and maintaining strong connections with the school community.`
    },
    contact: {
        keywords: ['contact', 'phone', 'email', 'address', 'reach'],
        response: `For more information about Corona Schools, please visit our website at https://coronaschools.org/ or contact our admissions office. You can also reach out through our official channels for specific inquiries.`
    }
};

// Chat functionality
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatMessages = document.getElementById('chatMessages');

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    
    if (message) {
        addMessage(message, 'user');
        userInput.value = '';
        
        // Simulate typing delay
        setTimeout(() => {
            const response = generateResponse(message);
            addMessage(response, 'bot');
        }, 500);
    }
});

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const p = document.createElement('p');
    p.textContent = text;
    
    contentDiv.appendChild(p);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function generateResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    // Check each knowledge base entry
    for (const [key, data] of Object.entries(coronaKnowledge)) {
        for (const keyword of data.keywords) {
            if (lowerMessage.includes(keyword)) {
                return data.response;
            }
        }
    }
    
    // Default response if no match found
    return `I'm not sure about that specific question. However, I can help you with information about Corona Schools including:\n\n• About Corona Schools\n• Mission and Vision\n• Admissions and Registration\n• Curriculum and Programs\n• Facilities and Infrastructure\n• Co-curricular Activities\n• Accreditations and Awards\n• Staff Information\n• Alumni Network\n\nFeel free to ask about any of these topics!`;
}

function askQuestion(question) {
    userInput.value = question;
    chatForm.dispatchEvent(new Event('submit'));
}
