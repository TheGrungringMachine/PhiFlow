import os

import numpy

from phi import math
from phi.field import Scene
from phi.math import shape, wrap, channel, spatial
from phi.math.backend import PHI_LOGGER


@math.broadcast
def load_scalars(scene: Scene or str,
                 name: str,
                 prefix='log_',
                 suffix='.txt',
                 x='steps',
                 entries_dim=spatial('entries')):
    """
    Read one or a `Tensor` of scalar logs as curves.

    Args:
        scene: `Scene` or `str`. Directory containing the log files.
        name: Log file base name.
        prefix: Log file prefix.
        suffix: Log file suffix.
        x: 'steps'  or 'time'
        entries_dim: Curve dimension.

    Returns:
        `Tensor` containing `entries_dim` and `vector`.
    """
    assert x in ('steps', 'time')
    if isinstance(scene, str):
        scene = Scene.at(scene)
    assert isinstance(scene, Scene), f"scene must be a Scene or str but got {type(scene)}"
    assert shape(scene).rank == 0, f"Use math.map(load_scalars, ...) to load data from multiple scenes"
    PHI_LOGGER.debug(f"Reading {os.path.join(scene.path, f'{prefix}{name}{suffix}')}")
    curve = numpy.loadtxt(os.path.join(scene.path, f"log_{name}.txt"))
    if curve.ndim == 2:
        x_values, values, *_ = curve.T
    else:
        values = curve
        x_values = numpy.arange(len(values))
    if x == 'time':
        assert x == 'time', f"x must be 'steps' or 'time' but got {x}"
        PHI_LOGGER.debug(f"Reading {os.path.join(scene.path, 'log_step_time.txt')}")
        _, x_values, *_ = numpy.loadtxt(os.path.join(scene.path, "log_step_time.txt")).T
        values = values[:len(x_values + 1)]
        x_values = numpy.cumsum(x_values[:len(values) - 1])
        x_values = numpy.concatenate([[0.], x_values])
    return wrap(numpy.stack([x_values, values], -1), entries_dim, channel(vector=[x, name]))