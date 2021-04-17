# Status of GPU-Determinism in TensorFlow

## Introduction

This page provides an up-to-date view of the status of GPU-related sources of
nondeterminism in TensorFlow. This is almost exclusively focused on the
determinsitic functionality of ops running on a GPU.

For a broader view, see the [TensorFlow Determinism](./README.md) page.

## Summary

The following table indicates whether a solution is available for each source.
For further information, see the later detailed notes, which are linked to
from the "Solution Available" column.

 Source                                                                  | Solution Available                     |
-------------------------------------------------------------------------|:---------------------------------------|
 Auto-tuning of cuDNN convolution algorithms                             | [YES](#auto-tuning)                    |
 `tfa.image.dense_image_warp` backprop                                   | [unreleased patch](#dense-image-warp)  |
 `tf.compat.v1.nn.fused_batch_norm` backrop                              | [NO](#fused-batch-norm)                |
 `tf.convert_to_tensor` forward, for `tf.IndexedSlices`                  | [unreleased patch](#convert-to-tensor) |
 `tf.gather` backprop                                                    | [unreleased patch](#gather)            |
 `tf.keras.layers.Conv1D` backprop                                       | [YES](#cudnn-conv)                     |
 `tf.keras.layers.Conv2D` backprop                                       | [YES](#cudnn-conv)                     |
 `tf.keras.layers.Conv3D` backprop                                       | [YES](#cudnn-conv)                     |
 `tf.keras.layers.MaxPool1D` backprop                                    | [YES](#max-pool)                       |
 `tf.keras.layers.MaxPool2D` backprop                                    | [YES](#max-pool)                       |
 `tf.keras.layers.MaxPool3D` backprop                                    | [YES](#max-pool)                       |
 `tf.keras.layers.UpSampling2D` backprop when `interpolation='bilinear'` | [YES](#resize-bilinear)                |
 `tf.keras.layers.UpSampling2D` backprop with `interpolation='nearest'`  | [NO](#resize-nearest)                  |
 `tf.keras.losses.categorical_crossentropy` forward and backprop         | [work-around](#softmax-xent)           |
 `tf.keras.losses.CategoricalCrossentropy` forward and backprop          | [work-around](#softmax-xent)           |
 `tf.keras.losses.sparse_categorical_crossentropy` forward and backprop  | [work-around](#softmax-xent)           |
 `tf.keras.losses.SparseCategoricalCrossentropy` forward and backprop    | [work-around](#softmax-xent)           |
 `tf.image.adjust_contrast` forward                                      | [NO](#adjust-contrast)                 |
 `tf.image.crop_and_resize` backprop                                     | [NO](#crop-and-resize)                 |
 `tf.image.resize` backprop when `method=ResizeMethod.BILINEAR`          | [YES](#resize-bilinear)                |
 `tf.image.resize` backprop when `method=ResizeMethod.NEAREST`           | [NO](#resize-nearest)                  |
 `tf.math.segment_prod` forward                                          | [NO](#segment-reduction)               |
 `tf.math.segment_sum` forward                                           | [unreleased patch](#segment-reduction) |
 `tf.math.unsorted_segment_mean`                                         | [NO](#segment-reduction)               |
 `tf.math.unsorted_segment_prod`                                         | [NO](#segment-reduction)               |
 `tf.math.unsorted_segment_sqrt_n`                                       | [NO](#segment-reduction)               |
 `tf.math.unsorted_segment_sum`                                          | [unreleased patch](#segment-reduction) |
 `tf.nn.bias_add` backprop                                               | [YES](#bias-addition)                  |
 `tf.nn.conv1d` backprop                                                 | [YES](#cudnn-conv)                     |
 `tf.nn.conv2d` backprop                                                 | [YES](#cudnn-conv)                     |
 `tf.nn.conv3d` backprop                                                 | [YES](#cudnn-conv)                     |
 `tf.nn.ctc_loss` backprop                                               | [NO](#ctc-loss)                        |
 `tf.nn.max_pool1d` backprop                                             | [YES](#max-pool)                       |
 `tf.nn.max_pool2d` backprop                                             | [YES](#max-pool)                       |
 `tf.nn.max_pool3d` backprop                                             | [YES](#max-pool)                       |
 `tf.nn.softmax_cross_entropy_with_logits`                               | [work-around](#softmax-xent)           |
 `tf.nn.sparse_softmax_cross_entropy_with_logits`                        | [work-around](#softmax-xent)           |
 `tf.sparse.sparse_dense_matmul` forward                                 | [YES](#sparse-dense-matmul)            |
 XLA reductions on GPU                                                   | [YES](#xla-reductions)                 |

Information for each source is listed below. To reduce repetition, the following
abbreviations have been used throughout:

  * <a name="TF_CUDNN_DETERMINISTIC">**TF_CUDNN_DETERMINISTIC**</a>: Set
    environment variable `TF_CUDNN_DETERMINISTIC` to `'1'` or `'true'`. Also
    *do not* set environment variable `TF_USE_CUDNN_AUTOTUNE` at all (and
    particularly *do not* set it to `'0'` or `'false'`).
  * <a name="TF_DETERMINISTIC_OPS">**TF_DETERMINISTIC_OPS**</a>: Set environment
    variable `TF_DETERMINISTIC_OPS` to `'1'` or `'true'`. Also *do not* set
    environment variable `TF_USE_CUDNN_AUTOTUNE` at all (and particularly
    *do not* set it to `'0'` or `'false'`).
  * <a name="PATCH">**PATCH**</a>: Apply `tfdeterminism.patch`. Note that
    this solution, enabled by [`TF_DETERMINISTIC_OPS`](#TF_DETERMINISTIC_OPS),
    is in stock TensorFlow version 2.1 (see github/tensorflow/tensorflow pull
    request [31465][31465], which makes patching unnecessary.
  * <a name="NO_SOLUTION">**NO SOLUTION**</a>: There is no solution in the
    specified version, but there may be a solution in other versions (as shown).

Where it is indicated that solutions are available in NGC TensorFlow container
images, it can be assumed, unless stated otherwise, that the solutions are
available in both TensorFlow API version 1 and TensorFlow API version 2 variants
of those container images.

If an NGC TF container version is not mentioned in the list of solutions for an
op, any NGC TF container image version that is based on a version of stock
TensorFlow that contains a solution probably also contains the same solution.

---

<a name="auto-tuning"></a>
## Auto-Tuning of cuDNN Convolution Algorithms

### Problem

TensorFlow normally tries different cuDNN convolution algorithms for a given
layer configuration to find the one that runs fastest. The functionality is
inherently nondeterministic because different algorithms can be selected on each
run.

### Solution

  * TF 1.14, 1.15, 2.0: [TF_CUDNN_DETERMINISTIC](#TF_CUDNN_DETERMINISTIC) or
    [PATCH](#PATCH)
  * NGC 19.06+, TF 2.1+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

### Additional Information

From NGC TF 19.12 onwards and stock TensorFlow 2.2 onwards, the
cuDNN forward and backward convolution algorithms are selected
deterministically from several deterministic algorithms. Prior to this (i.e.
NGC 19.11 and earlier, and stock TensorFlow 2.1 and earlier), there is only
one deterministic algorithm selected for each of the forward and two
backward paths. In those versions of TensorFlow, some layer configurations
are not supported (resulting in an exception being thrown with the message
"No algorithm worked!").

---

<a name="dense-image-warp"></a>
## Dense Image Warp

### Problem

The backprop for `tfa.image.dense_image_warp` may introduce truly random noise
because it uses the nondeterministic [`tf.gather`](#gather) functionality.

### Solution

See the solution status for [`tf.gather`](#gather).

---

<a name="fused-batch-norm"></a>
## Fused Batch-Norm

### Problem

`tf.compat.v1.nn.fused_batch_norm` introduces truly random noise in the backrop
to `offset` when `is_training=False`.

Backprop through `tf.compat.v1.nn.fused_batch_norm` when `training=False` is
used for fine-tuning. See github/tensorflow/tensorflow issue [10857][10857] for
more information.

### Solution

There is currently no available solution

---

<a name="convert-to-tensor"></a>
## Convert to Tensor

### Problem

`tf.convert_to_tensor`, when fed with (sparse) `tf.IndexedSlices`, uses the
potentially nondeterministic behavior of
[`tf.math.unsorted_segment_sum`](#segment-reduction) in its forward direction
and therefore may introduce truly random noise into its output when a slice
index is represented more than twice in its input (such as when reducing the
word embedding gradients from multiple instances of the same word in a sentence
or across a batch of sentences).

### Solution

See the solution status for
[`tf.math.unsorted_segment_sum`](#segment-reduction).

---

<a name="gather"></a>
## Gather

### Problem

`tf.gather` is often used to select word embeddings from an embedding matrix in
a model's forward direction and `tf.gather`'s backprop generates sparse
gradients conveyed as `tf.IndexedSlices`. The reduction of the back-propagated
sparse gradients from `tf.gather` by
[`tf.convert_to_tensor`](#convert-to-tensor) can therefore introduce truly
random noise into an embedding trainable variable.

### Solution

See the solution status for
[`tf.convert-to-tensor`](#convert-to-tensor).

A lower-performance work-around for this nondeterminism related to the use of
`tf.gather` is to use `tf.linalg.matmul` instead:

```
# inputs_embeds = tf.gather(embeddings, input_ids)
input_embeds = tf.dtypes.cast(
    tf.one_hot(input_ids, embeddings.shape[0]),
    embeddings.dtype) @ embeddings
```

Note that the backward (and forward) functionality of `tf.gather` itself _is_
deterministic.

---

<a name="cudnn-conv"></a>
## cuDNN Convolution

### Problem

cuDNN convolution backprop algorithms are exposed through `tf.nn.conv1d`,
`tf.nn.conv2d`, and `tf.nn.conv3d`. For the backprop (to both `input` and
`filters`) of these ops to function deterministically, TensorFlow must expose
the relevant deterministic cuDNN convolution algorithms.

Functionality that is built on top of these ops is also affected, such as
`tf.keras.layers.Conv1D`, `tf.keras.layers.Conv2D`, and
`tf.keras.layers.Conv3D`. See also notes on [bias addition](#bias-addition)

### Solution

  * TF 1.14, 1.15, 2.0: [TF_CUDNN_DETERMINISTIC](#TF_CUDNN_DETERMINISTIC) or
    [PATCH](#PATCH)
  * NGC 19.06+, TF 2.1+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

---

<a name="max-pool"></a>
## cuDNN Max-Pooling

### Problem

cuDNN max pooling is exposed through `tf.nn.max_pool1d`, `tf.nn.max_pool2d`, and
`tf.nn.max_pool3d`. For the backprop of these ops to function deterministically,
TensorFlow must expose the relevant deterministic cuDNN convolution algorithms.

Functionality that is built on top of these ops is also affected, such as
`tf.keras.layers.MaxPool1D`, `tf.keras.layers.MaxPool2D`, and
`tf.keras.layers.MaxPool3D`.

### Solution

  * TF 1.14, 1.15, 2.0: [TF_CUDNN_DETERMINISTIC](#TF_CUDNN_DETERMINISTIC) or
    [PATCH](#PATCH)
  * NGC 19.06+, TF 2.1+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

### Additional Information

This solution does not currently have unit tests in the TensorFlow repo but has
been confirmed to work in production models. Here is the
[TODO](https://github.com/tensorflow/tensorflow/blob/6269e15ade2b6b56cd5128afc46d7886da962571/tensorflow/python/kernel_tests/cudnn_deterministic_base.py#L53)
comment to add those tests.

---

<a name="resize-bilinear"></a>
## Bilinear Image Resizing

### Problem

`tf.image.resize` with `method=ResizeMethod.BILINEAR` (TF2 API) introduces truly
random noise into the backprop path. Note that `BILINEAR` is the default
`method` setting. In the TF1 API, this functionality is accessed via
`tf.image.resize_bilinear` (`tf.compat.v1.image.resize_bilinear` in TF 2.x). It
is also exposed through `tf.keras.layers.UpSampling2D` with
`interpolation='bilinear'` (which is not the default `interpolation` setting).

### Solution

  * NGC 20.03+, TF 2.4+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

---

<a name="resize-nearest"></a>
## Nearest-Neighbor Image Resizing

### Problem

`tf.image.resize` with `method=ResizeMethod.NEAREST` (TF2 API) introduces truly
random noise in the backprop path. Note that `BILINEAR` is the default `method`
setting. In the TF1 API, this functionality is accessed via
`tf.image.resize_nearest_neighbor` (`tf.compat.v1.image.resize_nearest_neighbor`
in TF 2.x). It is also exposed through `tf.keras.layers.UpSampling2D` with
`interpolation='nearest'` (which is the default `interpolation` setting).

### Solution

There is currently no solution available. Use bilinear image resizing, if
possible.

A potential work-around is to use `tf.keras.layers.Conv2DTranspose` (see
issues [#12](https://github.com/NVIDIA/framework-determinism/issues/12) and
[#24](https://github.com/NVIDIA/framework-determinism/issues/24) for this
current repository).

---

<a name="softmax-xent"></a>
## Fused Softmax/Cross-Entropy

### Problem

The fused softmax/cross-entropy ops `tf.nn.softmax_cross_entropy_with_logits`
and `tf.nn.sparse_softmax_cross_entropy_with_logits` (accessed via
`tf.keras.losses.categorical_crossentropy`,
`tf.keras.losses.CategoricalCrossentropy`,
`tf.keras.losses.sparse_categorical_crossentropy`, and
`tf.keras.losses.SparseCategoricalCrossentropy`) are known to inject
nondeterminism into both the backward and forward paths. See
github/tensorflow/tensorflow issue [38185][38185].

### Solution

There is currently no solution, although a patch is
[in development](https://github.com/NVIDIA/framework-determinism/pull/21).

A confirmed work-around is to use separate non-fused softmax and cross-entropy
ops. For example, assuming you're using `tf.keras`, select the activation on the
final layer (e.g. a `Dense` layer) to be 'softmax' (which chooses
`tf.nn.softmax`) and then, for the loss function, continue to use
`tf.keras.losses.categorical_crossentropy` (possibly by using its wrapper class
`tf.keras.losses.CategoricalCrossentropy`) or
`tf.keras.losses.sparse_categorical_crossentropy` (possibly by using its wrapper
class `tf.keras.losses.SparseCategoricalCrossentropy`). Since it uses non-fused
kernels, the work-around will be lower performance. Theoretically, you should
ensure that the loss function parameter `from_logits` is set to `False` (the
default), perhaps only for performance reasons since setting it to `True` is a
no-op arithmetically and does not appear to contribute to nondeterminism.

### Additional Information

Stock TensorFlow version 2.6+ will throw a `tf.errors.UnimplementedError` if the
nondeterministic paths of these ops are used with the expectation of determinism
(i.e. with `TF_DETERMINISTIC_OPS` set to `"true"` or `"1"`). See
github/tensorflow/tensorflow pull request [47925][47925].

---

<a name="adjust-contrast"></a>
## Adjust Contrast

### Problem

`tf.image.adjust_contrast` inject truly random noise in the forward direction
when running on a GPU.

### Solution

There is currently no available solution.

---

<a name="crop-and-resize"></a>
## Crop and Resize

### Problem

Backprop to `image` on `tf.image.crop_and_resize` introduces nondeterministic
noise when running on either CPU or GPU. Backprop to `boxes` introduces
nondeterministic noise when running on GPU. See github/tensorflow/tensorflow
issue [42033][42033] for more information.

### Solution

There is currently no available solution.

---

<a name="segment-reduction"></a>
## Segment Reduction

### Problem

The following ops have been shown to introduce truly random noise in the forward
path:

  * `tf.math.segment_sum`
  * `tf.math.unsorted_segment_prod`
  * `tf.math.unsorted_segment_sum` (see github/tensorflow/tensorflow issue
    [39751][39751])

The souce code that implements `tf.math.segment_prod` seems as though it should
introduce truly random noise in the forward path, although we have not be able
to produce it.

The following ops are implemented on top of `tf.math_unsorted_segment_sum` and
therefore also introduce truly random noise in the forward path:

  * `tf.math.unsorted_segment_sqrt_n`
  * `tf.math.unsroted_segment_mean`

### Solution

There is currently no released solution.

We **do** have an unreleased patch for `tf.math.segment_sum` and
`tf.math.unsorted_segment_sum` that can be used by cloning this current
repository, installing the `fwd9m` package, and calling
`fwd9m.tensorflow.enable_determinism`.

github/tensorflow/tensorflow pull request [47974][47974] adds GPU-deterministic
sparse segment reduction ops (probably in TF 2.6). This approach will be used to
provide GPU-deterministic functionality for all the segment reduction ops in
version 2.6 or possibly later.

### Additional Information

Stock TensorFlow version 2.5+ will throw a `tf.errors.UnimplementedError` if the
nondeterministic paths of these ops are used with the expectation of determinism
(i.e. with `TF_DETERMINISTIC_OPS` set to `"true"` or `"1"`). See
github/tensorflow/tensorflow pull request [47772][47772].

At the time of writing (TensorFlow 2.5), `tf.math.segment_mean` is not
implemented on the GPU and the CPU imlementation operates deterministically.

See also:
  * Issue [31](https://github.com/NVIDIA/framework-determinism/issues/31) in
    this current repository.

---

<a name="bias-addition"></a>
## Bias Addition

### Problem

The backprop of `tf.nn.bias_add` performs large, structured reductions using
CUDA `atomicAdd`, thereby capturing the truly random alignment between
asynchronous compute engines into truly randomly varying floating-point rounding
error in the gradients.

Note that various Keras layers, including the Keras convolution layers
(i.e. `tf.keras.layers.Conv1D`, `tf.keras.layers.Conv2D`, and
`tf.keras.layers.Conv3D`), are built on top of `tf.nn.bias_add`. Therefore,
when `use_bias=True` the deterministic functionality of the layer is dependent
on the deterministic functionality of `tf.nn.bias_add`.

### Solution

  * TF 1.14, 1.15, 2.0: [PATCH](#PATCH)
  * NGC 19.06+, TF 2.1+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

### Additional Information

Prior to TensorFlow version 2.2, this deterministic `tf.nn.bias_add` backprop
solution will not work when XLA JIT compilation is enabled due to XLA reductions
on GPU not being deterministic (see
[this comment](https://github.com/tensorflow/tensorflow/pull/34887#discussion_r355610837)
on github/tensorflow/tensorflow pull request 34887). This is resolved in stock
TensorFlow version 2.2 and NGC TF container images based on that version of
TensorFlow; see the [notes on that](#xla-reductions) elsewhere in this current
file.

---

<a name="ctc-loss"></a>
## CTC Loss

### Problem

I had previously assumed that deterministic cuDNN CTC loss was exposed, via
`tf.nn.ctc_loss`, by changes that ended up appearing in stock TensorFlow version
2.3 (see github/tensorflow/tensorflow issue [38151][38151]), but more recent
experiments, the results of which I am in the process of publishing, suggest
that this is not true and that `tf.nn.ctc_loss` has nondeterministic backprop
when operating on either CPU or GPU.

### Solution

There is currently no available solution.

---

<a name="sparse-dense-matmul"></a>
## Sparse-Dense Matmul

### Problem

In TF 2.4 and earlier, the forward path of `tf.sparse.sparse_dense_matmul`
introduces nondeterminism for `tf.float32`, but not for `tf.float64` (for which
there is no GPU implementation). See github/tensorflow/tensorflow issue
[18037][18037].

GPU support for other floating-point types (`tf.float16`, `tf.float64`,
`tf.complex64`, and `tf.complex128`) will be added in TF 2.5
(see github/tensorflow/tensorlow pull request [47419][47419]). In TF 2.5
onwards, if you were relying on the determinism of the `tf.float64` CPU
implementation being automatically selected because of an absense of the
`tf.float64` GPU implementation, you will need to force the op to run on the CPU
or use a different data type.

### Solutions

  * NGC 21.04+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

A deterministic GPU implementation of `tf.sparse.sparse_dense_matmul` when the
data type of the input tensors is `tf.float32`, for both TF1 and TF2 variants of
the NGC TF container image will be available in version `21.04` onwards (based
on stock TF 2.4, which only supported `tf.float64` on GPU).

A deterministic GPU implementation of `tf.sparse.sparse_dense_matmul` when the
data type is `tf.float16`, `tf.float32`, or `tf.complex64` will probably be
available in version 2.6 of stock TensorFlow (see github/tensorflow/tensorflow
pull request [47749][47749]). In this solution, an attempt to use the
`tf.sparse.sparse_dense_matmul` GPU implementation, with data of type tf.float64
or tf.complex128, when deterministic op functionality is enabled (currently via
`TF_DETERMINISTIC_OPS` being set to `"true"` or `"1"`) will cause a
`tf.errors.UnimplementedError` to be thrown.

---

<a name="xla-reductions"></a>
## XLA reductions on GPU

### Problem

Without this solution, when XLA JIT compilation is enabled, any op that relies
on XLA reductions, whether in the forward or backward direction, will introduce
nondeterministic noise.

### Solution

  * TF 2.2+: [TF_DETERMINISTIC_OPS](#TF_DETERMINISTIC_OPS)

---

[10857]: https://github.com/tensorflow/tensorflow/issues/10857
[18037]: https://github.com/tensorflow/tensorflow/issues/18037
[38151]: https://github.com/tensorflow/tensorflow/issues/38151
[38185]: https://github.com/tensorflow/tensorflow/issues/38185
[39751]: https://github.com/tensorflow/tensorflow/issues/39751
[42033]: https://github.com/tensorflow/tensorflow/issues/42033
[47419]: https://github.com/tensorflow/tensorflow/pull/47419
[47749]: https://github.com/tensorflow/tensorflow/pull/47749
[47772]: https://github.com/tensorflow/tensorflow/pull/47772
[47925]: https://github.com/tensorflow/tensorflow/pull/47925
[47974]: https://github.com/tensorflow/tensorflow/pull/47974