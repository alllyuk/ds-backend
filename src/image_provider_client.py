import requests

class ImageProviderError(Exception):
    pass

class ImageNotFoundError(ImageProviderError):
    pass

class ImageProviderTimeoutError(ImageProviderError):
    pass

class ImageProviderUnavailableError(ImageProviderError):
    pass

class ImageProviderClient:
    def __init__(self, host="http://89.169.157.72:8080", timeout=5):
        self.host = host
        self.timeout = timeout

    def get_image(self, image_id):
        url = f"{self.host}/images/{image_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            raise ImageProviderTimeoutError()
        except requests.exceptions.ConnectionError:
            raise ImageProviderUnavailableError()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ImageNotFoundError()
            else:
                raise ImageProviderError()
