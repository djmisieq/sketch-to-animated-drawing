"""Animator module for generating animated SVGs from static SVGs."""

import re
import xml.etree.ElementTree as ET
import drawsvg as draw
import logging
from typing import List, Dict, Any, Tuple, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class Animator:
    """Creates animated SVGs from static vector drawings."""

    def __init__(
        self,
        width: int = settings.VIDEO_WIDTH,
        height: int = settings.VIDEO_HEIGHT,
        fps: int = settings.VIDEO_FPS,
        animation_duration: float = 5.0,
        stroke_color: str = "#000000",
        stroke_width: float = 2.0,
        background_color: Optional[str] = None,
    ):
        """Initialize animator with the specified parameters.

        Args:
            width: SVG canvas width
            height: SVG canvas height
            fps: Frames per second for animation
            animation_duration: Duration of animation in seconds
            stroke_color: Color of the stroke
            stroke_width: Width of the stroke
            background_color: Background color (None for transparent)
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.animation_duration = animation_duration
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.background_color = background_color

    def _parse_svg(self, svg_content: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse SVG content and extract paths.

        Args:
            svg_content: SVG content as string

        Returns:
            Tuple containing SVG attributes and list of path data
        """
        # Parse SVG with xml.etree
        try:
            if isinstance(svg_content, str):
                # Clean up namespaces for easier parsing
                svg_content = re.sub(r'xmlns:xlink="[^"]+"', '', svg_content)
                svg_content = re.sub(r'xmlns="[^"]+"', '', svg_content)
            
            root = ET.fromstring(svg_content)
            
            # Get SVG attributes
            svg_attrs = {
                'width': root.get('width', str(self.width)),
                'height': root.get('height', str(self.height)),
                'viewBox': root.get('viewBox', f"0 0 {self.width} {self.height}"),
            }
            
            # Extract paths
            paths = []
            for path in root.findall('.//path'):
                path_data = {
                    'd': path.get('d', ''),
                    'stroke': path.get('stroke', self.stroke_color),
                    'stroke-width': path.get('stroke-width', str(self.stroke_width)),
                    'fill': path.get('fill', 'none'),
                }
                paths.append(path_data)
            
            return svg_attrs, paths
        
        except Exception as e:
            logger.error(f"Error parsing SVG: {str(e)}")
            # Return default values if parsing fails
            return {
                'width': str(self.width),
                'height': str(self.height),
                'viewBox': f"0 0 {self.width} {self.height}",
            }, []

    def _calculate_path_lengths(self, paths: List[Dict[str, Any]]) -> List[float]:
        """Calculate approximate path lengths for better animation timing.
        
        Args:
            paths: List of path data dictionaries
            
        Returns:
            List of approximate path lengths
        """
        # This is a simplified approximation
        # A more accurate method would involve actual path length calculation
        lengths = []
        
        for path in paths:
            # Count the number of commands in the path as a rough approximation
            d = path['d']
            # Count movement commands (M, L, C, Q, etc.)
            commands = len(re.findall(r'[MLHVCSQTAZmlhvcsqtaz]', d))
            # Count number points (pairs of numbers)
            points = len(re.findall(r'-?\d+\.?\d*', d)) / 2
            
            # Simplified length calculation
            length = commands * 10 + points * 5
            lengths.append(max(100, length))  # Minimum length of 100
            
        return lengths

    def create_animated_svg(self, svg_content: str) -> str:
        """Generate an animated SVG from a static SVG.

        Args:
            svg_content: Static SVG content as string

        Returns:
            Animated SVG content as string
        """
        # Parse SVG
        svg_attrs, paths = self._parse_svg(svg_content)
        
        # Calculate path lengths for timing
        path_lengths = self._calculate_path_lengths(paths)
        total_length = sum(path_lengths)
        
        # Create a new SVG with drawsvg
        d = draw.Drawing(
            width=self.width,
            height=self.height,
            origin=(0, 0),
            viewBox=svg_attrs.get('viewBox', f"0 0 {self.width} {self.height}")
        )
        
        # Add background if specified
        if self.background_color:
            d.append(draw.Rectangle(
                0, 0, self.width, self.height,
                fill=self.background_color,
            ))
        
        # Animation timing parameters
        total_duration = self.animation_duration * 1000  # ms
        current_time = 0
        
        # Add animated paths
        for i, (path_data, path_length) in enumerate(zip(paths, path_lengths)):
            # Calculate timing based on path length
            duration = (path_length / total_length) * total_duration if total_length > 0 else total_duration / len(paths)
            delay = current_time
            
            # Create path
            p = draw.Path(stroke=path_data.get('stroke', self.stroke_color),
                         stroke_width=float(path_data.get('stroke-width', self.stroke_width)),
                         fill=path_data.get('fill', 'none'),
                         d=path_data['d'])
            
            # Add dash array and offset for drawing animation
            p['stroke-dasharray'] = path_length
            p['stroke-dashoffset'] = path_length
            
            # Add animation
            anim = draw.AnimateMotion(
                'stroke-dashoffset',
                path_length,
                0,
                dur=f"{duration/1000}s",
                begin=f"{delay/1000}s",
                fill='freeze'
            )
            p.append(anim)
            d.append(p)
            
            # Update current time
            current_time += duration
        
        # Return SVG as string
        return d.as_str()

    def storyboard_frames(self, svg_content: str, num_frames: int = 10) -> List[str]:
        """Generate a series of SVG frames showing the animation progress.

        Args:
            svg_content: Static SVG content
            num_frames: Number of frames to generate

        Returns:
            List of SVG content strings representing animation frames
        """
        # Parse SVG
        svg_attrs, paths = self._parse_svg(svg_content)
        
        # Calculate path lengths
        path_lengths = self._calculate_path_lengths(paths)
        total_length = sum(path_lengths)
        
        frames = []
        
        # Generate frames at different animation states
        for frame in range(num_frames):
            # Calculate progress (0.0 to 1.0)
            progress = frame / (num_frames - 1) if num_frames > 1 else 1.0
            
            # Create SVG for this frame
            d = draw.Drawing(
                width=self.width,
                height=self.height,
                origin=(0, 0),
                viewBox=svg_attrs.get('viewBox', f"0 0 {self.width} {self.height}")
            )
            
            # Add background if specified
            if self.background_color:
                d.append(draw.Rectangle(
                    0, 0, self.width, self.height,
                    fill=self.background_color,
                ))
            
            # Determine which paths should be visible and how much
            cumulative_length = 0
            animation_progress = progress * total_length
            
            for i, (path_data, path_length) in enumerate(zip(paths, path_lengths)):
                # Calculate how much of this path to show
                if cumulative_length > animation_progress:
                    # Path not yet reached
                    continue
                
                if cumulative_length + path_length <= animation_progress:
                    # Path fully drawn
                    p = draw.Path(
                        stroke=path_data.get('stroke', self.stroke_color),
                        stroke_width=float(path_data.get('stroke-width', self.stroke_width)),
                        fill=path_data.get('fill', 'none'),
                        d=path_data['d']
                    )
                    d.append(p)
                else:
                    # Path partially drawn
                    p = draw.Path(
                        stroke=path_data.get('stroke', self.stroke_color),
                        stroke_width=float(path_data.get('stroke-width', self.stroke_width)),
                        fill=path_data.get('fill', 'none'),
                        d=path_data['d']
                    )
                    
                    # Calculate dashoffset
                    path_progress = (animation_progress - cumulative_length) / path_length
                    offset = path_length * (1 - path_progress)
                    
                    p['stroke-dasharray'] = path_length
                    p['stroke-dashoffset'] = offset
                    
                    d.append(p)
                
                cumulative_length += path_length
            
            # Add frame to list
            frames.append(d.as_str())
        
        return frames


# Create default animator instance
animator = Animator()
