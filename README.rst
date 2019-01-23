Zipline BitMEX
==============

BitMEX bundle for `Zipline <https://github.com/quantopian/zipline>`_

**[WARNING]** There is a bug in this repo. It can ingest the data from the BitMEX API to the Zipline folder, but somehow I can't run an algorithm upon it. Any PRs or advice would be appreciated!

Usage
-----

1. Install this package with pip:

::

    pip install zipline-bitmex

. You may want to run this command with ``--user`` parameter.

2. Register this package to Zipline by writing following content to
   ``$HOME/.zipline/extension.py``:

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

3. Ingest the data bundle with:

::

    zipline ingest -b bitmex
