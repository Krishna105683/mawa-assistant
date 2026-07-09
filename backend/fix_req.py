content = """flask==3.0.0
flask-cors==4.0.0
groq==0.9.0
python-dotenv==1.0.0
requests==2.31.0
apscheduler==3.10.4
feedparser==6.0.11
gunicorn==21.2.0
httpx==0.27.0
pytz==2024.1
flask-jwt-extended==4.7.4
bcrypt==5.0.0
"""

with open('requirements.txt', 'w') as f:
    f.write(content)

print('Done! Requirements updated!')