"""Jupyter notebook plotting module."""
# flake8: noqa: F401

import warnings

import pyvista
from pyvista.errors import PyVistaDeprecationWarning

ALLOWED_BACKENDS = [
    'ipyvtklink',
    'panel',
    'ipygany',
    'static',
    'pythreejs',
    'client',
    'server',
    'trame',
    'none',
]


def _validate_jupyter_backend(backend):
    """Validate that a jupyter backend is valid.

    Returns the normalized name of the backend. Raises if the backend is invalid.

    """
    # Must be a string
    if backend is None:
        backend = 'none'
    backend = backend.lower()

    try:
        import IPython
    except ImportError:  # pragma: no cover
        raise ImportError('Install IPython to display with pyvista in a notebook.')

    if backend == 'ipyvtk_simple':
        try:
            import ipyvtklink
        except ImportError:
            raise ImportError('Please install `ipyvtklink`. `ipyvtk_simple` ' 'is deprecated.')
        else:
            backend = 'ipyvtklink'

    if backend not in ALLOWED_BACKENDS:
        backend_list_str = ', '.join([f'"{item}"' for item in ALLOWED_BACKENDS])
        raise ValueError(
            f'Invalid Jupyter notebook plotting backend "{backend}".\n'
            f'Use one of the following:\n{backend_list_str}'
        )

    # verify required packages are installed
    if backend == 'pythreejs':
        try:
            import pythreejs
        except ImportError:  # pragma: no cover
            raise ImportError('Please install `pythreejs` to use this feature.')
        if not pyvista.BUILDING_GALLERY:
            warnings.warn(
                '`pythreejs` backend is deprecated and is planned for future removal.',
                PyVistaDeprecationWarning,
                stacklevel=3,
            )

    if backend == 'ipyvtklink':
        if not pyvista.BUILDING_GALLERY:
            warnings.warn(
                '`ipyvtklink` backend is deprecated and has been replaced by the `trame` backend.',
                PyVistaDeprecationWarning,
                stacklevel=3,
            )
        try:
            import ipyvtklink
        except ImportError:  # pragma: no cover
            raise ImportError('Please install `ipyvtklink` to use this feature.')

    if backend == 'panel':
        try:
            import panel
        except ImportError:  # pragma: no cover
            raise ImportError('Please install `panel` to use this feature.')
        panel.extension('vtk')
        if not pyvista.BUILDING_GALLERY:
            warnings.warn(
                '`panel` backend is deprecated and is planned for future removal.',
                PyVistaDeprecationWarning,
                stacklevel=3,
            )

    if backend == 'ipygany':
        # raises an import error when fail
        from pyvista.jupyter import pv_ipygany

        if not pyvista.BUILDING_GALLERY:
            warnings.warn(
                '`ipygany` backend is deprecated and is planned for future removal.',
                PyVistaDeprecationWarning,
                stacklevel=3,
            )

    if backend in ['server', 'client', 'trame']:
        try:
            from pyvista.trame.jupyter import show_trame
        except ImportError:  # pragma: no cover
            raise ImportError('Please install `trame` and `ipywidgets` to use this feature.')

    if backend == 'none':
        backend = None
    return backend


def set_jupyter_backend(backend):
    """Set the plotting backend for a jupyter notebook.

    Parameters
    ----------
    backend : str
        Jupyter backend to use when plotting.  Must be one of the following:

        * ``'ipyvtklink'`` : Render remotely and stream the
          resulting VTK images back to the client.  Supports all VTK
          methods, but suffers from lag due to remote rendering.
          Requires that a virtual framebuffer be set up when displaying
          on a headless server.  Must have ``ipyvtklink`` installed.

        * ``'panel'`` : Convert the VTK render window to a vtkjs
          object and then visualize that within jupyterlab. Supports
          most VTK objects.  Requires that a virtual framebuffer be
          set up when displaying on a headless server.  Must have
          ``panel`` installed.

        * ``'ipygany'`` : Convert all the meshes into ``ipygany``
          meshes and streams those to be rendered on the client side.
          Supports VTK meshes, but few others.  Aside from ``none``,
          this is the only method that does not require a virtual
          framebuffer.  Must have ``ipygany`` installed.

        * ``'pythreejs'`` : Convert all the meshes into ``pythreejs``
          meshes and streams those to be rendered on the client side.
          Aside from ``ipygany``, this is the only method that does
          not require a virtual framebuffer.  Must have ``pythreejs``
          installed.

        * ``'static'`` : Display a single static image within the
          Jupyterlab environment.  Still requires that a virtual
          framebuffer be set up when displaying on a headless server,
          but does not require any additional modules to be installed.

        * ``'client'`` : Export/serialize the scene graph to be rendered
          with VTK.js client-side through ``trame``. Requires ``trame``
          and ``jupyter-server-proxy`` to be installed.

        * ``'server'``: Render remotely and stream the resulting VTK
          images back to the client using ``trame``. This replaces the
          ``'ipyvtklink'`` backend with better performance.
          Supports the most VTK features, but suffers from minor lag due
          to remote rendering. Requires that a virtual framebuffer be set
          up when displaying on a headless server. Must have at least ``trame``
          and ``jupyter-server-proxy`` installed for cloud/remote Jupyter
          instances. This mode is also aliased by ``'trame'``.

        * ``'trame'``: The full Trame-based backend that combines both
          ``'server'`` and ``'client'`` into one backend. This requires a
          virtual frame buffer.

        * ``'none'`` : Do not display any plots within jupyterlab,
          instead display using dedicated VTK render windows.  This
          will generate nothing on headless servers even with a
          virtual framebuffer.

    Examples
    --------
    Enable the pythreejs backend.

    >>> import pyvista as pv
    >>> pv.set_jupyter_backend('pythreejs')  # doctest:+SKIP

    Enable the ipygany backend.

    >>> import pyvista as pv
    >>> pv.set_jupyter_backend('ipygany')  # doctest:+SKIP

    Enable the panel backend.

    >>> pv.set_jupyter_backend('panel')  # doctest:+SKIP

    Enable the ipyvtklink backend.

    >>> pv.set_jupyter_backend('ipyvtklink')  # doctest:+SKIP

    Enable the trame Trame backend.

    >>> pv.set_jupyter_backend('trame')  # doctest:+SKIP

    Just show static images.

    >>> pv.set_jupyter_backend('static')  # doctest:+SKIP

    Disable all plotting within JupyterLab and display using a
    standard desktop VTK render window.

    >>> pv.set_jupyter_backend(None)  # doctest:+SKIP

    """
    pyvista.global_theme._jupyter_backend = _validate_jupyter_backend(backend)
    if backend in ['server', 'client', 'trame']:
        # Launch the trame server
        from pyvista.trame.jupyter import elegantly_launch

        elegantly_launch(pyvista.global_theme.trame.jupyter_server_name)
