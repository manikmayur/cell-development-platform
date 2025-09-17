import plotly.graph_objects as go
import math


def calculate_unrolled_dimensions(
    inner_diameter: float,
    outer_diameter: float,
    positive_coating_thickness: float,
    negative_coating_thickness: float,
    separator_thickness: float,
    positive_foil_thickness: float,
    negative_foil_thickness: float,
    cylinder_height: float,
) -> dict:
    """
    Calculate unrolled electrode and separator dimensions for a cylindrical cell jelly roll.
    Layer order: negative coating, negative foil, negative coating, separator,
                 positive coating, positive foil, positive coating, separator.

    Parameters:
    inner_diameter (float): Inner diameter to first negative coating (mm)
    outer_diameter (float): Outer diameter to last positive coating (mm)
    positive_coating_thickness (float): Thickness of positive coating (mm)
    negative_coating_thickness (float): Thickness of negative coating (mm)
    separator_thickness (float): Thickness of separator (mm)
    positive_foil_thickness (float): Thickness of positive foil (mm)
    negative_foil_thickness (float): Thickness of negative foil (mm)
    cylinder_height (float): Height of the cylinder (mm)

    Returns:
    dict: Unrolled lengths, number of turns, layer thickness, and cylinder height
    """
    # Total thickness of one layer
    layer_thickness = (
        negative_coating_thickness * 2
        + negative_foil_thickness
        + separator_thickness * 2
        + positive_coating_thickness * 2
        + positive_foil_thickness
    )

    # Calculate the number of turns
    r_outer = outer_diameter / 2
    r_inner = inner_diameter / 2
    num_turns = (r_outer - r_inner) / layer_thickness
    area_jelly = math.pi * (r_outer**2 - r_inner**2)
    # avg_radius = (r_outer + r_inner) / 2
    unrolled_length = area_jelly / layer_thickness

    # Adjust lengths: positive coating and separator may be slightly longer
    negative_length = unrolled_length
    positive_length = (
        unrolled_length + 2 * math.pi * r_outer
    )  # Extra turn for outer wrap
    separator_length = unrolled_length + 2 * math.pi * r_outer  # Separator wraps both

    return {
        "negative_length": round(negative_length, 2),
        "positive_length": round(positive_length, 2),
        "separator_length": round(separator_length, 2),
        "num_turns": round(num_turns, 2),
        "layer_thickness": layer_thickness,
        "inner_radius": r_inner,
        "outer_radius": r_outer,
        "cylinder_height": cylinder_height,
    }


def generate_spiral_data(params):
    r_inner = params["inner_diameter"] / 2
    num_turns = params["num_turns"]
    # layer_thickness = params["layer_thickness"]
    layers = [
        ("Negative Coating", params["negative_coating_thickness"], "green"),
        ("Negative Foil", params["negative_foil_thickness"], "orange"),
        ("Negative Coating", params["negative_coating_thickness"], "green"),
        ("Separator", params["separator_thickness"], "blue"),
        ("Positive Coating", params["positive_coating_thickness"], "red"),
        ("Positive Foil", params["positive_foil_thickness"], "silver"),
        ("Positive Coating", params["positive_coating_thickness"], "red"),
        ("Separator", params["separator_thickness"], "blue"),
    ]
    traces = []
    annotations = []
    theta = [i * 2 * math.pi / 360 for i in range(361)]
    current_r = r_inner
    for layer_name, thickness, color in layers * int(num_turns):
        r = [current_r] * 361
        x = [r[i] * math.cos(theta[i]) for i in range(361)]
        y = [r[i] * math.sin(theta[i]) for i in range(361)]
        traces.append(
            go.Scatter(
                x=x,
                y=y,
                name=layer_name,
                mode="lines",
                line=dict(color=color, width=thickness * 20),  # Scaled for visibility
            )
        )
        # Add dimension annotation for first layer
        annotations.append(
            dict(
                x=current_r * math.cos(math.pi / 4),
                y=current_r * math.sin(math.pi / 4),
                xref="x",
                yref="y",
                text=f"{thickness:.3f} mm",
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=-20,
            )
        )
        current_r += thickness
    # Add inner, outer radius, and number of turns annotations
    annotations.extend(
        [
            dict(
                x=0,
                y=r_inner,
                xref="x",
                yref="y",
                text=f"R_inner: {r_inner:.2f} mm",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-30,
            ),
            dict(
                x=0,
                y=params["outer_radius"],
                xref="x",
                yref="y",
                text=f"R_outer: {params['outer_radius']:.2f} mm",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=30,
            ),
            dict(
                x=0,
                y=0,
                xref="x",
                yref="y",
                text=f"Turns: {params['num_turns']:.2f}",
                showarrow=False,
            ),
        ]
    )
    return traces, annotations


