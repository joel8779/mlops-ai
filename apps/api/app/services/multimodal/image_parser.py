"""Image Parser - Parse and understand resume images."""

import io
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImageType(str, Enum):
    """Types of resume images."""

    PHOTO = "photo"
    SIGNATURE = "signature"
    DOCUMENT = "document"
    CHART = "chart"
    LOGO = "logo"
    UNKNOWN = "unknown"


@dataclass
class ImageRegion:
    """Detected region in an image."""

    region_type: ImageType
    bbox: Tuple[int, int, int, int]  # (left, top, right, bottom)
    confidence: float


@dataclass
class ParseResult:
    """Result of image parsing."""

    regions: list[ImageRegion]
    text_regions: list[ImageRegion]
    profile_image: Optional[bytes] = None
    signature: Optional[bytes] = None
    metadata: dict


class ImageParser:
    """Parse resume images to extract structured information."""

    def __init__(self) -> None:
        """Initialize image parser."""
        pass

    async def parse_resume_image(
        self,
        image_data: bytes,
    ) -> ParseResult:
        """Parse a resume image to extract regions and information.

        Args:
            image_data: Image bytes

        Returns:
            ParseResult with detected regions
        """
        image = Image.open(io.BytesIO(image_data))

        # Preprocess image
        processed = self._preprocess_image(image)

        # Detect regions
        regions = await self._detect_regions(processed)

        # Extract profile image if present
        profile_image = await self._extract_profile_image(processed, regions)

        # Extract signature if present
        signature = await self._extract_signature(processed, regions)

        return ParseResult(
            regions=regions,
            text_regions=[r for r in regions if r.region_type == ImageType.DOCUMENT],
            profile_image=profile_image,
            signature=signature,
            metadata={
                "original_size": image.size,
                "processed_size": processed.size,
                "format": image.format,
            },
        )

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better region detection.

        Args:
            image: PIL Image

        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != "L":
            image = image.convert("L")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Binarize
        threshold = 200
        image = image.point(lambda p: 255 if p > threshold else 0, "1")

        return image

    async def _detect_regions(self, image: Image.Image) -> list[ImageRegion]:
        """Detect different regions in the image.

        Args:
            image: Preprocessed PIL Image

        Returns:
            List of detected ImageRegion objects
        """
        regions = []
        np_image = np.array(image)

        # Simple region detection using connected components
        # In production, use a proper CV model like YOLO or Faster R-CNN

        # Detect potential photo regions (typically top-left or top-right)
        height, width = np_image.shape

        # Check top-left corner for profile photo
        top_left = np_image[:height // 3, :width // 3]
        if self._is_photo_region(top_left):
            regions.append(
                ImageRegion(
                    region_type=ImageType.PHOTO,
                    bbox=(0, 0, width // 3, height // 3),
                    confidence=0.8,
                )
            )

        # Check for signature (typically bottom-right)
        bottom_right = np_image[2 * height // 3 :, 2 * width // 3 :]
        if self._is_signature_region(bottom_right):
            regions.append(
                ImageRegion(
                    region_type=ImageType.SIGNATURE,
                    bbox=(2 * width // 3, 2 * height // 3, width, height),
                    confidence=0.7,
                )
            )

        # Detect text regions (document content)
        text_regions = self._detect_text_regions(np_image)
        regions.extend(text_regions)

        return regions

    def _is_photo_region(self, region: np.ndarray) -> bool:
        """Check if region is likely a profile photo.

        Args:
            region: Image region as numpy array

        Returns:
            True if likely a photo
        """
        # Photos typically have more variation than text
        std_dev = np.std(region)
        return std_dev > 50  # Threshold for variation

    def _is_signature_region(self, region: np.ndarray) -> bool:
        """Check if region is likely a signature.

        Args:
            region: Image region as numpy array

        Returns:
            True if likely a signature
        """
        # Signatures are typically sparse with thin lines
        pixel_ratio = np.sum(region > 0) / region.size
        return 0.05 < pixel_ratio < 0.3  # Sparse but not empty

    def _detect_text_regions(self, image: np.ndarray) -> list[ImageRegion]:
        """Detect text regions in the image.

        Args:
            image: Image as numpy array

        Returns:
            List of text regions
        """
        # Simple line detection
        height, width = image.shape
        regions = []

        # Scan for horizontal lines of text
        line_height = height // 30  # Approximate line height
        for y in range(0, height, line_height):
            line = image[y : y + line_height, :]
            if np.sum(line > 0) / line.size > 0.1:  # Has content
                regions.append(
                    ImageRegion(
                        region_type=ImageType.DOCUMENT,
                        bbox=(0, y, width, min(y + line_height, height)),
                        confidence=0.6,
                    )
                )

        return regions

    async def _extract_profile_image(
        self,
        image: Image.Image,
        regions: list[ImageRegion],
    ) -> Optional[bytes]:
        """Extract profile image from detected region.

        Args:
            image: PIL Image
            regions: Detected regions

        Returns:
            Profile image bytes or None
        """
        photo_regions = [r for r in regions if r.region_type == ImageType.PHOTO]
        if not photo_regions:
            return None

        # Extract the first photo region
        bbox = photo_regions[0].bbox
        cropped = image.crop(bbox)

        # Convert to bytes
        img_bytes = io.BytesIO()
        cropped.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    async def _extract_signature(
        self,
        image: Image.Image,
        regions: list[ImageRegion],
    ) -> Optional[bytes]:
        """Extract signature from detected region.

        Args:
            image: PIL Image
            regions: Detected regions

        Returns:
            Signature image bytes or None
        """
        sig_regions = [r for r in regions if r.region_type == ImageType.SIGNATURE]
        if not sig_regions:
            return None

        # Extract the first signature region
        bbox = sig_regions[0].bbox
        cropped = image.crop(bbox)

        # Convert to bytes
        img_bytes = io.BytesIO()
        cropped.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    async def enhance_image_for_ocr(self, image_data: bytes) -> bytes:
        """Enhance image for better OCR results.

        Args:
            image_data: Original image bytes

        Returns:
            Enhanced image bytes
        """
        image = Image.open(io.BytesIO(image_data))

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG", dpi=(300, 300))
        return img_bytes.getvalue()
