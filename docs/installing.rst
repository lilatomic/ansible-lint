
.. _installing_lint:


**********
Installing
**********

.. contents:: Topics

Installing on Windows is not supported because we use symlinks inside Python
packages.

While our project does not directly ship a container, the
tool is part of the toolset_ container.  Please avoid raising any bugs
related to containers and use the discussions_ forum instead.

.. code-block:: bash

    # replace docker with podman
    docker run -h toolset -it quay.io/ansible/toolset ansible-lint --version

.. _toolset: https://github.com/ansible-community/toolset
.. _discussions: https://github.com/ansible-community/ansible-lint/discussions

Using pip or pipx
-----------------

You can use either pip3_ or pipx_ to install it; the latter one
automatically isolates the linter from your current python environment.
That approach may avoid having to deal with particularities of installing
python packages, like creating a virtual environment, activating it, installing
using ``--user`` or fixing potential conflicts if not using virtualenvs.

.. code-block:: bash

    # This will also install ansible-core if needed
    pip3 install "ansible-lint"

.. _installing_from_source:
.. _pip3: https://pypi.org/project/pip/
.. _pipx: https://pypa.github.io/pipx/

From Source
-----------

**Note**: pip 19.0+ is required for installation. Please consult with the
`PyPA User Guide`_ to learn more about managing Pip versions.

.. code-block:: bash

    pip3 install git+https://github.com/ansible-community/ansible-lint.git

.. _PyPA User Guide: https://packaging.python.org/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
