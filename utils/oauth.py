"""pip install oauthlib"""

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# OAuth provider configuration
client_id = 'your_client_id'
client_secret = 'your_client_secret'
authorization_base_url = 'https://example.com/oauth/authorize'
token_url = 'https://example.com/oauth/token'
redirect_uri = 'https://yourapp.com/callback'

# Initialize OAuth session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Get authorization URL
authorization_url, state = oauth.authorization_url(authorization_base_url)

# Redirect the user to the authorization URL
print('Please go here and authorize:', authorization_url)

# Handle callback URL after user authorization
authorization_response = input('Enter the full callback URL: ')

# Fetch access token
token = oauth.fetch_token(token_url, authorization_response=authorization_response, client_secret=client_secret)

# Use the access token to access protected resources
response = oauth.get('https://example.com/api/resource')
print(response.content)