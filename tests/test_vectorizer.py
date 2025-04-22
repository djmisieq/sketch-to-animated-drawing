"""Tests for the vectorizer module."""

import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import xml.etree.ElementTree as ET
import subprocess
from io import BytesIO
from PIL import Image

from app.vectorizer import Vectorizer


def create_test_image(width=100, height=100):
    """Create a simple test image."""
    img = Image.new('RGB', (width, height), color='white')
    # Draw a simple black line
    for i in range(10, 90):
        img.putpixel((i, 50), (0, 0, 0))
    
    # Convert to bytes
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io.read()


class TestVectorizer:
    """Tests for the Vectorizer class."""

    def test_initialization(self):
        """Test that the vectorizer initializes with default parameters."""
        vectorizer = Vectorizer()
        assert vectorizer.vtracer_path == "vtracer"
        assert vectorizer.color_mode == "binary"
        assert vectorizer.preset == "drawing"

    def test_preprocess_image(self):
        """Test image preprocessing."""
        vectorizer = Vectorizer()
        test_image = create_test_image()
        
        # Process the image
        processed_data = vectorizer.preprocess_image(test_image)
        
        # Check that we got bytes back
        assert isinstance(processed_data, bytes)
        
        # Check that it's a valid image
        img = Image.open(BytesIO(processed_data))
        assert img.mode == 'L'  # Should be grayscale

    @patch('subprocess.run')
    def test_vectorize_subprocess_call(self, mock_run):
        """Test that vectorize calls the vtracer subprocess with correct args."""
        # Setup mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Setup temp file mock
        with patch('tempfile.NamedTemporaryFile'):
            with patch("builtins.open", mock_open(read_data="<svg></svg>")):
                vectorizer = Vectorizer()
                test_image = create_test_image()
                
                # Call the function
                result = vectorizer.vectorize(test_image)
                
                # Check subprocess was called
                assert mock_run.called
                
                # Check correct arguments
                args = mock_run.call_args[0][0]
                assert args[0] == "vtracer"
                assert "--mode" in args
                assert "binary" in args

    @patch('subprocess.run')
    def test_vectorize_error_handling(self, mock_run):
        """Test error handling in vectorize method."""
        # Setup mock to raise exception
        mock_run.side_effect = subprocess.CalledProcessError(1, 'vtracer', stderr="Mock error")
        
        vectorizer = Vectorizer()
        test_image = create_test_image()
        
        # Test that exception is raised
        with pytest.raises(Exception) as exc_info:
            vectorizer.vectorize(test_image)
        
        assert "Vectorization process error" in str(exc_info.value)

    def test_optimize_svg(self):
        """Test SVG optimization."""
        vectorizer = Vectorizer(output_width=800, output_height=600)
        
        # Create a simple SVG
        svg_content = '<svg><path d="M10 10 L90 90" /></svg>'
        
        # Optimize it
        result = vectorizer.optimize_svg(svg_content)
        
        # Check that viewBox was added
        assert 'viewBox="0 0 800 600"' in result
        
        # Check that stroke properties were added
        assert 'stroke="#000000"' in result
        assert 'stroke-width="2"' in result
        assert 'fill="none"' in result
        
        # Check that animation CSS was added
        assert '<style>' in result
        assert 'stroke-dasharray' in result

    @patch('app.vectorizer.Vectorizer.vectorize')
    @patch('app.vectorizer.Vectorizer.optimize_svg')
    def test_process_image(self, mock_optimize, mock_vectorize):
        """Test the complete process_image flow."""
        # Setup mocks
        mock_vectorize.return_value = "<svg><path /></svg>"
        mock_optimize.return_value = "<svg><path optimized /></svg>"
        
        vectorizer = Vectorizer()
        test_image = create_test_image()
        
        # Call the function
        result = vectorizer.process_image(test_image)
        
        # Check mocks were called
        assert mock_vectorize.called
        mock_vectorize.assert_called_with(test_image)
        
        assert mock_optimize.called
        mock_optimize.assert_called_with("<svg><path /></svg>")
        
        # Check final result
        assert result == "<svg><path optimized /></svg>"
