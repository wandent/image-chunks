

# create a function that will take a file path and split into chunks with a given size of height and width

import os
from PIL import Image
import argparse

def split_image(image_path, chunk_height, chunk_width):
    # Load the image
    image = Image.open(image_path)
    image_width, image_height = image.size

    # Create a directory to save the chunks
    output_dir = os.path.join(os.path.dirname(image_path), 'chunks')
    os.makedirs(output_dir, exist_ok=True)

    # Split the image into chunks
    for i in range(0, image_height, chunk_height):
        for j in range(0, image_width, chunk_width):
            box = (j, i, min(j + chunk_width, image_width), min(i + chunk_height, image_height))
            chunk = image.crop(box)
            chunk.save(os.path.join(output_dir, f'chunk_{i // chunk_height}_{j // chunk_width}.png'))

    print(f"Chunks saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Split an image into chunks of a given size.')
    parser.add_argument('image_path', type=str, help='Path to the image file')
    parser.add_argument('chunk_height', type=int, help='Height of each chunk')
    parser.add_argument('chunk_width', type=int, help='Width of each chunk')
    args = parser.parse_args()
    split_image(args.image_path, args.chunk_height, args.chunk_width)

# call the main function
if __name__ == "__main__":
    main()

# Example usage:
# python chunk-image.py path/to/image.png 100 100

