Zipline BitMEX
==============

BitMEX bundle for `Zipline <https://github.com/quantopian/zipline>`_

Usage
-----

1. Install this package with pip:

::

    pip install zipline-bitmex

. You may want to run this command with ``--user`` parameter.

2. Register this package to Zipline by writing following content to
   ``$HOME/.zipline/extension.py``:

.. code:: python

    import pandas as pd
    from zipline.data.bundles import register
    from zipline_bitmex import bitmex

    start = pd.Timestamp('2017-08-01', tz='utc')
    end = pd.Timestamp('2017-08-08', tz='utc')

    register(
            'bitmex',
            bitmex(['XBTUSD', 'XBTU17']),
            calendar_name='bitmex',
            start_session=start,
            end_session=end,
            minutes_per_day=24*60)

3. Ingest the data bundle with:

::

    zipline ingest -b bitmex
