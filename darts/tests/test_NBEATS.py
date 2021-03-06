import shutil
import logging

from .base_test_class import DartsBaseTestClass
from ..utils import timeseries_generation as tg
from ..logging import get_logger

logger = get_logger(__name__)

try:
    from ..models.nbeats import NBEATSModel
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning('Torch not available. TCN tests will be skipped.')
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class NBEATSModelTestCase(DartsBaseTestClass):

        def test_creation(self):
            with self.assertRaises(ValueError):
                # if a list is passed to the `layer_widths` argument, it must have a length equal to `num_stacks`
                NBEATSModel(input_chunk_length=1, output_chunk_length=1, num_stacks=3, layer_widths=[1, 2])

        def test_fit(self):
            large_ts = tg.constant_timeseries(length=100, value=1000)
            small_ts = tg.constant_timeseries(length=100, value=10)

            # Test basic fit and predict
            model = NBEATSModel(input_chunk_length=1, output_chunk_length=1, n_epochs=10,
                                num_stacks=1, num_blocks=1, layer_widths=20)
            model.fit(large_ts[:98])
            pred = model.predict(n=2).values()[0]

            # Test whether model trained on one series is better than one trained on another
            model2 = NBEATSModel(input_chunk_length=1, output_chunk_length=1,
                                 n_epochs=10, num_stacks=1, num_blocks=1, layer_widths=20)
            model2.fit(small_ts[:98])
            pred2 = model2.predict(n=2).values()[0]
            self.assertTrue(abs(pred2 - 10) < abs(pred - 10))

            # test short predict
            pred3 = model2.predict(n=1)
            self.assertEqual(len(pred3), 1)

        def test_multivariate(self):
            series_multivariate = tg.linear_timeseries(length=100).stack(tg.linear_timeseries(length=100))
            model = NBEATSModel(input_chunk_length=1, output_chunk_length=1,
                                n_epochs=10, num_stacks=1, num_blocks=1, layer_widths=20)
            with self.assertRaises(ValueError):
                model.fit(series_multivariate)
