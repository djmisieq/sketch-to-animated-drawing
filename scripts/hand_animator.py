#!/usr/bin/env python3
"""
Blender script for generating hand animation overlay frames.

This script is designed to be run with Blender to generate a sequence
of transparent PNG frames showing a hand drawing.

Usage:
    blender --background --python hand_animator.py -- --output=/path/to/output --frames=150 --width=1920 --height=1080
"""

import bpy
import sys
import os
import math
import argparse
from mathutils import Vector


def parse_arguments():
    """Parse command line arguments."""
    # Get all args after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Generate hand animation frames')
    parser.add_argument('--output', required=True, help='Output directory for frames')
    parser.add_argument('--frames', type=int, default=150, help='Number of frames to render')
    parser.add_argument('--width', type=int, default=1920, help='Output width')
    parser.add_argument('--height', type=int, default=1080, help='Output height')
    parser.add_argument('--hand-model', help='Path to hand model (optional)')
    
    return parser.parse_args(argv)


def setup_scene(width, height):
    """Set up the Blender scene."""
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Configure render settings
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.film_transparent = True  # Transparent background
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.compression = 15
    
    # Set up lighting
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Add camera
    bpy.ops.object.camera_add(location=(0, 0, 10))
    camera = bpy.context.active_object
    camera.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = camera
    
    # Set camera to orthographic for 2D look
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 12.0  # Adjust as needed
    
    return camera


def create_hand_model():
    """Create a simple 2D hand with Grease Pencil."""
    # Create a new Grease Pencil object
    bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
    gpencil = bpy.context.active_object
    gpencil.name = "Hand"
    
    # Create a new layer and frame
    gp_layer = gpencil.data.layers.new("HandLayer", set_active=True)
    gp_frame = gp_layer.frames.new(0)
    
    # Create the hand shape
    stroke = gp_frame.strokes.new()
    stroke.display_mode = '3DSPACE'
    
    # Define the hand shape points (simplified hand)
    points = [
        (0.0, -2.0, 0.0),    # Wrist
        (0.5, -1.5, 0.0),    # Palm
        (1.0, -1.0, 0.0),    # Base of fingers
        (1.5, -0.5, 0.0),    # Middle of hand
        (2.0, 0.0, 0.0),     # Knuckles
        (2.5, 0.5, 0.0),     # Index finger
        (3.0, 1.0, 0.0),     # Tip of index finger
        (2.5, 0.8, 0.0),     # Base of thumb
        (2.0, 0.6, 0.0),     # Middle of thumb
        (1.5, 0.4, 0.0),     # Tip of thumb
        (1.0, 0.2, 0.0),     # Side of hand
        (0.5, 0.0, 0.0),     # Base of hand
        (0.0, -2.0, 0.0),    # Back to wrist
    ]
    
    # Create a stroke
    stroke.points.add(len(points))
    for i, point in enumerate(points):
        stroke.points[i].co = Vector(point)
    
    # Set stroke attributes
    stroke.line_width = 50  # Adjust thickness
    
    # Set material
    mat = bpy.data.materials.new("HandMaterial")
    bpy.data.materials.create_gpencil_data(mat)
    mat.grease_pencil.color = (0.1, 0.1, 0.1, 1.0)  # Dark gray, opaque
    gpencil.data.materials.append(mat)
    
    return gpencil


def create_animation(hand, num_frames):
    """Create hand animation for drawing motion."""
    # Define animation path (simplified circular motion)
    def path_function(frame):
        """Generate position for a given frame."""
        progress = frame / num_frames
        radius = 3.0
        angle = progress * 2 * math.pi * 2  # Two full circles
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Add some variation to simulate drawing
        variation = math.sin(progress * 12 * math.pi) * 0.5
        
        return x + variation, y + variation, 0
    
    # Set up animation
    for frame in range(num_frames):
        # Set current frame
        bpy.context.scene.frame_set(frame)
        
        # Calculate position
        x, y, z = path_function(frame)
        
        # Set hand position
        hand.location = (x, y, z)
        
        # Set rotation to follow path tangent
        if frame > 0:
            prev_x, prev_y, _ = path_function(frame - 1)
            dx = x - prev_x
            dy = y - prev_y
            angle = math.atan2(dy, dx)
            hand.rotation_euler = (0, 0, angle)
        
        # Insert keyframes
        hand.keyframe_insert(data_path="location", frame=frame)
        hand.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Set animation range
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = num_frames - 1


def render_animation(output_dir, num_frames):
    """Render the animation frames."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output path
    bpy.context.scene.render.filepath = os.path.join(output_dir, "hand_")
    
    # Render frames
    for frame in range(num_frames):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = os.path.join(output_dir, f"hand_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered frame {frame+1}/{num_frames}")


def main():
    """Main function."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup scene
    camera = setup_scene(args.width, args.height)
    
    # Create or import hand model
    if args.hand_model and os.path.exists(args.hand_model):
        # Import external model
        if args.hand_model.endswith('.blend'):
            with bpy.data.libraries.load(args.hand_model) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects]
            hand = bpy.data.objects[-1]  # Assume last imported object is the hand
        else:
            # Import other formats
            bpy.ops.import_scene.obj(filepath=args.hand_model)
            hand = bpy.context.selected_objects[0]
    else:
        # Create simple hand model
        hand = create_hand_model()
    
    # Create animation
    create_animation(hand, args.frames)
    
    # Render animation
    render_animation(args.output, args.frames)
    
    print(f"Animation complete. Frames saved to {args.output}")


if __name__ == "__main__":
    main()
