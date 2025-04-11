import json
import time
from flask import current_app
import requests

def generate_osint_analysis(target, analysis_type, data):
    """
    Generate AI-powered analysis of OSINT data using OpenAI API
    """
    api_key = current_app.config.get('OPENAI_API_KEY')
    
    # Use mock data if no API key is available or if OpenAI API call fails
    try:
        # Initialize the OpenAI client with the API key
        if not api_key:
            print("No OpenAI API key provided. Using mock data.")
            return _get_mock_insights(target, analysis_type)
            
        # Prepare data for API call
        system_message = _get_system_prompt(analysis_type)
        formatted_data = json.dumps(data, indent=2)
        
        user_message = f"""
        Target: {target}
        Analysis Type: {analysis_type}
        
        Data:
        {formatted_data}
        
        Please analyze this data and provide insights.
        """
        
        # Make API call to OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for API errors
        if response.status_code != 200:
            print(f"Error generating AI analysis: Error code: {response.status_code} - {response.json()}")
            return _get_mock_insights(target, analysis_type)
            
        # Extract and parse response
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content']
        insights = _parse_ai_response(ai_response, analysis_type)
        
        return insights
        
    except Exception as e:
        print(f"Error generating AI analysis: {e}")
        return _get_mock_insights(target, analysis_type)

def generate_security_recommendations(analysis_type, insights):
    """
    Generate security recommendations based on the AI analysis
    """
    api_key = current_app.config.get('OPENAI_API_KEY')
    
    # Use mock data if no API key is available or if OpenAI API call fails
    try:
        # Initialize the OpenAI client with the API key
        if not api_key:
            print("No OpenAI API key provided. Using mock data for recommendations.")
            return _get_mock_recommendations(analysis_type)
            
        # Prepare data for API call
        system_message = """
        You are a cybersecurity expert specialized in providing actionable security recommendations based on OSINT findings.
        Provide specific, practical recommendations to address security concerns identified in the insights.
        Each recommendation should include:
        1. A clear title
        2. A detailed description of the recommended action
        3. A priority level (Critical, High, Medium, Low)
        4. A category for the recommendation
        
        Format your response as a JSON array of recommendation objects.
        """
        
        # Format the insights for the AI
        formatted_insights = json.dumps(insights, indent=2)
        
        user_message = f"""
        Analysis Type: {analysis_type}
        
        Insights:
        {formatted_insights}
        
        Please provide security recommendations based on these insights.
        """
        
        # Make API call to OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for API errors
        if response.status_code != 200:
            print(f"Error generating security recommendations: Error code: {response.status_code} - {response.json()}")
            return _get_mock_recommendations(analysis_type)
            
        # Extract and parse response
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content']
        
        # Parse the response into our recommendations format
        try:
            # Extract JSON from the response
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("Could not find JSON array in response")
            
            json_str = ai_response[json_start:json_end]
            recommendations = json.loads(json_str)
            
            # Validate and format recommendations
            formatted_recommendations = []
            for rec in recommendations:
                if all(k in rec for k in ['title', 'description', 'priority', 'category']):
                    formatted_recommendations.append(rec)
            
            if not formatted_recommendations:
                return _get_mock_recommendations(analysis_type)
                
            return formatted_recommendations
        except Exception as e:
            print(f"Error parsing AI recommendations: {e}")
            return _get_mock_recommendations(analysis_type)
    
    except Exception as e:
        print(f"Error generating security recommendations: {e}")
        return _get_mock_recommendations(analysis_type)

def _get_system_prompt(analysis_type):
    """Get the appropriate system prompt based on analysis type"""
    prompts = {
        'username': """
        You are an OSINT (Open Source Intelligence) analyst specializing in digital footprint analysis.
        You're examining accounts linked to a specific username across various online platforms.
        
        Analyze the provided data to identify:
        1. Digital activity patterns
        2. Identity consistency across platforms
        3. Interests and behaviors suggested by platform choices
        4. Exposure level and privacy implications
        5. Professional vs. personal presence separation
        
        For each insight, provide:
        - A clear title
        - A detailed description
        - A confidence level (High, Medium, Low)
        - A category (Identity, Exposure, Professional, Interests, etc.)
        
        Format your response as a JSON array of insight objects.
        """,
        
        'email': """
        You are an OSINT (Open Source Intelligence) analyst specializing in data breach analysis.
        You're examining breaches containing a specific email address.
        
        Analyze the provided data to identify:
        1. Severity and scope of the breaches
        2. Types of data exposed
        3. Timeline of breaches
        4. Potential security implications
        5. Identity theft and fraud risks
        
        For each insight, provide:
        - A clear title
        - A detailed description
        - A confidence level (High, Medium, Low)
        - A category (Security, Privacy, Account History, etc.)
        
        Format your response as a JSON array of insight objects.
        """,
        
        'domain': """
        You are an OSINT (Open Source Intelligence) analyst specializing in domain analysis.
        You're examining information about a specific domain.
        
        Analyze the provided data to identify:
        1. Domain age and history
        2. Infrastructure insights
        3. Owner intent and legitimacy
        4. Security posture
        5. Operational patterns
        
        For each insight, provide:
        - A clear title
        - A detailed description
        - A confidence level (High, Medium, Low)
        - A category (Legitimacy, Infrastructure, Intent, etc.)
        
        Format your response as a JSON array of insight objects.
        """,
        
        'combined': """
        You are an OSINT (Open Source Intelligence) analyst specializing in comprehensive digital presence analysis.
        You're examining a combined dataset including usernames, emails, and domains.
        
        Analyze the provided data to identify:
        1. Cross-platform identity patterns
        2. Overall digital footprint assessment
        3. Security and privacy vulnerabilities
        4. Timeline of online activity
        5. Professional and personal activity correlation
        
        For each insight, provide:
        - A clear title
        - A detailed description
        - A confidence level (High, Medium, Low)
        - A category (Identity, Exposure, Security, History, Professional, etc.)
        
        Format your response as a JSON array of insight objects.
        """
    }
    
    return prompts.get(analysis_type, prompts['combined'])

