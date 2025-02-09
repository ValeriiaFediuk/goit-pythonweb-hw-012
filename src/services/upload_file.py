import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    A service class to handle file uploads to Cloudinary.

    Args:
        cloud_name (str): Cloudinary cloud name.
        api_key (str): Cloudinary API key.
        api_secret (str): Cloudinary API secret.
    """
    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads a file to Cloudinary and returns a URL of the uploaded image.

        Args:
            file (Any): The file to upload (usually a file-like object).
            username (str): The username to be used for creating the public ID.

        Returns:
            str: The URL of the uploaded image with specific dimensions.
        
        Raises:
            Exception: If an error occurs during the file upload process.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url