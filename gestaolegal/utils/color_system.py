import colorsys
from typing import Dict, Tuple

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def generate_color_palette(base_color: str) -> Dict[str, str]:
    """Generate a complete color palette from base color."""
    # Convert hex to HSL for easier manipulation
    hex_color = base_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    # Generate secondary color using complementary color heuristic
    # Shift hue by 180 degrees (complementary) and adjust saturation/lightness for harmony
    secondary_h = (h + 0.5) % 1.0  # 180 degrees = 0.5 in normalized hue
    secondary_l = max(0.3, min(0.7, l))  # Keep lightness in a good range
    secondary_s = max(0.4, min(0.8, s * 0.8))  # Slightly reduce saturation for harmony
    
    palette = {
        'primary': base_color,
        'primary-light': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, min(1.0, l + 0.1), s))),
        'primary-dark': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, max(0.0, l - 0.1), s))),
        'primary-muted': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, l, max(0.0, s - 0.2)))),
        'primary-bright': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, min(1.0, l + 0.2), min(1.0, s + 0.1)))),
        
        # Secondary color and its variations
        'secondary': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, secondary_l, secondary_s))),
        'secondary-light': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, min(1.0, secondary_l + 0.1), secondary_s))),
        'secondary-dark': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, max(0.0, secondary_l - 0.1), secondary_s))),
        'secondary-muted': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, secondary_l, max(0.0, secondary_s - 0.2)))),
        'secondary-bright': rgb_to_hex(tuple(int(c * 255) for c in colorsys.hls_to_rgb(secondary_h, min(1.0, secondary_l + 0.2), min(1.0, secondary_s + 0.1)))),
    }
    
    return palette
