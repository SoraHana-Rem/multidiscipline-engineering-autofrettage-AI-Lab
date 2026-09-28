import os
from src.visualization.plots import generate_residual_stress_plot


def test_generate_residual_stress_plot():
    """Verifies that the plotting function executes and exports an image file."""
    output_file = "outputs/test_residual_stress.png"
    
    file_path = generate_residual_stress_plot(
        r_i=100.0,
        r_o=120.0,
        r_p=108.5,
        sigma_y=300.0,
        P_auto=58.0,
        output_path=output_file
    )

    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 0

    if os.path.exists(file_path):
        os.remove(file_path)