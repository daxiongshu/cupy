import unittest

import cupy
from cupy.random import distributions
from cupy import testing

import numpy


_regular_float_dtypes = (numpy.float64, numpy.float32)
_float_dtypes = _regular_float_dtypes + (numpy.float16,)
_signed_dtypes = tuple(numpy.dtype(i).type for i in 'bhilq')
_unsigned_dtypes = tuple(numpy.dtype(i).type for i in 'BHILQ')
_int_dtypes = _signed_dtypes + _unsigned_dtypes


class RandomDistributionsTestCase(unittest.TestCase):
    def check_distribution(self, dist_name, params, dtype):
        cp_params = {k: cupy.asarray(params[k]) for k in params}
        np_out = getattr(numpy.random, dist_name)(
            size=self.shape, **params).astype(dtype)
        cp_out = getattr(distributions, dist_name)(
            size=self.shape, dtype=dtype, **cp_params)
        self.assertEqual(cp_out.shape, np_out.shape)
        self.assertEqual(cp_out.dtype, np_out.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'a_shape': [(), (3, 2)],
    'b_shape': [(), (3, 2)],
    'dtype': _float_dtypes,  # to escape timeout
})
)
@testing.gpu
class TestDistributionsBeta(RandomDistributionsTestCase):

    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['a_dtype', 'b_dtype'])
    def test_beta(self, a_dtype, b_dtype):
        a = numpy.full(self.a_shape, 3, dtype=a_dtype)
        b = numpy.full(self.b_shape, 3, dtype=b_dtype)
        self.check_distribution('beta',
                                {'a': a, 'b': b}, self.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'n_shape': [(), (3, 2)],
    'p_shape': [(), (3, 2)],
    'dtype': _int_dtypes,  # to escape timeout
})
)
@testing.gpu
class TestDistributionsBinomial(RandomDistributionsTestCase):

    @cupy.testing.for_signed_dtypes('n_dtype')
    @cupy.testing.for_float_dtypes('p_dtype')
    def test_binomial(self, n_dtype, p_dtype):
        n = numpy.full(self.n_shape, 5, dtype=n_dtype)
        p = numpy.full(self.p_shape, 0.5, dtype=p_dtype)
        self.check_distribution('binomial',
                                {'n': n, 'p': p}, self.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'df_shape': [(), (3, 2)],
})
)
@testing.gpu
class TestDistributionsChisquare(unittest.TestCase):

    def check_distribution(self, dist_func, df_dtype, dtype):
        df = cupy.full(self.df_shape, 5, dtype=df_dtype)
        out = dist_func(df, self.shape, dtype)
        self.assertEqual(self.shape, out.shape)
        self.assertEqual(out.dtype, dtype)

    @cupy.testing.for_float_dtypes('df_dtype')
    @cupy.testing.for_float_dtypes('dtype')
    def test_chisquare(self, df_dtype, dtype):
        self.check_distribution(distributions.chisquare, df_dtype, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2, 3), (3, 2, 3)],
    'alpha_shape': [(3,)],
})
)
@testing.gpu
class TestDistributionsDirichlet(RandomDistributionsTestCase):

    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['alpha_dtype', 'dtype'])
    def test_dirichlet(self, alpha_dtype, dtype):
        alpha = numpy.ones(self.alpha_shape, dtype=alpha_dtype)
        self.check_distribution('dirichlet',
                                {'alpha': alpha}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'shape_shape': [(), (3, 2)],
    'scale_shape': [(), (3, 2)],
    'dtype': _float_dtypes,  # to escape timeout
})
)
@testing.gpu
class TestDistributionsGamma(unittest.TestCase):

    def check_distribution(self, dist_func, shape_dtype, scale_dtype, dtype):
        shape = cupy.ones(self.shape_shape, dtype=shape_dtype)
        scale = cupy.ones(self.scale_shape, dtype=scale_dtype)
        out = dist_func(shape, scale, self.shape, dtype)
        self.assertEqual(self.shape, out.shape)
        self.assertEqual(out.dtype, dtype)

    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['shape_dtype', 'scale_dtype'])
    def test_gamma(self, shape_dtype, scale_dtype):
        self.check_distribution(distributions.gamma,
                                shape_dtype, scale_dtype, self.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'p_shape': [(), (3, 2)],
    'dtype': _int_dtypes,  # to escape timeout
})
)
@testing.gpu
class TestDistributionsGeometric(unittest.TestCase):

    def check_distribution(self, dist_func, p_dtype, dtype):
        p = 0.5 * cupy.ones(self.p_shape, dtype=p_dtype)
        out = dist_func(p, self.shape, dtype)
        self.assertEqual(self.shape, out.shape)
        self.assertEqual(out.dtype, dtype)

    @cupy.testing.for_float_dtypes('p_dtype')
    def test_geometric(self, p_dtype):
        self.check_distribution(distributions.geometric,
                                p_dtype, self.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'loc_shape': [(), (3, 2)],
    'scale_shape': [(), (3, 2)],
})
)
@testing.gpu
class TestDistributionsGumbel(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['loc_dtype', 'scale_dtype'])
    def test_gumbel(self, loc_dtype, scale_dtype, dtype):
        loc = numpy.ones(self.loc_shape, dtype=loc_dtype)
        scale = numpy.ones(self.scale_shape, dtype=scale_dtype)
        self.check_distribution('gumbel',
                                {'loc': loc, 'scale': scale}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'ngood_shape': [(), (3, 2)],
    'nbad_shape': [(), (3, 2)],
    'nsample_shape': [(), (3, 2)],
    'nsample_dtype': [numpy.int32, numpy.int64],  # to escape timeout
    'dtype': [numpy.int32, numpy.int64],  # to escape timeout
})
)
@testing.gpu
class TestDistributionsHyperGeometric(unittest.TestCase):

    def check_distribution(self, dist_func, ngood_dtype, nbad_dtype,
                           nsample_dtype, dtype):
        ngood = cupy.ones(self.ngood_shape, dtype=ngood_dtype)
        nbad = cupy.ones(self.nbad_shape, dtype=nbad_dtype)
        nsample = cupy.ones(self.nsample_shape, dtype=nsample_dtype)
        out = dist_func(ngood, nbad, nsample, self.shape, dtype)
        self.assertEqual(self.shape, out.shape)
        self.assertEqual(out.dtype, dtype)

    @cupy.testing.for_dtypes_combination(
        [numpy.int32, numpy.int64], names=['ngood_dtype', 'nbad_dtype'])
    def test_hypergeometric(self, ngood_dtype, nbad_dtype):
        self.check_distribution(distributions.hypergeometric, ngood_dtype,
                                nbad_dtype, self.nsample_dtype, self.dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'loc_shape': [(), (3, 2)],
    'scale_shape': [(), (3, 2)],
})
)
@testing.gpu
class TestDistributionsLaplace(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['loc_dtype', 'scale_dtype'])
    def test_laplace(self, loc_dtype, scale_dtype, dtype):
        loc = numpy.ones(self.loc_shape, dtype=loc_dtype)
        scale = numpy.ones(self.scale_shape, dtype=scale_dtype)
        self.check_distribution('laplace',
                                {'loc': loc, 'scale': scale}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'mean_shape': [()],
    'sigma_shape': [()],
})
)
@testing.gpu
class TestDistributionsLognormal(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['mean_dtype', 'sigma_dtype'])
    def test_lognormal(self, mean_dtype, sigma_dtype, dtype):
        mean = numpy.ones(self.mean_shape, dtype=mean_dtype)
        sigma = numpy.ones(self.sigma_shape, dtype=sigma_dtype)
        self.check_distribution('lognormal',
                                {'mean': mean, 'sigma': sigma}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'loc_shape': [(), (3, 2)],
    'scale_shape': [(), (3, 2)],
})
)
@testing.gpu
class TestDistributionsNormal(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['loc_dtype', 'scale_dtype'])
    def test_normal(self, loc_dtype, scale_dtype, dtype):
        loc = numpy.ones(self.loc_shape, dtype=loc_dtype)
        scale = numpy.ones(self.scale_shape, dtype=scale_dtype)
        self.check_distribution('normal',
                                {'loc': loc, 'scale': scale}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
})
)
@testing.gpu
class TestDistributionsStandardCauchy(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    def test_standard_cauchy(self, dtype):
        self.check_distribution('standard_cauchy', {}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
})
)
@testing.gpu
class TestDistributionsStandardExponential(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    def test_standard_exponential(self, dtype):
        self.check_distribution('standard_exponential', {}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
})
)
@testing.gpu
class TestDistributionsStandardNormal(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    def test_standard_normal(self, dtype):
        self.check_distribution('standard_normal', {}, dtype)


@testing.parameterize(*testing.product({
    'shape': [(4, 3, 2), (3, 2)],
    'low_shape': [(), (3, 2)],
    'high_shape': [(), (3, 2)],
})
)
@testing.gpu
class TestDistributionsUniform(RandomDistributionsTestCase):

    @cupy.testing.for_float_dtypes('dtype', no_float16=True)
    @cupy.testing.for_dtypes_combination(
        _float_dtypes, names=['low_dtype', 'high_dtype'])
    def test_uniform(self, low_dtype, high_dtype, dtype):
        low = numpy.ones(self.low_shape, dtype=low_dtype)
        high = numpy.ones(self.high_shape, dtype=high_dtype) * 2.
        self.check_distribution('uniform',
                                {'low': low, 'high': high}, dtype)
