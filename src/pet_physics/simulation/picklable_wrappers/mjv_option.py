"""Picklable wrapper for the MuJoCo `mujoco.MjvOption` class."""

import mujoco


class MjvOption:
    """Picklable wrapper around a `mujoco.MjvOption` instance."""

    def __init__(self):
        self._mjvoption = mujoco.MjvOption()

    # forward all calls to the _mjvoption instance
    def __getattr__(self, name):
        """Forwards attribute access to the wrapped `mujoco.MjvOption` instance."""
        return getattr(self._mjvoption, name)

    def __setattr__(self, name, value):
        """Forwards attribute assignment to the wrapped `mujoco.MjvOption` instance."""
        if name == "_mjvoption":
            super().__setattr__(name, value)
        else:
            setattr(self._mjvoption, name, value)

    def __getstate__(self):
        """Returns an empty state since `mujoco.MjvOption` is recreated on unpickling."""
        return {}

    def __setstate__(self, state):
        """Reinitializes the wrapped `mujoco.MjvOption` instance after unpickling."""
        self.__init__()
