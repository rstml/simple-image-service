from os import environ as env
from base64 import b64decode
from io import BytesIO
from uuid import uuid4
from chalice import Chalice, Response, BadRequestError, NotFoundError
from PIL import Image
from chalicelib.storage import S3Storage, MemoryStorage

# Initialise webapp
app = Chalice(app_name='progimage')
app.debug = True

# Make sure all supported image formats are registered
Image.init()

if env.get('S3_BUCKET_NAME'):
    store = S3Storage(env.get('S3_BUCKET_NAME'))
else:
    store = MemoryStorage()


@app.route('/v1/img', methods=['POST'])
def img_post():
    uuid = str(uuid4())

    try:
        request = app.current_request.json_body
        requestType = request['type']
        requestData = request['data']

        if requestType == 'base64':
            img_data = _load_from_base64(requestData)
        elif requestType == 'url':
            img_data = _load_from_url(requestData)
        elif requestType == 'uuid':
            img_data = _load_from_uuid(requestData)
        else:
            raise BadRequestError(f"Unknown request type: {requestType}")
    except KeyError:
        raise BadRequestError("Invalid request")

    _verify_image(img_data)
    store.put(uuid, img_data)

    return {'id': uuid}


@app.route('/v1/img/{filename}', methods=['GET'])
def img_get(filename):
    filters = app.current_request.query_params
    [uuid, extension] = filename.lower().split('.')

    format = Image.EXTENSION.get(f'.{extension}')

    if format is None:
        raise BadRequestError(f"Unsupported image format: {extension}")

    # Load original image
    orig_img_data = store.get(uuid)
    img = Image.open(orig_img_data)
    img = img.convert("RGB")

    # Apply filters
    if filters is not None:
        img = _apply_filters(img, filters)

    # Prepare image for response
    img_data = BytesIO()
    img.save(img_data, format, quality=90)
    img_data.seek(0)

    return Response(body=img_data.read(),
                    status_code=200,
                    headers={
                        'Content-Type': Image.MIME[format],
                        'Content-Disposition': f'inline; filename=\"{filename}\"'
                    })


def _apply_filters(img, filters):
    """Applies multiple image manipulation filters"""

    if 'thumbnail' in filters:
        size = int(filters['thumbnail']), int(filters['thumbnail'])
        img.thumbnail(size, resample=Image.LANCZOS)

    if 'rotate' in filters:
        angle = int(filters['rotate'])
        img = img.rotate(angle)

    ### TODO: Add more filters here

    return img


def _load_from_base64(b64_img_data: str) -> BytesIO:
    """Loads image data from Base64 encoded string"""
    img_data = BytesIO(b64decode(b64_img_data))
    return img_data


def _load_from_url(url: str) -> BytesIO:
    """Loads image data from remote URL"""
    raise BadRequestError(f"Request type is not implemented yet: url")


def _load_from_uuid(existing_uuid: str) -> BytesIO:
    """Loads image data from an existing image"""
    raise BadRequestError(f"Request type is not implemented yet: uuid")


def _verify_image(data: BytesIO):
    """Verify image format.
    Throws an exception if invalid or unsupported image detected.
    """
    img = Image.open(data)
    img.load()
    data.seek(0)