def generate_unrolled_data(params):
    traces = []
    annotations = []
    y_offset = 0
    layers = [
        (
            "Negative Coating",
            params["negative_length"],
            params["negative_coating_thickness"],
            "green",
        ),
        (
            "Negative Foil",
            params["negative_length"],
            params["negative_foil_thickness"],
            "orange",
        ),
        (
            "Negative Coating",
            params["negative_length"],
            params["negative_coating_thickness"],
            "green",
        ),
        (
            "Separator",
            params["separator_length"],
            params["separator_thickness"],
            "blue",
        ),
        (
            "Positive Coating",
            params["positive_length"],
            params["positive_coating_thickness"],
            "red",
        ),
        (
            "Positive Foil",
            params["positive_length"],
            params["positive_foil_thickness"],
            "silver",
        ),
        (
            "Positive Coating",
            params["positive_length"],
            params["positive_coating_thickness"],
            "red",
        ),
        (
            "Separator",
            params["separator_length"],
            params["separator_thickness"],
            "blue",
        ),
    ]
    # max_length = max(params['positive_length'], params['negative_length'], params['separator_length'])
    for name, length, thickness, color in layers:
        traces.append(
            go.Scatter(
                x=[0, length, length, 0, 0],
                y=[
                    y_offset,
                    y_offset,
                    y_offset + thickness * 10,
                    y_offset + thickness * 10,
                    y_offset,
                ],
                name=name,
                mode="lines",
                fill="toself",
                fillcolor=color,
                line=dict(color=color),
            )
        )
        # Add thickness annotation
        annotations.append(
            dict(
                x=length / 2,
                y=y_offset + thickness * 5,
                xref="x",
                yref="y",
                text=f"{thickness:.3f} mm",
                showarrow=False,
            )
        )
        y_offset += thickness * 10  # Scaled for visibility
    # Add length annotations
    annotations.extend(
        [
            dict(
                x=params["negative_length"],
                y=0,
                xref="x",
                yref="y",
                text=f"Neg: {params['negative_length']:.2f} mm",
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=-20,
            ),
            dict(
                x=params["positive_length"],
                y=y_offset / 2,
                xref="x",
                yref="y",
                text=f"Pos: {params['positive_length']:.2f} mm",
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=0,
            ),
            dict(
                x=params["separator_length"],
                y=y_offset,
                xref="x",
                yref="y",
                text=f"Sep: {params['separator_length']:.2f} mm",
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=20,
            ),
        ]
    )
    return traces, annotations


def generate_front_view(params):
    r_inner = params["inner_diameter"] / 2
    r_outer = params["outer_diameter"] / 2
    height = params["cylinder_height"]
    traces = []
    # Projection in xz-plane: rectangle with width = outer diameter, height = cylinder height
    traces.append(
        go.Scatter(
            x=[-r_outer, r_outer, r_outer, -r_outer, -r_outer],
            y=[0, 0, height, height, 0],
            mode="lines",
            line=dict(color="black", width=2),
            name="Outer Cylinder",
            fill="toself",
            fillcolor="rgba(0,0,0,0.1)",
        )
    )
    traces.append(
        go.Scatter(
            x=[-r_inner, r_inner, r_inner, -r_inner, -r_inner],
            y=[0, 0, height, height, 0],
            mode="lines",
            line=dict(color="black", width=2, dash="dash"),
            name="Inner Cylinder",
            fill="toself",
            fillcolor="rgba(255,255,255,1)",
        )
    )
    # Dimension annotations
    annotations = [
        dict(
            x=0,
            y=-10,
            xref="x",
            yref="y",
            text=f"D_outer: {params['outer_diameter']:.2f} mm",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
        ),
        dict(
            x=r_outer + 5,
            y=height / 2,
            xref="x",
            yref="y",
            text=f"H: {height:.2f} mm",
            showarrow=True,
            arrowhead=2,
            ax=50,
            ay=0,
        ),
        dict(
            x=0,
            y=height + 10,
            xref="x",
            yref="y",
            text=f"D_inner: {params['inner_diameter']:.2f} mm",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=30,
        ),
    ]
    return traces, annotations
