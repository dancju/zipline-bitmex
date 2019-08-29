Zipline BitMEX
==============

.. image:: https://img.shields.io/pypi/status/zipline-bitmex.svg
   :target: https://pypi.org/project/zipline-bitmex
.. image:: 	https://img.shields.io/pypi/dm/zipline-bitmex.svg
   :target: https://pypi.org/project/zipline-bitmex
.. image:: https://img.shields.io/pypi/pyversions/zipline-bitmex.svg
   :target: https://pypi.org/project/zipline-bitmex
.. image:: https://img.shields.io/pypi/v/zipline-bitmex.svg
   :target: https://pypi.org/project/zipline-bitmex

`BitMEX <https://bitmex.com>`_ bundle for `Zipline <https://github.com/quantopian/zipline>`_

**[WARNING]** This Python module is unusable by now due to `an upstream bug of Zipline <https://github.com/quantopian/zipline/issues/2405>`_. Unfortunately, it seems that Zipline is no longer under maintenance.

Usage
-----

1. Install this package with pip.

::

    pip install --user zipline-bitmex

2. Register this package to Zipline by amending the following script to ``~/.zipline/extension.py``.

.. code:: python

    from zipline.data.bundles import register
    from zipline_bitmex import bitmex_bundle
    import pandas as pd

    start = pd.Timestamp('2019-01-01', tz='utc')
    end = pd.Timestamp('2019-01-07', tz='utc')

    register(
        'bitmex',
        bitmex_bundle(['XBTUSD']),
        calendar_name='bitmex',
        start_session=start,
        end_session=end,
        minutes_per_day=24*60,
    )

3. Ingest the data bundle.

::

    zipline ingest -b bitmex
