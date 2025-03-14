# create a function that will loop into the image chuncks and explain the content of the whole image

import os
from PIL import Image
from dotenv import load_dotenv, find_dotenv
import tiktoken
import base64

from openai import AzureOpenAI
load_dotenv(find_dotenv())

client = AzureOpenAI( azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
         azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
         api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
         api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        timeout=1000  
    )
# read the chunks on the chunks directory and return the list of chunks as a bidimentional array

def count_tokens(message)-> int:
    # calculate the amount of openai input tokens in the message using the tiktoken library
    encoding = tiktoken.encoding_for_model(os.getenv('AZURE_OPENAI_DEPLOYMENT'))
    total_tokens = 0
    
    for msg in message:
        content = msg.get('content', '')
        # Check if the content is a base64 image
        if isinstance(content, str) and content.startswith('data:image'):
            # Get image quality level
            detail = msg.get('detail', 'high')
            
            # Extract base64 data
            base64_data = content.split('base64,')[1] if 'base64,' in content else ''
            
            if base64_data:
                try:
                    image_data = base64.b64decode(base64_data)
                    img = Image.open(BytesIO(image_data))
                    width, height = img.size
                    
                    # Calculate tokens based on dimensions and quality
                    if detail == "low":
                        image_tokens = int((width * height) / (512 * 512) * 85)
                    else:  # "high" or default
                        image_tokens = int((width * height) / (512 * 512) * 170)
                    
                    total_tokens += max(image_tokens, 1)
                except Exception:
                    total_tokens += len(encoding.encode(content))
            else:
                total_tokens += len(encoding.encode(content))
        else:
            # Regular text content
            total_tokens += len(encoding.encode(content))
    
    return total_tokens


def read_chunks():
    image_path = "./image/chunks/"
    chunks = []
    for filename in os.listdir(image_path):
        if filename.endswith('.png'):
            chunks.append(os.path.join(image_path, filename))
    return chunks


# create a function that will explain only the first image chunk
def explain_image_chunk(chunk):
    # open the image
    with Image.open(chunk) as img:
        # convert img to base64
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        # create a prompt for the model
        prompt = "Explain the content of the following image chunk: "
        message= [{"role": "user", "content": [{"type": "text", "content": prompt}]}]
        message[0]['content'].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}, "detail": "low" })

        #  "image_url": { "url":  f"data:image/jpeg;base64,{base64_image}"
        # {"type": "image_url", "image_url": { "url":  f"data:image/jpeg;base64,{base64_image}" , "detail": "low" }


    # calculate the amount of openai input tokens in the message using the tiktoken library
    #total_tokens = count_tokens(message)
    #print(f"Number of tokens: {total_tokens}")
    


    

    # call the OpenAI API to get the explanation
    
    response = client.chat.completions.create(
         model = os.getenv('AZURE_OPENAI_DEPLOYMENT'),
         messages=message)

    #explanation = "This is a test explanation"
    # create a dictionary to store the explanation, with the role and the content
    explanation = response.choices[0].message.content
    # return the explanation
    return explanation


# create a function that will loop into the image chuncks and explain the content of the whole image
def explain_image(chunks):
    # read the chunks
    explanation = ""
    message = []
    # create a prompt for the model
    prompt = "Explain the content of following image chunks: "
    message= [ {"role": "user", "type": "text",  "content":[ {"type": "text", "content": prompt}]}]
    # loop into the chunks and explain each chunk
    for chunk in chunks:
        # open the image
        with Image.open(chunk) as img:
            # convert img to base64
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            # append a new element on message.content
            message[0]['content'].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}, "detail": "low" })
            
        # call the OpenAI API to get the explanation
    response = client.chat.completions.create(
         model = os.getenv('AZURE_OPENAI_DEPLOYMENT'),
         messages=message)

    # calculate the amount of openai input tokens in the whole message using the tiktoken library
    # total_tokens = count_tokens(message)
    #print the number of tokens
    # print(f"Number of tokens: {total_tokens}")


    # create a dictionary to store the explanation, with the role and the content
    explanation = response.choices[0].message.content
    #return the list of explanations
    #explanation= "Test explanation"
    return explanation


def main():
    # set the image path to the directory image under the current directory
    image_path= "./image/chunks/"
    print(f"Reading chunks from {image_path}")
    chunks = read_chunks()
    # explain the image
    explanations = explain_image(chunks)
    print(explanations)
    print("Number of tokens on the first chunk")
    # look for the first file in the chunks directory
    #first_chunk = chunks[0]
    #print(explain_image_chunk( first_chunk))

if __name__ == "__main__":
    main()

