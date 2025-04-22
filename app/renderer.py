"""Renderer module for generating frames and compiling video."""

import os
import subprocess
import tempfile
import cairosvg
import numpy as np
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union
from PIL import Image
from moviepy.editor import ImageSequenceClip, VideoFileClip, CompositeVideoClip, ImageClip

from app.config import settings
from app.animator import animator

logger = logging.getLogger(__name__)


class Renderer:
    """Handles rendering of animated SVG to PNG frames and compiling to MP4."""

    def __init__(
        self,
        width: int = settings.VIDEO_WIDTH,
        height: int = settings.VIDEO_HEIGHT,
        fps: int = settings.VIDEO_FPS,
        duration: float = 5.0,
        output_format: str = "mp4",
        hand_overlay: bool = True,
        blender_path: str = "blender",
        blender_script_path: Optional[str] = None,
    ):
        """Initialize the renderer with the specified parameters.

        Args:
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second
            duration: Video duration in seconds
            output_format: Output video format ('mp4' or 'webm')
            hand_overlay: Whether to overlay a drawing hand
            blender_path: Path to Blender executable
            blender_script_path: Path to Blender script for hand animation
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.output_format = output_format
        self.hand_overlay = hand_overlay
        self.blender_path = blender_path
        self.blender_script_path = blender_script_path
        
        # Calculate total frames
        self.total_frames = int(self.fps * self.duration)

    def svg_to_png(self, svg_content: str, output_path: str) -> None:
        """Convert SVG to PNG.

        Args:
            svg_content: SVG content as string
            output_path: Path to save PNG
        """
        try:
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=output_path,
                output_width=self.width,
                output_height=self.height,
            )
        except Exception as e:
            logger.error(f"Error converting SVG to PNG: {str(e)}")
            raise

    def generate_animation_frames(self, svg_content: str, output_dir: str) -> List[str]:
        """Generate PNG frames from animated SVG.

        Args:
            svg_content: SVG content
            output_dir: Directory to save frames

        Returns:
            List of frame file paths
        """
        frame_paths = []
        
        try:
            # Make sure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate frames using animator
            frame_svgs = animator.storyboard_frames(
                svg_content, 
                num_frames=self.total_frames
            )
            
            # Convert SVGs to PNGs
            for i, frame_svg in enumerate(frame_svgs):
                frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
                self.svg_to_png(frame_svg, frame_path)
                frame_paths.append(frame_path)
                
            return frame_paths
        
        except Exception as e:
            logger.error(f"Error generating animation frames: {str(e)}")
            raise

    def generate_hand_frames(self, output_dir: str) -> List[str]:
        """Generate hand animation frames using Blender.

        Args:
            output_dir: Directory to save frames

        Returns:
            List of frame file paths
        """
        if not self.hand_overlay or not self.blender_script_path:
            logger.info("Hand overlay disabled or Blender script not provided")
            return []
            
        try:
            # Make sure output directory exists
            hand_output_dir = os.path.join(output_dir, "hand")
            os.makedirs(hand_output_dir, exist_ok=True)
            
            # Call Blender to generate hand animation
            blender_cmd = [
                self.blender_path,
                "--background",
                "--python", self.blender_script_path,
                "--",  # Pass remaining arguments to the script
                f"--output={hand_output_dir}",
                f"--frames={self.total_frames}",
                f"--width={self.width}",
                f"--height={self.height}",
            ]
            
            logger.info(f"Running Blender: {' '.join(blender_cmd)}")
            result = subprocess.run(
                blender_cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            
            if result.returncode != 0:
                logger.error(f"Blender failed with error: {result.stderr}")
                raise Exception(f"Hand animation generation failed: {result.stderr}")
            
            # Collect generated frame paths
            frame_paths = []
            for i in range(self.total_frames):
                frame_path = os.path.join(hand_output_dir, f"hand_{i:04d}.png")
                if os.path.exists(frame_path):
                    frame_paths.append(frame_path)
            
            return frame_paths
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Blender process error: {e.stderr}")
            # Continue without hand overlay if Blender fails
            logger.info("Continuing without hand overlay")
            return []
        except Exception as e:
            logger.error(f"Error generating hand frames: {str(e)}")
            # Continue without hand overlay
            logger.info("Continuing without hand overlay")
            return []

    def compose_frames(
        self, drawing_frames: List[str], hand_frames: List[str], output_dir: str
    ) -> List[str]:
        """Compose drawing and hand frames together.

        Args:
            drawing_frames: List of drawing frame paths
            hand_frames: List of hand frame paths
            output_dir: Directory to save composed frames

        Returns:
            List of composed frame paths
        """
        composed_frames = []
        
        try:
            # Make sure output directory exists
            composed_dir = os.path.join(output_dir, "composed")
            os.makedirs(composed_dir, exist_ok=True)
            
            # If no hand frames, just return drawing frames
            if not hand_frames:
                return drawing_frames
                
            # Compose each frame
            for i, drawing_path in enumerate(drawing_frames):
                # Skip if we don't have a matching hand frame
                if i >= len(hand_frames):
                    break
                    
                # Load images
                drawing = Image.open(drawing_path).convert("RGBA")
                hand = Image.open(hand_frames[i]).convert("RGBA")
                
                # Resize hand if needed
                if hand.size != (self.width, self.height):
                    hand = hand.resize((self.width, self.height), Image.Resampling.LANCZOS)
                
                # Compose images (hand over drawing)
                composed = Image.alpha_composite(drawing, hand)
                
                # Save composed frame
                composed_path = os.path.join(composed_dir, f"frame_{i:04d}.png")
                composed.save(composed_path)
                composed_frames.append(composed_path)
                
            return composed_frames if composed_frames else drawing_frames
        
        except Exception as e:
            logger.error(f"Error composing frames: {str(e)}")
            # Return drawing frames if composition fails
            return drawing_frames

    def compile_video(self, frame_paths: List[str], output_path: str) -> str:
        """Compile frames into a video.

        Args:
            frame_paths: List of frame paths
            output_path: Path to save video

        Returns:
            Path to the created video file
        """
        try:
            # Create clip from image sequence
            clip = ImageSequenceClip(frame_paths, fps=self.fps)
            
            # Set output codec and format
            codec = 'libx264'
            if self.output_format == 'webm':
                codec = 'libvpx-vp9'
                if not output_path.endswith('.webm'):
                    output_path = f"{os.path.splitext(output_path)[0]}.webm"
            else:
                if not output_path.endswith('.mp4'):
                    output_path = f"{os.path.splitext(output_path)[0]}.mp4"
            
            # Write video file
            clip.write_videofile(
                output_path,
                codec=codec,
                fps=self.fps,
                threads=4,
                preset='medium',
                bitrate='5000k',
            )
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error compiling video: {str(e)}")
            raise

    def render(self, svg_content: str, output_path: str) -> str:
        """Render SVG to video with all steps.

        Args:
            svg_content: SVG content
            output_path: Path to save video

        Returns:
            Path to the created video file
        """
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                logger.info(f"Starting rendering process to {output_path}")
                
                # Generate animation frames
                logger.info("Generating animation frames...")
                drawing_frames = self.generate_animation_frames(svg_content, temp_dir)
                
                # Generate hand frames if enabled
                final_frames = drawing_frames
                if self.hand_overlay:
                    logger.info("Generating hand frames...")
                    hand_frames = self.generate_hand_frames(temp_dir)
                    
                    if hand_frames:
                        logger.info("Composing frames...")
                        final_frames = self.compose_frames(drawing_frames, hand_frames, temp_dir)
                
                # Compile video
                logger.info("Compiling video...")
                video_path = self.compile_video(final_frames, output_path)
                
                logger.info(f"Video rendered successfully to {video_path}")
                return video_path
                
            except Exception as e:
                logger.error(f"Error in render process: {str(e)}")
                raise


# Create default renderer instance
renderer = Renderer()
