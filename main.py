
import glob

from quart import Quart, request, jsonify, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename

app = Quart(__name__)
UPLOAD_FOLDER = 'uploads'

@app.route('/')
async def index():
    return jsonify({"message": "hi there"})

@app.route('/upload', methods=['POST'])
async def upload_image():
    form = await request.form
    blend_id = form.get('blend_id')
    lot_number = form.get('lot_number')
    if 'image' in (await request.files) and blend_id and lot_number:
        file = (await request.files)['image']
        extension = os.path.splitext(file.filename)[1]  # Extract file extension
        safe_blend_id = secure_filename(blend_id)
        safe_lot_number = secure_filename(lot_number)
        directory_path = os.path.join(UPLOAD_FOLDER, safe_blend_id)
        os.makedirs(directory_path, exist_ok=True)
        filename = f"{safe_lot_number}{extension}"  # Use lot number as filename
        save_path = os.path.join(directory_path, filename)
        await file.save(save_path)
        external_filename = filename.replace(".jpg", "").replace(".png", "")
        external_filename = external_filename.replace(".jpeg", "")
        external_path = f"http://51.81.166.148:25050/images/{safe_blend_id}/{external_filename}"
        print(f"Returning: {external_path}")
        return jsonify({'message': 'Image uploaded successfully', 'image_path': external_path}), 200
    else:
        return jsonify({'message': 'Missing image, blend ID, or lot number'}), 400


@app.route('/images/<blend_id>/<lot_number>')
async def serve_image(blend_id, lot_number):
    safe_blend_id = secure_filename(blend_id)
    directory_path = os.path.join(UPLOAD_FOLDER, safe_blend_id)
    # Search for any file format with the given lot_number
    file_pattern = os.path.join(directory_path, f"{lot_number}.*")
    matching_files = glob.glob(file_pattern)
    if matching_files:
        # Serve the first matching file
        return await send_file(matching_files[0])
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=25050,
            debug=True)
