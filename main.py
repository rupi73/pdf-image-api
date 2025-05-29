from fastapi import FastAPI, File, UploadFile
import fitz  # PyMuPDF
import os
import uuid

app = FastAPI()

@app.post("/extract-images")
async def extract_images(pdf_file: UploadFile = File(...)):
    contents = await pdf_file.read()
    file_id = str(uuid.uuid4())
    os.makedirs(f"output/{file_id}", exist_ok=True)

    input_path = f"output/{file_id}/input.pdf"
    with open(input_path, "wb") as f:
        f.write(contents)

    doc = fitz.open(input_path)
    images = []

    for page_index, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_index+1}_img{img_index+1}.{image_ext}"
            image_path = f"output/{file_id}/{image_filename}"
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            images.append({"file": image_filename, "url": f"/files/{file_id}/{image_filename}"})

    return {"id": file_id, "images": images}
