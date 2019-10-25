# Copyright 2019 The TensorFlow-Determinism Authors. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================

# Reported at https://github.com/tensorflow/tensorflow/issues/33660
# TODO: See if this bug repros with tf.compat.v1.test.compute_gradient
#       (in graph mode)

import numpy as np
import tensorflow as tf

def empty(rank):
  shape = (0,) * rank
  return np.array([]).reshape(shape)

# Comment-out the first to run the second
tf.test.compute_gradient(tf.nn.bias_add, [empty(3), empty(1)])
tf.test.compute_gradient(tf.linalg.matmul, [empty(2), empty(3)])