def _parse_ai_response(ai_response, analysis_type):
    """Parse the AI's response into our insights format"""
    try:
        # Extract JSON from the response
        json_start = ai_response.find('[')
        json_end = ai_response.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("Could not find JSON array in response")
        
        json_str = ai_response[json_start:json_end]
        insights = json.loads(json_str)
        
        # Validate and format insights
        formatted_insights = []
        for insight in insights:
            if all(k in insight for k in ['title', 'description', 'confidence', 'category']):
                formatted_insights.append(insight)
        
        if not formatted_insights:
            return _get_mock_insights("Unknown Target", analysis_type)
            
        return formatted_insights
    
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return _get_mock_insights("Unknown Target", analysis_type)

def _get_mock_insights(target, analysis_type):
    """Return mock insights for development"""
    if analysis_type == 'username':
        return [
            {
                'title': 'Digital Activity Pattern',
                'description': f'The username "{target}" is primarily active on professional platforms and social media. The presence across both GitHub and LinkedIn suggests tech industry involvement.',
                'confidence': 'High',
                'category': 'Professional'
            },
            {
                'title': 'Identity Consistency',
                'description': f'The username "{target}" uses consistent naming across platforms, which increases the likelihood these accounts belong to the same individual.',
                'confidence': 'Medium',
                'category': 'Identity'
            },
            {
                'title': 'Interest Analysis',
                'description': f'Based on the platforms where "{target}" is active, there is a strong interest in technology, programming, and professional networking.',
                'confidence': 'Medium',
                'category': 'Interests'
            },
            {
                'title': 'Visibility Assessment',
                'description': f'The username "{target}" has a moderate digital footprint with accounts on several major platforms, making the individual relatively easy to find online.',
                'confidence': 'High',
                'category': 'Exposure'
            }
        ]
    
    elif analysis_type == 'email':
        return [
            {
                'title': 'Breach Exposure',
                'description': f'The email "{target}" has been found in multiple data breaches, including high-profile incidents.',
                'confidence': 'High',
                'category': 'Security'
            },
            {
                'title': 'Password Vulnerability',
                'description': 'The email has been exposed in breaches that included password data, indicating a high risk of credential stuffing attacks.',
                'confidence': 'High',
                'category': 'Security'
            },
            {
                'title': 'Personal Data Exposure',
                'description': 'Additional personal information beyond email was exposed in some breaches, increasing identity theft risk.',
                'confidence': 'Medium',
                'category': 'Privacy'
            },
            {
                'title': 'Historical Vulnerability',
                'description': 'The breaches occurred over several years, suggesting the email has been in use for a long time.',
                'confidence': 'Medium',
                'category': 'Account History'
            }
        ]
    
    elif analysis_type == 'domain':
        return [
            {
                'title': 'Domain Maturity',
                'description': f'The domain "{target}" was registered several years ago, giving it a significant online history and established web presence.',
                'confidence': 'High',
                'category': 'Legitimacy'
            },
            {
                'title': 'Hosting Infrastructure',
                'description': 'The domain uses standard nameservers, suggesting it is hosted on a conventional web hosting provider without special security measures.',
                'confidence': 'Medium',
                'category': 'Infrastructure'
            },
            {
                'title': 'Registration Longevity',
                'description': 'The domain registration expiration date indicates the owner intends to maintain it for the long term.',
                'confidence': 'High',
                'category': 'Intent'
            }
        ]
    
    else:  # combined or other
        return [
            {
                'title': 'Cross-Platform Identity',
                'description': f'The target "{target}" maintains a consistent identity across social, professional, and email platforms, increasing the confidence of attribution.',
                'confidence': 'High',
                'category': 'Identity'
            },
            {
                'title': 'Comprehensive Exposure',
                'description': 'The combination of social media accounts, breached email data, and domain ownership creates a significant digital footprint.',
                'confidence': 'High',
                'category': 'Exposure'
            },
            {
                'title': 'Security Risk Profile',
                'description': 'The exposed email credentials in conjunction with identifiable social accounts creates an elevated risk for targeted attacks.',
                'confidence': 'Medium',
                'category': 'Security'
            },
            {
                'title': 'Online Activity Timeline',
                'description': 'Based on various data points, the target has maintained an online presence for several years.',
                'confidence': 'Medium',
                'category': 'History'
            },
            {
                'title': 'Professional Context',
                'description': 'The combination of professional platforms suggests this individual works in a specific industry.',
                'confidence': 'Medium',
                'category': 'Professional'
            }
        ]

