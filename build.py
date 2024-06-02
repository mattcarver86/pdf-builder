from PIL import Image
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Directory containing the images
image_directory = 'output'

# Output PDF file
output_pdf = 'atlas.pdf'

# Initialize the PDF canvas
c = canvas.Canvas(output_pdf, pagesize=A4)

# List all image files in the directory
image_files = [f for f in os.listdir(image_directory) if f.endswith(('jpeg', 'jpg', 'png'))]

# Sort the image files alphabetically
image_files.sort()

for image_file in image_files:
    # Get the characters between 'page-' and '.jpeg'
    page_number = image_file.split('page-')[1].split('.jpeg')[0]

    print(f"Building Page {page_number} from {image_file}...")
    
    image_path = os.path.join(image_directory, image_file)
    img = Image.open(image_path)
    
    # Convert to RGB if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Get image size and calculate ratio to fit A4 page
    img_width, img_height = img.size
    a4_width, a4_height = A4
    
    ratio = min(a4_width / img_width, a4_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)

    # Center the image on the page
    x_offset = (a4_width - new_width) / 2
    y_offset = (a4_height - new_height) / 2

    # Draw the image on the PDF
    c.drawImage(image_path, x_offset, y_offset, width=new_width, height=new_height)
    c.showPage()
    print(f"Added")

# Save the PDF
c.save()

print(f"Combined {len(image_files)} images into {output_pdf}")
