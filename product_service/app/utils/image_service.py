import io
import uuid
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

try:
    import boto3
    from botocore.exceptions import ClientError
    R2_AVAILABLE = True
except ImportError:
    R2_AVAILABLE = False


class ImageService:
    def __init__(self):
        if R2_AVAILABLE:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.r2_endpoint_url,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                region_name=settings.r2_region
            )
            self.bucket_name = settings.r2_bucket_name
        else:
            self.s3_client = None
            self.bucket_name = None

    async def upload_image(self, file: UploadFile, folder: str) -> str:
        """Upload image to Cloudflare R2"""
        if not R2_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="R2 integration not available"
            )
            
        try:
            # Validate file
            if not self._is_valid_image(file):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image file"
                )
            
            # Compress image
            compressed_image = await self._compress_image(file)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            s3_key = f"{folder}/{unique_filename}"
            
            # Upload to R2
            self.s3_client.upload_fileobj(
                compressed_image,
                self.bucket_name,
                s3_key
            )
            
            # Return public URL
            return f"{settings.r2_endpoint_url}/{self.bucket_name}/{s3_key}"
            
        except ClientError as e:
            # Handle R2-specific errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to R2: {str(e)}"
            )
        except Exception as e:
            # Handle other errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {str(e)}"
            )

    def _is_valid_image(self, file: UploadFile) -> bool:
        """Validate image file type and size"""
        # Check file extension and size
        allowed_extensions = ['jpg', 'jpeg', 'png']
        file_extension = file.filename.split('.')[-1].lower()
        return (file_extension in allowed_extensions and 
                file.size <= 10 * 1024 * 1024)  # 10MB limit

    async def _compress_image(self, file: UploadFile) -> io.BytesIO:
        """Compress and resize image"""
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if larger than 1200x1200
        if image.width > 1200 or image.height > 1200:
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        # Compress to 80% quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=80, optimize=True)
        output.seek(0)
        
        return output