import logging
import io
import json
from flask import Flask, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from models.plate_reader import PlateReader, InvalidImage
from image_provider_client import ImageProviderClient, ImageNotFoundError, ImageProviderTimeoutError, ImageProviderUnavailableError

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
image_client = ImageProviderClient(timeout=5)


def process_image(image_id):
    try:
        image_data = image_client.get_image(image_id)
        plate_number = plate_reader.read_text(io.BytesIO(image_data))
        return {'image_id': image_id, 'plate_number': plate_number}, 200
    except ImageNotFoundError:
        logging.error(f'Image not found: {image_id}')
        return {'image_id': image_id, 'error': 'Image not found'}, 404
    except (ImageProviderTimeoutError, ImageProviderUnavailableError) as e:
        logging.error(f'Image provider error for {image_id}: {str(e)}')
        return {'image_id': image_id, 'error': 'Image service unavailable'}, 503
    except InvalidImage as e:
        logging.error(f'Invalid image {image_id}: {str(e)}')
        return {'image_id': image_id, 'error': 'Invalid image format'}, 400
    except Exception as e:
        logging.error(f"Unexpected error processing {image_id}: {str(e)}")
        return {'image_id': image_id, 'error': 'Internal server error'}, 500


@app.route('/readPlateNumberById', methods=['GET','POST'])
def handle_images():
    try:
        data = request.get_json()
        if not data:
            return Response(
                json.dumps({'error': 'No JSON data received'}, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=400
            )

        if 'image_id' in data:
            result, status = process_image(data['image_id'])
            return Response(
                json.dumps(result, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=status
            )

        elif 'image_ids' in data:
            if not isinstance(data['image_ids'], list):
                return Response(
                    json.dumps({'error': 'image_ids must be a list'}, ensure_ascii=False),
                    mimetype='application/json; charset=utf-8',
                    status=400
                )

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(process_image, data['image_ids']))

            # Extract responses and status codes
            responses = [r[0] for r in results]
            status_codes = [r[1] for r in results]  # Now guaranteed to have status codes

            # Determine overall status code
            if all(code == 200 for code in status_codes):
                overall_status = 200
            else:
                overall_status = max(status_codes)

            return Response(
                json.dumps(responses, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=overall_status
            )

        return Response(
            json.dumps({'error': 'Missing image_id or image_ids parameter'}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=400
        )

    except Exception as e:
        logging.error(f"Unexpected error in handler: {str(e)}")
        return Response(
            json.dumps({'error': 'Internal server error'}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=500
        )


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
