# create a function that will loop into the image chuncks and explain the content of the whole image

import os
from PIL import Image
from dotenv import load_dotenv
from dotenv import find_dotenv
import base64

from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv(find_dotenv())
client = AzureOpenAI( azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
         azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
         api_key=os.getenv("AZURE_OPENAI_KEY"), 
         api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        timeout=1000  
    )
# read the chunks on the chunks directory and return the list of chunks as a bidimentional array
def read_chunks(image_path: str):
    image_path="./image/chunks/"
    chunks = []
    for filename in os.listdir(image_path):
        if filename.endswith('.png'):
            chunks.append(os.path.join(image_path, filename))
    return chunks

# create a function that will loop into the image chuncks and explain the content of the whole image
def explain_image(image_path):
    # read the chunks
    chunks = read_chunks(image_path)
    # create a list to store the explanations
    chunks = chunks[:16]
    explanation = ""
    message = []
            # create a prompt for the model
    prompt = "Explain the content of following image chunks: "
    message= [{"role": "user", "content": prompt}]
    # loop into the chunks and explain each chunk
    for chunk in chunks:
        # open the image
        with Image.open(chunk) as img:
            # convert img to base64
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            message.append({"role": "user", "content": f"data:image/jpeg;base64,{img_base64}", "detail": "low" })
            
        # call the OpenAI API to get the explanation
    response = client.chat.completions.create(
        model = os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        messages=message)

    # create a dictionary to store the explanation, with the role and the content
    explanation = response.choices[0].message.content
    # return the list of explanations
    return explanation


# iterate over the explanations and summarize the content with openai

def summarize_explanations(explanations):
    # create a prompt for the model
    prompt = "Summarize the content of the following image chunks: "
    # loop into the explanations and append the content to the prompt
    for explanation in explanations:
        prompt += explanation["content"] + "\n"
    # call the OpenAI API to get the summary
    response = client.chat.completions.create(
        model = os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        n=1,
        stop=None,
    )
    # return the summary
    return response.choices[0].message.content

# create the main function to run the code
def main():
    # set the image path to the directory image under the current directory
    image_path= "./image/chunks/"
    
    print(f"Reading chunks from {image_path}")

    
    chunks = read_chunks(image_path)
    # explain the image
    explanations = explain_image(chunks)
    print(explanations)

if __name__ == "__main__":
    main()