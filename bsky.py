import os
import logging
import time
from datetime import datetime
import json
from atproto import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"bluesky_bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("bluesky_bot")

class BlueskyBot:
    def __init__(self):
        self.logger = setup_logging()
        self.client = None
        self.profile = None
        
        # Get credentials from environment variables
        self.username = os.getenv("BLUESKY_USERNAME")
        self.password = os.getenv("BLUESKY_PASSWORD")
        
        if not self.username or not self.password:
            self.logger.error("Bluesky credentials not found in environment variables")
            raise ValueError("Missing Bluesky credentials. Set BLUESKY_USERNAME and BLUESKY_PASSWORD environment variables.")
        
        self.logger.info("BlueskyBot initialized")
    
    def login(self):
        """Log in to Bluesky"""
        try:
            self.logger.info(f"Attempting to log in as {self.username}")
            self.client = Client()
            self.profile = self.client.login(self.username, self.password)
            self.logger.info(f"Successfully logged in as {self.username}")
            self.logger.info(f"DID: {self.profile.did}")
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def get_profile(self):
        """Get the bot's profile information"""
        if not self.client:
            self.logger.error("Not logged in")
            return None
        
        try:
            # Updated to use the correct method
            profile = self.client.get_profile(self.profile.handle)
            self.logger.info(f"Retrieved profile for {profile.display_name} (@{profile.handle})")
            return profile
        except Exception as e:
            self.logger.error(f"Failed to get profile: {str(e)}")
            return None
    
    def post_text(self, text):
        """Post a text update to Bluesky"""
        if not self.client:
            self.logger.error("Not logged in")
            return False
        
        try:
            self.logger.info(f"Posting update: {text[:300]}...")
            # Updated to use the simplified post method
            response = self.client.send_post(text=text)
            self.logger.info(f"Post successful, URI: {response.uri}")
            return response.uri
        except Exception as e:
            self.logger.error(f"Failed to post update: {str(e)}")
            return False
    
    def post_with_image(self, text, image_path, alt_text=""):
        """Post an update with an image to Bluesky"""
        if not self.client:
            self.logger.error("Not logged in")
            return False
        
        try:
            # Upload the image
            self.logger.info(f"Uploading image: {image_path}")
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Updated to use the simplified post with image method
            response = self.client.send_image(text=text, image=image_data, image_alt=alt_text)
            self.logger.info(f"Post with image successful, URI: {response.uri}")
            return response.uri
        except Exception as e:
            self.logger.error(f"Failed to post update with image: {str(e)}")
            return False
    
    def get_recent_posts(self, limit=10):
        """Get the bot's recent posts"""
        if not self.client:
            self.logger.error("Not logged in")
            return []
        
        try:
            # Updated to use the correct method
            feed = self.client.get_author_feed(self.profile.handle, limit=limit)
            posts = []
            for item in feed.feed:
                post = item.post
                posts.append({
                    'uri': post.uri,
                    'cid': post.cid,
                    'text': post.record.text,
                    'created_at': post.record.created_at,
                    'likes': getattr(post, 'like_count', 0),
                    'replies': getattr(post, 'reply_count', 0),
                    'reposts': getattr(post, 'repost_count', 0)
                })
            self.logger.info(f"Retrieved {len(posts)} recent posts")
            return posts
        except Exception as e:
            self.logger.error(f"Failed to get recent posts: {str(e)}")
            return None

def main():
    bot = BlueskyBot()
    
    # Login to Bluesky
    if bot.login():
        # Get profile information
        profile = bot.get_profile()
        if profile:
            print(f"Logged in as: {profile.display_name} (@{profile.handle})")
            print(f"Followers: {profile.followers_count}, Following: {profile.follows_count}")
            
            # Post a test message
            test_message = f"This is a test post from my Bluesky bot at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            post_uri = bot.post_text(test_message)
            
            if post_uri:
                print(f"Test post successful! URI: {post_uri}")
            
            # Get recent posts
            recent_posts = bot.get_recent_posts(5)
            if recent_posts:
                print(f"\nRecent posts ({len(recent_posts)}):")
                for i, post in enumerate(recent_posts, 1):
                    print(f"{i}. [{post['created_at']}] {post['text'][:300]}... ({post['likes']} likes, {post['replies']} replies)")
    else:
        print("Failed to log in to Bluesky")

if __name__ == "__main__":
    main()