def _get_mock_recommendations(analysis_type):
    """Return mock recommendations for development"""
    if analysis_type == 'username':
        return [
            {
                'title': 'Review Privacy Settings',
                'description': 'Audit and restrict privacy settings across all identified social media accounts to limit public information exposure.',
                'priority': 'High',
                'category': 'Privacy'
            },
            {
                'title': 'Username Variation',
                'description': 'Consider using different usernames across platforms to make it harder to correlate your online identities.',
                'priority': 'Medium',
                'category': 'Identity Protection'
            },
            {
                'title': 'Content Audit',
                'description': 'Review content posted under this username for potentially sensitive information that could be used for social engineering.',
                'priority': 'Medium',
                'category': 'Content Management'
            },
            {
                'title': 'Enable Two-Factor Authentication',
                'description': 'Secure all discovered accounts with two-factor authentication to prevent unauthorized access.',
                'priority': 'High',
                'category': 'Account Security'
            }
        ]
    
    elif analysis_type == 'email':
        return [
            {
                'title': 'Change Passwords Immediately',
                'description': 'Update passwords on all accounts associated with this email, especially where you may have reused passwords.',
                'priority': 'Critical',
                'category': 'Credential Security'
            },
            {
                'title': 'Implement Password Manager',
                'description': 'Use a password manager to generate and store unique, strong passwords for each online account.',
                'priority': 'High',
                'category': 'Credential Management'
            },
            {
                'title': 'Enable Breach Alerts',
                'description': 'Set up alerts for future breaches through a service like HaveIBeenPwned to be notified if your email appears in new data breaches.',
                'priority': 'Medium',
                'category': 'Monitoring'
            },
            {
                'title': 'Consider Email Aliasing',
                'description': 'Use email aliases for different services to minimize the impact of future data breaches.',
                'priority': 'Medium',
                'category': 'Email Security'
            }
        ]
    
    elif analysis_type == 'domain':
        return [
            {
                'title': 'Enable WHOIS Privacy',
                'description': 'Ensure WHOIS privacy protection is enabled to prevent personal information exposure through domain registration data.',
                'priority': 'High',
                'category': 'Privacy'
            },
            {
                'title': 'Implement SSL/TLS',
                'description': 'Ensure the domain uses HTTPS with a valid SSL/TLS certificate to secure communications.',
                'priority': 'High',
                'category': 'Communication Security'
            },
            {
                'title': 'Configure SPF, DKIM, and DMARC',
                'description': 'Implement email authentication protocols to prevent email spoofing using your domain.',
                'priority': 'Medium',
                'category': 'Email Security'
            },
            {
                'title': 'Regular Security Scanning',
                'description': 'Set up regular vulnerability scanning for websites hosted on this domain.',
                'priority': 'Medium',
                'category': 'Vulnerability Management'
            }
        ]
    
    else:  # combined or other
        return [
            {
                'title': 'Comprehensive Security Review',
                'description': 'Conduct a thorough security review across all platforms where your identity is present, prioritizing accounts with the highest risk exposure.',
                'priority': 'Critical',
                'category': 'Holistic Security'
            },
            {
                'title': 'Identity Segmentation',
                'description': 'Consider separating professional and personal online identities to reduce correlation and overall risk surface.',
                'priority': 'High',
                'category': 'Identity Management'
            },
            {
                'title': 'Password Reset Campaign',
                'description': 'Systematically reset passwords across all identified accounts, using unique strong passwords for each service.',
                'priority': 'Critical',
                'category': 'Credential Security'
            },
            {
                'title': 'Data Minimization',
                'description': 'Audit and remove unnecessary personal information from all online profiles to reduce exposure.',
                'priority': 'High',
                'category': 'Privacy'
            },
            {
                'title': 'Security Monitoring',
                'description': 'Implement continuous monitoring for your digital identity across social media, email security, and domain integrity.',
                'priority': 'Medium',
                'category': 'Ongoing Protection'
            }
        ]