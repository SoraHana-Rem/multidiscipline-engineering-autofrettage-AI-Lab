from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import pytest

from src.physics.autofrettage import calculate_autofrettage_stresses
from src.visualization.plots import generate_residual_stress_plot


def test_generate_residual_stress_plot(tmp_path):
    """REQ-AUT-003: Export a non-empty residual-stress image."""
    output_file = tmp_path / "plots" / "residual.png"

    returned = generate_residual_stress_plot(
        r_i=50.0,
        r_o=70.0,
        sigma_y=250.0,
        P_auto=80.0,
        output_path=str(output_file),
    )

    assert returned == str(output_file)
    assert output_file.is_file()
    assert output_file.stat().st_size > 0


@pytest.mark.parametrize("pressure", [80.0, 90.0])
def test_plot_uses_solver_data_and_boundary(tmp_path, pressure):
    """REQ-AUT-001, REQ-AUT-003: Chart data and marker match solver."""
    expected = calculate_autofrettage_stresses(
        P_auto=pressure,
        r_i=50.0,
        r_o=70.0,
        sigma_y=250.0,
        num_points=200,
    )

    with patch.object(plt, "close", wraps=plt.close) as close_spy:
        generate_residual_stress_plot(
            r_i=50.0,
            r_o=70.0,
            sigma_y=250.0,
            P_auto=pressure,
            output_path=str(tmp_path / "residual.png"),
        )

    fig = close_spy.call_args.args[0]
    ax = fig.axes[0]

    stress_line = ax.lines[0]
    radii = stress_line.get_xdata()
    hoop = stress_line.get_ydata()

    np.testing.assert_allclose(radii, expected["radius"])
    np.testing.assert_allclose(hoop, expected["sigma_theta_res"])

    boundary_x = ax.lines[1].get_xdata()
    np.testing.assert_allclose(
        boundary_x,
        [expected["r_p"], expected["r_p"]],
    )

    assert hoop[0] < 0
    assert hoop[-1] > 0

    if pressure == 80.0:
        assert hoop[0] == pytest.approx(-37.991532, abs=1e-4)
        assert hoop[-1] == pytest.approx(3.214578, abs=1e-4)