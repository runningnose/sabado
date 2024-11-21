#!/usr/local/bin/python3

import os
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

def main():
    # Replace these with your client ID and client secret
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    # Define the scope of access you need
    scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

    # Set up the flow using the client secrets
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print("Please go to this URL and authorize the app:", auth_url)
    print("Enter the authorization code:")
    code = input()

    # Use the code to obtain tokens
    flow.fetch_token(code=code)

    # Get the refresh token
    refresh_token = flow.credentials.refresh_token
    print('Your refresh token is:', refresh_token)

if __name__ == '__main__':
    main()
