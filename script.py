from flask import Flask, request, jsonify
import gym
import nle
import logging
import sys
from nle_language_wrapper import NLELanguageWrapper
from PIL import Image, ImageDraw, ImageFont
import io
import base64

#Set up logging to file and console
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
logPath = "/"
fileName = "bsky-plays-nethack-bot"
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

#Instantiate global variables for app.  I know, this is bad and I shouldn't be using globals, don't @ me.
app = Flask(__name__)
env = NLELanguageWrapper(gym.make("NetHackChallenge-v0"))
obsv = env.reset()

@app.route('/api/command', methods=['GET'])
def process_command():
    # Get the command from query parameters
    command = request.args.get('command')
    
    # Log the request parameters
    rootLogger.info(f"Received command: {command}")
    
    # Check if 'command' parameter exists in the request
    if not command:
        return jsonify({
            'status': 'error',
            'message': 'Missing command parameter'
        }), 400
    
    obsv, reward, done, info = env.step(command)
    screen = env.render(mode="string")
    rootLogger.info(screen)
    # Create image from screen text
    screen_image = text_to_image(screen)
    img_io = io.BytesIO()
    screen_image.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('ascii')
    # Process the command (this is where you would add your logic)
    # For now, we'll just echo it back
    response = {
        'status': 'success',
        'message': f'Received command: {command}',
        'obsv': obsv,
        'reward': reward,
        'done': done,
        'info': info,
        'screen': screen,
        'img_base64': img_base64
    }
    
    return jsonify(response)

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>Command API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Command API</h1>
            <p>Send a POST request to <code>/api/command</code> with a JSON body containing a "Command" field.</p>
            <h2>Example:</h2>
            <pre>
curl -X POST http://localhost:5000/api/command \\
    -H "Content-Type: application/json" \\
    -d '{"Command": "hello world"}'
            </pre>
        </body>
    </html>
    """

def text_to_image(text, font_size=15):
    """Convert text to an image with white text on black background"""
    # Split the text into lines
    lines = text.split('\n')
    
    # Calculate image dimensions based on text
    try:
        # Try to use a monospace font for better alignment
        font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    except IOError:
        # Fall back to default font if monospace not available
        font = ImageFont.load_default()
    
    # Calculate image size based on text content
    line_height = font_size + 2
    text_width = max(len(line) * (font_size // 2) for line in lines)
    text_height = len(lines) * line_height
    
    # Create image with black background
    img = Image.new('RGB', (text_width, text_height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw text in white
    y_position = 0
    for line in lines:
        draw.text((0, y_position), line, font=font, fill='white')
        y_position += line_height
    
    return img

def main():
    rootLogger.info('Started')
    # Run the Flask app on all interfaces (0.0.0.0) on port 5000
    app.run(host='0.0.0.0', port=5000)
    rootLogger.info('Finished')

if __name__ == '__main__':
    main()
