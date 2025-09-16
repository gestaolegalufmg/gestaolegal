import colorsys


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def hls_to_rgb_tuple(h: float, l: float, s: float) -> tuple[int, int, int]:
    rgb_float = colorsys.hls_to_rgb(h, l, s)
    return (int(rgb_float[0] * 255), int(rgb_float[1] * 255), int(rgb_float[2] * 255))


def generate_color_palette(base_color: str) -> dict[str, str]:
    hex_color = base_color.lstrip("#")
    rgb = (
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0,
    )
    h, l, s = colorsys.rgb_to_hls(*rgb)

    # Generate secondary color using complementary color heuristic
    # Shift hue by 180 degrees (complementary) and adjust saturation/lightness for harmony
    secondary_h = (h + 0.5) % 1.0  # 180 degrees = 0.5 in normalized hue
    secondary_l = max(0.3, min(0.7, l))
    secondary_s = max(0.4, min(0.8, s * 0.8))

    palette = {
        "primary": base_color,
        "primary-light": rgb_to_hex(hls_to_rgb_tuple(h, min(1.0, l + 0.1), s)),
        "primary-dark": rgb_to_hex(hls_to_rgb_tuple(h, max(0.0, l - 0.1), s)),
        "primary-muted": rgb_to_hex(hls_to_rgb_tuple(h, l, max(0.0, s - 0.2))),
        "primary-bright": rgb_to_hex(
            hls_to_rgb_tuple(h, min(1.0, l + 0.2), min(1.0, s + 0.1))
        ),
        "secondary": rgb_to_hex(
            hls_to_rgb_tuple(secondary_h, secondary_l, secondary_s)
        ),
        "secondary-light": rgb_to_hex(
            hls_to_rgb_tuple(secondary_h, min(1.0, secondary_l + 0.1), secondary_s)
        ),
        "secondary-dark": rgb_to_hex(
            hls_to_rgb_tuple(secondary_h, max(0.0, secondary_l - 0.1), secondary_s)
        ),
        "secondary-muted": rgb_to_hex(
            hls_to_rgb_tuple(secondary_h, secondary_l, max(0.0, secondary_s - 0.2))
        ),
        "secondary-bright": rgb_to_hex(
            hls_to_rgb_tuple(
                secondary_h,
                min(1.0, secondary_l + 0.2),
                min(1.0, secondary_s + 0.1),
            )
        ),
    }

    return palette
