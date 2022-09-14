# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Typing tests
------------
This test is meant to be both a runtime test and a static type annotation test,
so it should be checked with pytype/mypy as well as being run with pytest.
"""
from typing import Union

import jax
from jax._src import test_util as jtu
from jax._src import typing
from jax import lax
import jax.numpy as jnp

from absl.testing import absltest
import numpy as np


# DtypeLike is meant to annotate inputs to np.dtype that return
# a valid JAX dtype, so we test with np.dtype.
def dtypelike_to_dtype(x: typing.DtypeLike) -> typing.Dtype:
  return np.dtype(x)


# ArrayLike is meant to annotate object that are valid as array
# inputs to jax primitive functions; use convert_element_type here
# for simplicity.
def arraylike_to_array(x: typing.ArrayLike) -> typing.Array:
  return lax.convert_element_type(x, np.result_type(x))


class HasDtype:
  dtype: np.dtype
  def __init__(self, dt):
    self.dtype = np.dtype(dt)

float32_dtype = np.dtype("float32")


# Avoid test parameterization because we want to statically check these annotations.
class TypingTest(jtu.JaxTestCase):

  def testDtypeLike(self) -> None:
    out1: typing.Dtype = dtypelike_to_dtype("float32")
    self.assertEqual(out1, float32_dtype)

    out2: typing.Dtype = dtypelike_to_dtype(np.float32)
    self.assertEqual(out2, float32_dtype)

    out3: typing.Dtype = dtypelike_to_dtype(jnp.float32)
    self.assertEqual(out3, float32_dtype)

    out4: typing.Dtype = dtypelike_to_dtype(np.dtype('float32'))
    self.assertEqual(out4, float32_dtype)

    out5: typing.Dtype = dtypelike_to_dtype(HasDtype("float32"))
    self.assertEqual(out5, float32_dtype)

  def testArrayLike(self) -> None:
    out1: typing.Array = arraylike_to_array(jnp.arange(4))
    self.assertArraysEqual(out1, jnp.arange(4))

    out2: typing.Array = jax.jit(arraylike_to_array)(jnp.arange(4))
    self.assertArraysEqual(out2, jnp.arange(4))

    out3: typing.Array = arraylike_to_array(np.arange(4))
    self.assertArraysEqual(out3, jnp.arange(4))

    out4: typing.Array = arraylike_to_array(True)
    self.assertArraysEqual(out4, jnp.array(True))

    out5: typing.Array = arraylike_to_array(1)
    self.assertArraysEqual(out5, jnp.array(1))

    out6: typing.Array = arraylike_to_array(1.0)
    self.assertArraysEqual(out6, jnp.array(1.0))

    out7: typing.Array = arraylike_to_array(1 + 1j)
    self.assertArraysEqual(out7, jnp.array(1 + 1j))

    out8: typing.Array = arraylike_to_array(np.bool_(0))
    self.assertArraysEqual(out8, jnp.bool_(0))

    out9: typing.Array = arraylike_to_array(np.float32(0))
    self.assertArraysEqual(out9, jnp.float32(0))

  def testArrayInstanceChecks(self):
    # TODO(jakevdp): enable this test when `typing.Array` instance checks are implemented.
    self.skipTest("Test is broken for now.")

    def is_array(x: typing.ArrayLike) -> Union[bool, typing.Array]:
      return isinstance(x, typing.Array)

    x = jnp.arange(5)

    self.assertFalse(is_array(1.0))
    self.assertTrue(jax.jit(is_array)(1.0))
    self.assertTrue(is_array(x))
    self.assertTrue(jax.jit(is_array)(x))
    self.assertTrue(jnp.all(jax.vmap(is_array)(x)))


if __name__ == '__main__':
  absltest.main(testLoader=jtu.JaxTestLoader())
