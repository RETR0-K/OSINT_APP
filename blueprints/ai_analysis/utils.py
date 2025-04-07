# blueprints/ai_analysis/utils.py
import openai
import random
import json
from flask import current_app

def generate_osint_analysis(target, analysis_type, data):
    """
    Generate AI-powered analysis of OSINT data
    
    For a real implementation, you would use OpenAI API or another NLP model.
    This is a mock implementation for development.
    """
    insights = []
    
    # In a production environment, you would call OpenAI API like this:
    # openai.api_key = current_app.config['OPENAI_API_KEY']
    # response = openai.ChatCompletion.create(
    #    model="gpt-4",
    #    messages=[
    #        {"role": "system", "content": "You are an OSINT analysis expert."},
    #        {"role": "user", "content": f"Analyze this {analysis_type} data for {target}: {json.dumps(data)}"}
    #    ]
    # )
    # analysis_text = response.choices[0].message.content
    
    # For the mock implementation, return predefined insights based on analysis type
    if analysis_type == 'username':
        insights = [
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
                'description': f'The username "{target}" has a moderate digital footprint with accounts on {len(data)} major platforms, making the individual relatively easy to find online.',
                'confidence': 'High',
                'category': 'Exposure'
            }
        ]
    
    elif analysis_type == 'email':
        insights = [
            {
                'title': 'Breach Exposure',
                'description': f'The email "{target}" has been found in multiple data breaches, including high-profile incidents at LinkedIn and Adobe.',
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
                'description': 'In the Adobe breach, additional personal information beyond email was exposed, increasing identity theft risk.',
                'confidence': 'Medium',
                'category': 'Privacy'
            },
            {
                'title': 'Historical Vulnerability',
                'description': 'The breaches occurred between 2012 and 2013, suggesting the email has been in use for at least 10 years.',
                'confidence': 'Medium',
                'category': 'Account History'
            }
        ]
    
    elif analysis_type == 'domain':
        insights = [
            {
                'title': 'Domain Maturity',
                'description': f'The domain "{target}" was registered in 2010, giving it a significant online history and established web presence.',
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
                'description': 'The domain is registered until 2025, indicating the owner intends to maintain it for the long term.',
                'confidence': 'High',
                'category': 'Intent'
            }
        ]
    
    elif analysis_type == 'combined':
        insights = [
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
                'description': 'Based on domain registration and breach dates, the target has maintained an online presence since at least 2010.',
                'confidence': 'Medium',
                'category': 'History'
            },
            {
                'title': 'Professional Context',
                'description': 'The combination of LinkedIn, GitHub, and a personally registered domain suggests this individual is a technology professional.',
                'confidence': 'Medium',
                'category': 'Professional'
            }
        ]
    
    return insights

def generate_security_recommendations(analysis_type, insights):
    """
    Generate security recommendations based on the AI analysis
    
    For a real implementation, you would use the insights to generate targeted recommendations.
    This is a mock implementation for development.
    """
    recommendations = []
    
    if analysis_type == 'username':
        recommendations = [
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
        recommendations = [
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
        recommendations = [
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
    
    elif analysis_type == 'combined':
        recommendations = [
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
    
    return recommendations