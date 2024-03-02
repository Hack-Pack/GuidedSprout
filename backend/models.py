import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from glob import glob

load_dotenv()


client = OpenAI()

class Model:
    def __init__(self, model_name):
        self.model_name = model_name

class TextModel(Model):
    def __init__(self, model_name="gpt-4-1106-preview"):
        super().__init__(model_name)

    def complete(self, prompt, role="You are an experienced math teacher"):
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ]
        
        completion = client.chat.completions.create(model=self.model_name,
        temperature=0,
        messages=messages)
        
        # Returning the response message
        return completion.choices[0].message.content
    
class VisionModel(Model):
    def __init__(self, model_name="gpt-4-vision-preview"):
        super().__init__(model_name)

    def encode_image(self, image_path):
        """Encodes an image to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def complete(self, prompt, image_dir):
        """Generates a completion using images and a text prompt."""
        # Find all images in the specified directory
        image_paths = glob(os.path.join(image_dir, '*'))
        images_encoded = [self.encode_image(path) for path in image_paths]

        # Prepare the content with text and images
        content = [{"type": "text", "text": prompt}]
        content.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in images_encoded])

        # Make the API request
        response = client.chat.completions.create(model=self.model_name,
        messages=[{"role": "user", "content": content}],
        temperature=0,
        max_tokens=3000)
        
        return response.choices[0].message.content
    
def tts(input_text, output_file):
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input_text
    )
    response.stream_to_file(output_file)