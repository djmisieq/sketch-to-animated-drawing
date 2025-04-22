"""Vectorizer module for converting raster images to vector SVG."""

import os
import subprocess
import tempfile
from pathlib import Path
import logging
from typing import Optional, Dict, Any, Union

from PIL import Image, ImageOps
import io

from app.config import settings

logger = logging.getLogger(__name__)


class Vectorizer:
    """Handles conversion of raster images (JPG/PNG) to vector SVG format using vtracer."""

    def __init__(
        self,
        vtracer_path: str = "vtracer",
        output_width: int = settings.VIDEO_WIDTH,
        output_height: int = settings.VIDEO_HEIGHT,
        color_mode: str = "binary",
        preset: str = "drawing",
        filter_speckle: int = 4,
        corner_threshold: float = 60.0,
        max_iterations: int = 10,
        splice_threshold: float = 45.0,
        path_precision: int = 8,
    ):
        """Initialize the vectorizer with the specified parameters.

        Args:
            vtracer_path: Path to vtracer executable
            output_width: Output SVG width
            output_height: Output SVG height
            color_mode: Color mode ('binary', 'color', 'posterize')
            preset: Preset optimization ('drawing', 'photo', 'pixel', 'none')
            filter_speckle: Filter speckles up to this size
            corner_threshold: Corner detection threshold (degrees)
            max_iterations: Maximum curve fitting iterations
            splice_threshold: Line splicing threshold (degrees)
            path_precision: Path precision (decimal places)
        """
        self.vtracer_path = vtracer_path
        self.output_width = output_width
        self.output_height = output_height
        self.color_mode = color_mode
        self.preset = preset
        self.filter_speckle = filter_speckle
        self.corner_threshold = corner_threshold
        self.max_iterations = max_iterations
        self.splice_threshold = splice_threshold
        self.path_precision = path_precision

    def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess image for better vectorization.

        Args:
            image_data: Raw image bytes

        Returns:
            bytes: Preprocessed image bytes
        """
        # Open image from bytes
        img = Image.open(io.BytesIO(image_data))

        # Convert to grayscale
        img = img.convert("L")

        # Resize to target dimensions preserving aspect ratio
        img.thumbnail((self.output_width, self.output_height), Image.Resampling.LANCZOS)

        # Enhance contrast
        img = ImageOps.autocontrast(img, cutoff=5)

        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    def vectorize(self, image_data: bytes) -> str:
        """Convert raster image to SVG.

        Args:
            image_data: Raw image bytes

        Returns:
            str: SVG content
        """
        # Preprocess the image
        preprocessed_data = self.preprocess_image(image_data)

        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_input:
            temp_input.write(preprocessed_data)
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace(".png", ".svg")

        try:
            # Build vtracer command
            cmd = [
                self.vtracer_path,
                "--input", temp_input_path,
                "--output", temp_output_path,
                "--mode", self.color_mode,
                "--preset", self.preset,
                "--filter-speckle", str(self.filter_speckle),
                "--corner-threshold", str(self.corner_threshold),
                "--max-iterations", str(self.max_iterations),
                "--splice-threshold", str(self.splice_threshold),
                "--path-precision", str(self.path_precision),
            ]

            # Run vtracer
            logger.info(f"Running vtracer: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                logger.error(f"vtracer failed with error: {result.stderr}")
                raise Exception(f"Vectorization failed: {result.stderr}")

            # Read the output SVG
            with open(temp_output_path, "r") as f:
                svg_content = f.read()

            return svg_content

        except subprocess.CalledProcessError as e:
            logger.error(f"vtracer process error: {e.stderr}")
            raise Exception(f"Vectorization process error: {e.stderr}")
        except Exception as e:
            logger.error(f"Vectorization error: {str(e)}")
            raise
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def optimize_svg(self, svg_content: str) -> str:
        """Optimize SVG for animation.

        This method cleans up the SVG, normalizes path data, and ensures
        all stroke properties are properly set for animation.

        Args:
            svg_content: Raw SVG content from vectorizer

        Returns:
            str: Optimized SVG content
        """
        try:
            # Here we would use a proper SVG parser, but for simplicity
            # we'll just do some basic string replacements

            # Set viewBox if not present
            if "viewBox" not in svg_content:
                svg_content = svg_content.replace(
                    "<svg", 
                    f'<svg viewBox="0 0 {self.output_width} {self.output_height}"',
                    1
                )

            # Set stroke properties for all paths if not present
            svg_content = svg_content.replace(
                "<path", 
                '<path stroke="#000000" stroke-width="2" fill="none"',
            )

            # Remove any fill attributes
            svg_content = svg_content.replace('fill="#000000"', 'fill="none"')
            
            # Add CSS for animation preparation
            animation_css = """
            <style>
                path {
                    stroke-dasharray: 1000;
                    stroke-dashoffset: 1000;
                }
            </style>
            """
            svg_content = svg_content.replace("</svg>", f"{animation_css}</svg>")

            return svg_content
        except Exception as e:
            logger.error(f"SVG optimization error: {str(e)}")
            # Return original if optimization fails
            return svg_content

    def process_image(self, image_data: bytes) -> str:
        """Complete process to convert image to optimized SVG.

        Args:
            image_data: Raw image bytes

        Returns:
            str: Optimized SVG content ready for animation
        """
        # Vectorize the image
        svg_content = self.vectorize(image_data)
        
        # Optimize for animation
        optimized_svg = self.optimize_svg(svg_content)
        
        return optimized_svg


# Create default vectorizer instance
vectorizer = Vectorizer()
