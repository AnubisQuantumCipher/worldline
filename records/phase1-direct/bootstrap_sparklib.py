#!/usr/bin/env python3
"""Build a fresh, private copy of the byte-pinned FSF 16.1.0-1 SPARKlib.

Requires Python 3.10+, GNAT 16.1.0, GPRbuild/GPRls 26.0.0 and ar on PATH.
--sdk-root is the GNATprove SDK prefix containing include/spark and lib/gnat,
not the directory containing several toolchain distributions. --out must not
exist, even as an empty directory or a dangling symlink. --jobs is 1 or 2.

Example (run only when the coordinator admits the build):
    python3 scripts/bootstrap_sparklib.py \
        --sdk-root "$GNATPROVE_SDK_ROOT" \
        --out scratch/coordinator/private-sparklib --jobs 2

Only after exit 0, the caller supplies the private project path and scenarios:
    export GPR_PROJECT_PATH="$PWD/scratch/coordinator/private-sparklib/lib/gnat${GPR_PROJECT_PATH:+:$GPR_PROJECT_PATH}"
    export WORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True
    export SPARKLIB_MODE=full SPARKLIB_BUILD=Production
    export SPARKLIB_LIBRARY_TYPE=static SPARKLIB_INSTALLED=True

This is the source/project and GPR/ALI/archive convention used by
scratch/old-analysis/sparklib_build_experiment.py, made independent of that
scratch tree. No SDK object, ALI, archive, proof session or executable is copied;
no installation command is run. GNATprove remains external in the consumer
project as shipped; separate complete imported-source proof is still required.
The receipt establishes build preparation only, never proof or acceptance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


SCENARIO = (
    "-XSPARKLIB_MODE=full",
    "-XSPARKLIB_BUILD=Production",
    "-XSPARKLIB_LIBRARY_TYPE=static",
    "-XSPARKLIB_INSTALLED=True",
)
BOOTSTRAP_SCENARIO = (*SCENARIO, "-XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=False")
PROJECT_REL = "lib/gnat/sparklib.gpr"
COMMON_REL = "lib/gnat/sparklib_common.gpr"
OBJECT_REL = "lib/gnat/sparklib_obj"
LIBRARY_REL = "lib/gnat/sparklib_lib"
ARCHIVE_REL = LIBRARY_REL + "/libsparklib.a"
ALTERNATIVE_REL = "include/spark/spark__exec.ads"
RECEIPT_REL = "bootstrap-receipt.json"
EVIDENCE_REL = "bootstrap-evidence"

# The installed project and common project used by the passing private recipe.
# These pins, rather than SDK directory names or version banners, identify the
# supported project layout and source release. Mismatches require a new review.
EXPECTED_PROJECT_HASHES = {
    PROJECT_REL: "6b5cf2175948db1894c234b0eca00be567220c0f881bf2de2b9a670e1b9a455f",
    COMMON_REL: "78873f695fa193ef0587051044d2cc3511dc637ec455a249b6696b842a1806ba",
}
ADAPTED_PROJECT_SHA256 = "ffdf9e235830799c45759540dbfff3a24da164bce9272ad9eb63e7be9935569d"
REFERENCE_SOURCE_MANIFEST_SHA256 = "8c1f7cbefcb199a286ff0b7fe748ed12b2e934df338cb185c59d899d70903da1"

# Verbatim source roster/hashes from the passing experiment's source manifest:
# scratch/old-analysis/evidence/private-sparklib-experiment-source-v1.json.
# Include the shipped light alternatives and the pinned body-mode replacement;
# only the root/full active closure may appear in this full-mode compilation.
EXPECTED_SOURCE_HASHES = {
    "include/spark/full/spark-big_integers.ads": "79bfb613772e74569efec2aa2bfd8495a16a64d72cd0b0257a9acc674450ff61",
    "include/spark/full/spark-big_intervals.ads": "590cb312117cb3adbed5818b03defb6f9820ae63e8c568c078b59595e44c10b1",
    "include/spark/full/spark-big_reals.ads": "ee5c25de4d0c209c6af93587eeac58c312fb21601b2ad89f4c8cf6e82cf89682",
    "include/spark/full/spark-containers-formal-holders.adb": "671837cdbcc0f512ea3dc513b8bfa3692b0577bfdce2b99e0b7c9d1b0e4715a7",
    "include/spark/full/spark-containers-formal-holders.ads": "39cdff291ae1613b13093437e198013bf5146a57c2befc8945ac5ae256ea8cc8",
    "include/spark/full/spark-containers-formal-ordered_maps.adb": "e87c2f4c9a3b301e34545c75bb1b1adae9149e81da780f60db644957490b4d19",
    "include/spark/full/spark-containers-formal-ordered_maps.ads": "0054cac103c032a41e5f6b911131db9b1eb61b87946ecd2f0069cea24ffbedf5",
    "include/spark/full/spark-containers-formal-ordered_sets.adb": "8fbb2891d1e595ced49a7313373d89166b10e3c013e129fa1e9a5b7ed4c18f21",
    "include/spark/full/spark-containers-formal-ordered_sets.ads": "20856f73e94f5ba42ac5c1a7173d5bafdf9495266d215a6b0092936f939fcc84",
    "include/spark/full/spark-containers-formal-unbounded_doubly_linked_lists.adb": "b1e950a2c042233e3fd708417d140dbf8a6f8782c92a77b534bb23040bb25bd0",
    "include/spark/full/spark-containers-formal-unbounded_doubly_linked_lists.ads": "79fb2217fec06caeb2abb611dd6f303131355ed7aa044d38eb56160dd1afa4a1",
    "include/spark/full/spark-containers-formal-unbounded_hashed_maps.adb": "812413c65468c16c2f44433c22f7b6ae42959a21ded45f71a8d6dd898280bdb6",
    "include/spark/full/spark-containers-formal-unbounded_hashed_maps.ads": "b8fe60ef990a3baada9ec35caf8180cc80de7e5981060605a42d7899c8081b62",
    "include/spark/full/spark-containers-formal-unbounded_hashed_sets.adb": "035cb06a17ecceb5f3f64249075c6fd27136ecd1b9937cf236379a8608cf5a98",
    "include/spark/full/spark-containers-formal-unbounded_hashed_sets.ads": "730cdae432311d106f8c0f842fcc8b8c89a8397dfe5622497d274cb18b3880dd",
    "include/spark/full/spark-containers-formal-unbounded_ordered_maps.adb": "b3867c1ca50d6ee3bb8b00be06ee90e8a0b554d045e5efc61419a7d2efaf511b",
    "include/spark/full/spark-containers-formal-unbounded_ordered_maps.ads": "739dae352b28bbf41966c75990b137d75cf24f009453fae16dd951d8504a569e",
    "include/spark/full/spark-containers-formal-unbounded_ordered_sets.adb": "b08b53b84e483598eb92b4a18f2cfcbcc3514337f6ad40c8d39195c2817f7cba",
    "include/spark/full/spark-containers-formal-unbounded_ordered_sets.ads": "509792f41a8f96edff35a67c2d05bef35b392f4cf28b3fda5effcd6a5fcf1dfa",
    "include/spark/full/spark-containers-formal-unbounded_vectors.adb": "cecba6254e006e162acf42cd8b9fd747e0da2758be90bb916058fd780dd3dbe8",
    "include/spark/full/spark-containers-formal-unbounded_vectors.ads": "ef7d978c29cb44a4cd0aafab1194a95d38fe3b45d8372622aa47b358d3f86c00",
    "include/spark/full/spark-containers-formal-vectors.adb": "cb4a7c7505bfcd97a04ff80064c2288c74355a31097c324ad19bab95e22e5ee7",
    "include/spark/full/spark-containers-formal-vectors.ads": "e6fd502a4aab41fdfbbc3c09d26efb5c562b658b6c86f1e740a7698a46860d95",
    "include/spark/full/spark-containers-functional-base.ads": "a603b0c174c7d59fae0b80d9597b6f0cbea5696b8c0badb1cb00a400cf47c505",
    "include/spark/full/spark-containers-functional-holder.ads": "7450a9e80006d63908bc37f6ff522702fcdec3a4040efe60cde68a915aa3aa05",
    "include/spark/full/spark-containers-functional-infinite_sequences.ads": "4f5f764e8a11664efc04eff582fa98d8619b9f58773495196ba331416b6f679b",
    "include/spark/full/spark-containers-functional-maps.ads": "069dfead4c9a5a108edf3e66bc6cf4046e67fa06dfe99884d15cfb0a8fd7cbb0",
    "include/spark/full/spark-containers-functional-multisets.ads": "13faa72fb5f94eae82d0d0717bd1b880a0f13000a1f8a3cbab7a4557ff2a7bfd",
    "include/spark/full/spark-containers-functional-sets.ads": "9f5c5be7518dc2be9e94a1851accaeb7beb7d4f14ba720f8b22bd35217816458",
    "include/spark/full/spark-containers-functional-trees.ads": "5a9f7277d5264919217338bb82fbba89e249f708fdc47a3140586dc7421c359b",
    "include/spark/full/spark-containers-functional-vectors.ads": "bd30b2c56b27f6846320203852e1a3c7c03ac7ff0a7ef6d24790760feabe6832",
    "include/spark/full/spark-containers-hash.adb": "8ffb770bf38db9d7222603dbb003e84e28c6bad476c20db079e695cbd028d5e6",
    "include/spark/full/spark-containers-hash.ads": "ea5cc30f3291fca5a6580708cfdd9542e8ec1723ff537b9109a5778d248cb788",
    "include/spark/full/spark-containers-types.ads": "1448a63333a039e34d44d793d85331952926ae08360ec676e7179aafc491a051",
    "include/spark/full/spark.ads": "442ca2550288ad9c79fe16ac7ea4d2ea6437c5b404773cea86f94776b0017b82",
    "include/spark/light/spark-big_integers.adb": "7fdd70ca2241b3c507411f6506e27b7a7b2d7f04943b236e981e2ce95fe25d6d",
    "include/spark/light/spark-big_integers.ads": "fe5eaa1931942522bc904eac6129d046db3338448b64b2a35781f171c7064cf1",
    "include/spark/light/spark-big_intervals.ads": "143356e9763aeba4790eb0a5fc402889dc0d7b18ab459a00607fa7272b053d5b",
    "include/spark/light/spark-big_reals.adb": "14d55e9fce0571250f4397dc40424862e0d72bfae1b7420271912e6732cc3425",
    "include/spark/light/spark-big_reals.ads": "0f8eb95ae7f89a9a7e431bcaa8783a86504e94dccc983fb0e14f0930af79ace8",
    "include/spark/light/spark-containers-functional-base.ads": "5052be7d6f48e83219daead828a524198dc01f58a0ab491b3a52e55d98d30d4b",
    "include/spark/light/spark-containers-functional-holder.ads": "846edc026849c05018777d8d16e2a0e3557202b65488d431da18c6a57acc21b9",
    "include/spark/light/spark-containers-functional-infinite_sequences.ads": "005c23aaa0ab100ede852c161cc25d39f980776068d7c1ce9f6bb04f276bbe42",
    "include/spark/light/spark-containers-functional-maps.ads": "5492ad39ea2d79ab9fde60b48ab98539371a6db0fcaf1daeac2700946bce505e",
    "include/spark/light/spark-containers-functional-multisets.ads": "10b76c36cd7c21c03c8eaaa4a44a66a71128e6a5a86ae9045b097840636f6f73",
    "include/spark/light/spark-containers-functional-sets.ads": "b25b9137a947f8aeea9e71fa2afdb4c6415066103503e4add4cd1ebc0163a68f",
    "include/spark/light/spark-containers-functional-trees.ads": "f68f6eba1a3812590ed66519efb12c4a34c33f4b98bafcdfcef09ea07e2fde6f",
    "include/spark/light/spark-containers-functional-vectors.ads": "ae247966d0027d6b05b692f26b65a24d1d4537471280105777d9474e72fac49b",
    "include/spark/light/spark-containers-types.ads": "e4204fabb72c626b618095aae4d73bcffdb0c4889fc72f2b6d1cfdec6016e57c",
    "include/spark/light/spark.ads": "2a937c38868bf8bef02b779ce1a34b167a0477c9a3df64c44e958a2a2a729520",
    "include/spark/spark-c-constant_strings.adb": "f4510b4bc02b557b5d86b5c6cbe77bcb6f455d918e24ede605eafac2e49e2845",
    "include/spark/spark-c-constant_strings.ads": "bbc66fd45fd09c1d615b407ba4d31fdf32c7621b3920adc71a614003755de870",
    "include/spark/spark-c-strings.adb": "448e00c0e5940d2e56087f4c69f26cf3f28bd00445159c76f25dceb7aebba0ba",
    "include/spark/spark-c-strings.ads": "f83bdaa5136c0f7114ed3e540eab596de58ef2c4e5a8af08a535078a784124b1",
    "include/spark/spark-c.ads": "c227200ccd599e534eda4ac28dc07201656f228fea51fb7c3cab27f7a04fd6b4",
    "include/spark/spark-containers-formal-doubly_linked_lists.adb": "bd19fb7973cc4f7a72a6c9fd556c1d11b36caafba0c29c48ac5c3b7b17b06600",
    "include/spark/spark-containers-formal-doubly_linked_lists.ads": "b5ded162039a00026ff9940592761a9de003ebdc6bff27a2ad6faad3456b8a87",
    "include/spark/spark-containers-formal-hash_tables-generic_keys.adb": "4b662daaae4d934eff0872fa7ab6a9cda795bfed2fdf7ba914a7c0fead87789b",
    "include/spark/spark-containers-formal-hash_tables-generic_keys.ads": "171c45aa3485a6919b502016350be5ba9c5802c5521856f8d74f0c5f782202f5",
    "include/spark/spark-containers-formal-hash_tables-generic_operations.adb": "a125b5e051dbe67c2818c270f292ce02b7016e13cc9daa8622bda3d51ddbb53e",
    "include/spark/spark-containers-formal-hash_tables-generic_operations.ads": "6651bd8882319a89815d7b367679b2f90ae3edd6a4d8d483c6b962c80c43e9bd",
    "include/spark/spark-containers-formal-hash_tables-prime_numbers.adb": "5aa8c31a09c2aab68b0a1b140a638cac369bc2ed357c53386d15ae874f993fa3",
    "include/spark/spark-containers-formal-hash_tables-prime_numbers.ads": "ba7c2a744221b2e8968be4139f8473d8c45d3c964a039cf58fa7264ec3f61bc1",
    "include/spark/spark-containers-formal-hash_tables.ads": "cf03f73b3398567ed5efb4f86f32e49de38e94b0ba1b04d8fc9a05f17cd749b7",
    "include/spark/spark-containers-formal-hashed_maps.adb": "4a665ce1a2d7b3df4af186bbdddda7a85ad744736fa15bc50b1b4fb4615fa06b",
    "include/spark/spark-containers-formal-hashed_maps.ads": "0fd908c11e4f63c12a11d212fb33859abad4f8cf0ec3ecf8c7515403bb85439d",
    "include/spark/spark-containers-formal-hashed_sets.adb": "beebc5fa8d160c81e1907ae6ebe8cf6259dac2dc3b4d7973157fc8829f1b41ba",
    "include/spark/spark-containers-formal-hashed_sets.ads": "9789e4474c33458b7bdf059aa74b421d548e3e66d5c0621b872dd8625dd4012d",
    "include/spark/spark-containers-formal.ads": "b4facb754a6107d5e7fb3e9b878695d228084f3ce3884a3fb3be44c83f3561a7",
    "include/spark/spark-containers-functional-base.adb": "56f4833e25734dee9d1c6d29583ac45e03fa3dc06dc61fd64e7c4cf1fcb63d71",
    "include/spark/spark-containers-functional-holder.adb": "3a4465ae59fbd737d8f17654bc1c90c1d834abb978938e37a2201c8064e68922",
    "include/spark/spark-containers-functional-infinite_sequences-higher_order.adb": "c74db5ef3013cdb51155a7682162509aa68e4364cb1883696b244dc4efb24d3a",
    "include/spark/spark-containers-functional-infinite_sequences-higher_order.ads": "c8b75fe0aaa9df66a8db67cf28aeaf68a74b2a6671af37427cfdc2670fe67b4e",
    "include/spark/spark-containers-functional-infinite_sequences.adb": "7aeb0e9a15413f299272f3996e4b8f34e4573842c67afe897c0d520db5b53145",
    "include/spark/spark-containers-functional-maps-higher_order.adb": "00c9ed29f092d48f827478ceedac1681fd076aaf575b65734021b81599484a6b",
    "include/spark/spark-containers-functional-maps-higher_order.ads": "55b2b335ec348ca121d458aa0544a601ca9de4f028ab30d8bfbbc592ed196d04",
    "include/spark/spark-containers-functional-maps.adb": "65e5b4dcfb30c218fd167f96b47d34ac46c431a29fdf4955b2cc980d878f4d50",
    "include/spark/spark-containers-functional-multisets.adb": "81cde8f0a134f19730c566c681a8a20b6473ec881b9343d293094fe732eb2bce",
    "include/spark/spark-containers-functional-sets-higher_order.adb": "fa10cb42e9045c7a3834e2afc56dbc50a17825bbbd0e6ffd543bb6cf5b5a5bd6",
    "include/spark/spark-containers-functional-sets-higher_order.ads": "abd2eb19e827e23f7b2735ce8a953c8944ad2ac8f4b584f5a1eb40e2d71218bb",
    "include/spark/spark-containers-functional-sets.adb": "deeb8ad80a2cf36fa342439458b330a4a2eb894cb68054b0df1521d501c0657b",
    "include/spark/spark-containers-functional-trees.adb": "ac66f994d4b12cade21096cb7baa7a31dc72ac7305a3ad48b0c387805c10a5d5",
    "include/spark/spark-containers-functional-vectors-higher_order.adb": "7b63bf18840e30ed4be35cd0dc3fcbec93a8c7122ed0ab9cb57b46ff64a03fb2",
    "include/spark/spark-containers-functional-vectors-higher_order.ads": "a7cdf085b2086b7a26e8154061739bc352bb53e976d86e14bd3985c495702a00",
    "include/spark/spark-containers-functional-vectors.adb": "4e282d116035b4552fa1ff8383107a339a55c17dff1d58796bd04f0963226439",
    "include/spark/spark-containers-functional.ads": "8668c3f70fc753e5aac8c47fcd7b21bf72826d000dbde1bc997d3bf356b023c6",
    "include/spark/spark-containers-parameter_checks.adb": "de86c8ab417675daa64f511cbb0e73110d483af82d2d6a011842bf39dfd76489",
    "include/spark/spark-containers-parameter_checks.ads": "a0baa9bcbe6594b0f75bda8509ad8d063b7b10f1bf93dc7eb8e3ebe468370da1",
    "include/spark/spark-containers-stable_sorting.adb": "09eb1346d64f0311c21ebb9963ffb2932b904b71d83d08e00fb759357ce7e7f5",
    "include/spark/spark-containers-stable_sorting.ads": "f1d584697df66dfc20172b80ff3161e2a54e7dc6e7b2efa3462aba20b3b186c8",
    "include/spark/spark-containers.ads": "93f4d0b97fa2853048f83fe72ed3e744aeb58d8e9ccac82a03f7864125d272b9",
    "include/spark/spark-conversions-float_conversions.ads": "28e2d3b76603df4ade553c4ca5f393970c2f8a5e7d539e5996ec8ef5ce2555d1",
    "include/spark/spark-conversions-long_float_conversions.ads": "dc9272eb69f06ee292c66c2afb3bea810b9c1b56ea045cdb4e2d890fea05c504",
    "include/spark/spark-conversions-long_integer_conversions.ads": "96d5f0582f9e3f6c725a12babef7d7d0a8c71c980adbce9ea1f2c00371bff2eb",
    "include/spark/spark-conversions.ads": "8521470696e3c66286cbf80ed3321a743a13f2a48999c2ab8f0104f0d9def02d",
    "include/spark/spark-cut_operations.adb": "671db2897227b631102c0cdbf643a780252cf0e9cc605266fe860cc4d1d81535",
    "include/spark/spark-cut_operations.ads": "1214a442f339a3995ac2df71e79477caea9b1185bababa2756c639fa19c8ee61",
    "include/spark/spark-higher_order-fold.adb": "291dcecfd9123ca16949441dbfcdc387ccc4ec559e8c70d616996e3b71fe2f80",
    "include/spark/spark-higher_order-fold.ads": "3e2cf177a59b29b6d84b3d1992b9bb3c0698593fcd11f3f71db85848dd78f8a5",
    "include/spark/spark-higher_order.adb": "036a25e0a43a6515b4cbd7bdc2d009c62393823ab712038102ff4492a539ef42",
    "include/spark/spark-higher_order.ads": "08acbc065cd25ba4b23b04021621a128293a4740f6e3fc0873c0a3d7b9e32a9f",
    "include/spark/spark-lemmas-arithmetic.adb": "a26fc4380a0224829c84a841d60cdab6be9cac063f57ef7c012fe5a0a89523e4",
    "include/spark/spark-lemmas-arithmetic.ads": "2eb6e3ca1ef03ebfcc4ab3e8a1937e97202a9afdb2edd6cda5618579d0adefa7",
    "include/spark/spark-lemmas-constrained_array.adb": "255dcf028ee3025a8a1f32f51be01fcc85631ede0cd28d7965527df8d6ebe852",
    "include/spark/spark-lemmas-constrained_array.ads": "4e0cf2c0b29f70858612496b4eb0c86fb0ed8856ca83791609bc8fd2c710c985",
    "include/spark/spark-lemmas-fixed_point_arithmetic.adb": "522ca5c6964a8eef816d1399816f82215a5e11c48992447ac81b8ec3af9156f0",
    "include/spark/spark-lemmas-fixed_point_arithmetic.ads": "361f325ae07cf042e781747660b7838f31ef760e3f8fdc9cb9ae681518b0a45d",
    "include/spark/spark-lemmas-float_arithmetic.ads": "ff6e6dcf17742827bf9f3334768089ceb58cc5cc3d4cd0ae29364fd3d4cb0b5d",
    "include/spark/spark-lemmas-floating_point_arithmetic.adb": "d22954b8b23a33f4d8d51882cd091c7a7045829fe0faeb5e35eca23f06b7c3f8",
    "include/spark/spark-lemmas-floating_point_arithmetic.ads": "fd63d65392fbb520036c8bbd2bba7e524673f3c563723621bc9b1435ad3584f2",
    "include/spark/spark-lemmas-integer_arithmetic.ads": "3f5ae070443170b3a02977a12a8049025637c550fdaaeff9d435b8d0f872bcfa",
    "include/spark/spark-lemmas-long_float_arithmetic.ads": "1e034d221cc764042d88d795536d57cc0eb23ca7a4c79bf98e8f2f2cdcc7ee1a",
    "include/spark/spark-lemmas-long_integer_arithmetic.ads": "3b804875284f4fe381eb947125dc07e1fd81e18a5ee421196e21c4b83e8d54be",
    "include/spark/spark-lemmas-mod32_arithmetic.ads": "d3b9f348535ce4103cc8897b7e4a2f835520d5db26900269a265df3063cb1d25",
    "include/spark/spark-lemmas-mod64_arithmetic.ads": "74bff45ca5043b94fa696ff8a06eab95da90fd0d09e0b8875032d1ab86bcb3f9",
    "include/spark/spark-lemmas-mod_arithmetic.adb": "06ded9fe9d3bb96a50240a238be654f36003f9df523ce47d904a23e79d9a011f",
    "include/spark/spark-lemmas-mod_arithmetic.ads": "8e79a79853aede5569178241a14debc8019a2d5d968cdd76b28c1e923887b625",
    "include/spark/spark-lemmas-unconstrained_array.adb": "243246a7cfb1205908a311648d503213668e06300feb7da6938bd6174d291ee0",
    "include/spark/spark-lemmas-unconstrained_array.ads": "3ae4947f8cf51621768719e5e04b2c77d65d7e9abc010f6e132bb02ba88bca01",
    "include/spark/spark-lemmas.ads": "19de721862fa8af03dab5e33877bb5eb26d2c6af739656956e66e3899540ce08",
    "include/spark/spark-pointers-abstract_maps.ads": "0303720c9275ba0c3387cfde230f74bdd974b6c686525a703541d052e847d8eb",
    "include/spark/spark-pointers-abstract_sets.adb": "8d3118ab0888e1f737750ffad54d553246abdce88597b47010401c30c3632e0f",
    "include/spark/spark-pointers-abstract_sets.ads": "53fcd80c5708f7e03e88442de1c39133ab7e5145347619650e79e8a1e3aa9a51",
    "include/spark/spark-pointers-pointers_with_aliasing.adb": "4f04b754e5213433a6a6df2f9214a6359121ec73ab18bc3a5d08d82aa088d69a",
    "include/spark/spark-pointers-pointers_with_aliasing.ads": "e5b0ca2277755e7678c9b46bde92aa9407ca09347f573cb7ca5ef94ce9bb8948",
    "include/spark/spark-pointers-pointers_with_aliasing_separate_memory.adb": "1248599e9f2a39b55619d052c893f1095a69fb172464405824ffc8963b76ed8c",
    "include/spark/spark-pointers-pointers_with_aliasing_separate_memory.ads": "440d47abaf472b863ef98baa276385bf00874a448a8ab2d3ae26210c21bb4347",
    "include/spark/spark-pointers.ads": "b373df9db05626108a2469be01d51018593eee35a664c9b39bdb3bc2e4d90ea0",
    "include/spark/spark-tests-array_lemmas.adb": "81aacb0bd194a4035dfc70aa50a84d15c1c3375acbcf3e5abf2a3895e22c5a07",
    "include/spark/spark-tests-array_lemmas.ads": "def5e7b0e5531c798ead053f868914123a9e992efd8cb1436d95e5935fc5ceb0",
    "include/spark/spark-tests.ads": "0fe890abad1d39293168d397d1134842da573cd4558df7c7a2a0d9e58eb46a32",
    "include/spark/spark__exec.ads": "63ad0b8c94c229a16813cf8583b3e9872606456a1e1c4d7cda99c7d831a1a286",
}

ORIGINAL_TOOL_BLOCK = '''   GPR_Tool := external ("GPR_TOOL", "");
   case GPR_Tool is
      when "gnatprove" =>
         for Externally_Built use "True";
      when others =>
         null;
   end case;
'''
# Exact passing adaptation, including its historical experiment comments. No
# proof switch or Ada source byte is changed; real GPR_TOOL is never spoofed.
PRIVATE_TOOL_BLOCK = '''   --  Experiment only: the standalone phase builds the complete private library.
   --  The unchanged WORLDLINE aggregate then consumes that exact artifact.
   type Private_Prebuilt_Kind is ("True", "False");
   Private_Prebuilt : Private_Prebuilt_Kind :=
     external ("WORLDLINE_PRIVATE_SPARKLIB_PREBUILT", "False");

   GPR_Tool := external ("GPR_TOOL", "");
   case GPR_Tool is
      when "gnatprove" =>
         for Externally_Built use "True";
      when others =>
         for Externally_Built use Private_Prebuilt;
   end case;
'''


class BootstrapError(RuntimeError):
    pass


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_file(root: Path, relative: str) -> Path:
    path = root
    for part in Path(relative).parts:
        path /= part
        if path.is_symlink():
            raise BootstrapError("Symlink in required private/SDK path: " + str(path))
    if not path.is_file() or path.stat().st_size == 0:
        raise BootstrapError("Missing, empty or nonregular required file: " + str(path))
    if not path.resolve().is_relative_to(root):
        raise BootstrapError("Required file escapes its root: " + str(path))
    return path


def source_hashes(root: Path) -> dict[str, str]:
    source_root = root / "include/spark"
    for directory in (root / "include", source_root, source_root / "full", source_root / "light"):
        if directory.is_symlink() or not directory.is_dir():
            raise BootstrapError("Unsupported source directory layout: " + str(directory))
    result = {}
    for path in sorted(source_root.rglob("*")):
        if path.is_symlink():
            raise BootstrapError("Symlink in source tree: " + str(path))
        if path.is_dir():
            if path not in (source_root / "full", source_root / "light"):
                raise BootstrapError("Unexpected source directory: " + str(path))
            continue
        if not path.is_file() or path.suffix not in (".ads", ".adb"):
            raise BootstrapError("Unexpected non-Ada source-tree entry: " + str(path))
        result[path.relative_to(root).as_posix()] = digest(path)
    return result


def project_hashes(root: Path) -> dict[str, str]:
    return {rel: digest(require_file(root, rel)) for rel in EXPECTED_PROJECT_HASHES}


def require_hashes(actual: dict[str, str], expected: dict[str, str], label: str) -> None:
    if actual != expected:
        details = {
            "missing": sorted(expected.keys() - actual.keys()),
            "unexpected": sorted(actual.keys() - expected.keys()),
            "changed": {rel: {"expected": expected[rel], "actual": actual[rel]}
                        for rel in sorted(actual.keys() & expected.keys())
                        if actual[rel] != expected[rel]},
        }
        raise BootstrapError(label + " mismatch: " + json.dumps(details, sort_keys=True))


def persist(out: Path, receipt: dict) -> None:
    temporary = out / (RECEIPT_REL + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(out / RECEIPT_REL)


def run_command(out: Path, env: dict[str, str], receipt: dict, label: str,
                argv: list[str], *, member_bytes: bool = False) -> dict:
    """Retain every command result; archive payloads are hashed, not copied."""
    number = len(receipt["commands"]) + 1
    prefix = f"{EVIDENCE_REL}/{number:03d}-{label}"
    stdout_path = out / (prefix + ".stdout")
    stderr_path = out / (prefix + ".stderr")
    record = {"label": label, "argv": argv, "cwd": str(out), "started_utc": utc(),
              "exit_code": None, "stderr_file": prefix + ".stderr"}
    if not member_bytes:
        record["stdout_file"] = prefix + ".stdout"
    receipt["commands"].append(record)
    persist(out, receipt)
    try:
        with stderr_path.open("xb") as stderr:
            if member_bytes:
                completed = subprocess.run(argv, cwd=out, env=env, stdout=subprocess.PIPE, stderr=stderr)
                record["stdout_sha256"] = hashlib.sha256(completed.stdout).hexdigest()
                record["stdout_bytes"] = len(completed.stdout)
            else:
                with stdout_path.open("xb") as stdout:
                    completed = subprocess.run(argv, cwd=out, env=env, stdout=stdout, stderr=stderr)
        record["exit_code"] = completed.returncode
    except BaseException as exc:
        record["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        record["completed_utc"] = utc()
        for channel, path in (("stdout", stdout_path), ("stderr", stderr_path)):
            if path.is_file():
                record[channel + "_sha256"] = digest(path)
                record[channel + "_bytes"] = path.stat().st_size
        persist(out, receipt)
    if record["exit_code"] != 0:
        raise BootstrapError(f"Command failed ({record['exit_code']}): {label}; see {prefix}.stderr")
    return record


def command_text(out: Path, record: dict, channel: str = "stdout") -> str:
    return (out / record[channel + "_file"]).read_text(encoding="utf-8")


def materialize(sdk: Path, out: Path, receipt: dict) -> None:
    inputs = receipt["inputs"]
    inputs["installed_source_hashes"] = source_hashes(sdk)
    inputs["installed_project_hashes"] = project_hashes(sdk)
    require_hashes(inputs["installed_source_hashes"], EXPECTED_SOURCE_HASHES, "SDK source identity/layout")
    require_hashes(inputs["installed_project_hashes"], EXPECTED_PROJECT_HASHES, "SDK project identity/version")
    copied = receipt["materialization"]
    copied["copied_source_hashes"] = {}
    for rel, expected in EXPECTED_SOURCE_HASHES.items():
        data = require_file(sdk, rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise BootstrapError("SDK source changed during copy: " + rel)
        destination = out / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
        copied["copied_source_hashes"][rel] = digest(destination)
    for rel, expected in EXPECTED_PROJECT_HASHES.items():
        data = require_file(sdk, rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise BootstrapError("SDK project changed during copy: " + rel)
        if rel == PROJECT_REL:
            original = data.decode("utf-8")
            if original.count(ORIGINAL_TOOL_BLOCK) != 1:
                raise BootstrapError("Installed GPR_TOOL block is not the reviewed block")
            adapted = original.replace(ORIGINAL_TOOL_BLOCK, PRIVATE_TOOL_BLOCK, 1)
            data = adapted.encode("utf-8")
            if hashlib.sha256(data).hexdigest() != ADAPTED_PROJECT_SHA256:
                raise BootstrapError("Project adaptation is not byte-identical to the passing recipe")
            copied["project_adaptation"] = {
                "path": rel, "installed_sha256": expected,
                "private_sha256": ADAPTED_PROJECT_SHA256,
                "old_block": ORIGINAL_TOOL_BLOCK, "new_block": PRIVATE_TOOL_BLOCK,
                "unified_diff": "".join(difflib.unified_diff(
                    original.splitlines(keepends=True), adapted.splitlines(keepends=True),
                    fromfile="SDK/" + rel, tofile="private/" + rel)),
                "gnatprove_consumer_external_unchanged": True,
                "normal_gpr_bootstrap_prebuilt": "False",
                "normal_gpr_consumer_prebuilt_supplied_by_caller": "True",
            }
        destination = out / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
    copied["private_source_hashes"] = source_hashes(out)
    copied["private_project_hashes"] = project_hashes(out)
    require_hashes(copied["private_source_hashes"], EXPECTED_SOURCE_HASHES, "Copied source bytes")
    require_hashes(copied["private_project_hashes"],
                   {**EXPECTED_PROJECT_HASHES, PROJECT_REL: ADAPTED_PROJECT_SHA256}, "Private project bytes")
    # Only the two project files and byte-identical Ada sources were materialized.
    # In particular, SDK build directories and shipped proof sessions are unread.
    copied["copied_sdk_build_or_proof_artifacts"] = []


def identify_tools(out: Path, env: dict[str, str], receipt: dict) -> dict[str, str]:
    tools = {}
    expected_versions = {"gnat": r"^GNAT 16\.1\.0(?:\s|$)",
                         "gprbuild": r"^GPRBUILD 26\.0\.0(?:\s|$)",
                         "gprls": r"\b26\.0\.0\b"}
    receipt["tools"] = {}
    for name in ("gnat", "gprbuild", "gprls", "ar"):
        found = shutil.which(name, path=env.get("PATH"))
        if found is None:
            raise BootstrapError("Required executable not on PATH: " + name)
        executable = Path(found).resolve(strict=True)
        tools[name] = str(executable)
        identity = {"executable": str(executable), "executable_sha256": digest(executable)}
        receipt["tools"][name] = identity
        result = run_command(out, env, receipt, name + "-version", [str(executable), "--version"])
        identity["version"] = {"command_index": len(receipt["commands"]),
                               "argv": result["argv"], "exit_code": result["exit_code"],
                               "stdout": command_text(out, result),
                               "stderr": command_text(out, result, "stderr")}
        if name in expected_versions and re.search(expected_versions[name],
                                                    identity["version"]["stdout"], re.MULTILINE) is None:
            raise BootstrapError("Unsupported " + name + " version; expected GNAT 16.1.0 / GPR 26.0.0")
    return tools


def selected_paths(out: Path, record: dict, kind: str) -> list[Path]:
    paths = [Path(line.strip()) for line in command_text(out, record).splitlines() if line.strip()]
    if not paths or len(paths) != len(set(paths)):
        raise BootstrapError("Empty or duplicate GPR-selected " + kind + " roster")
    for path in paths:
        if not path.is_absolute() or not path.is_relative_to(out):
            raise BootstrapError("GPR selected out-of-private " + kind + ": " + str(path))
        require_file(out, path.relative_to(out).as_posix())
    return paths


def artifact_hashes(out: Path) -> dict[str, str]:
    paths = [out / ARCHIVE_REL]
    for directory in (out / OBJECT_REL, out / LIBRARY_REL):
        for pattern in ("*.o", "*.ali"):
            paths.extend(directory.glob(pattern))
    return {path.relative_to(out).as_posix(): digest(require_file(out, path.relative_to(out).as_posix()))
            for path in sorted(set(paths)) if path.exists()}


def verify_dependency(out: Path, env: dict[str, str], receipt: dict, tools: dict[str, str]) -> None:
    """Actual GPR compilation roster + ALI U coverage, never one object per spec."""
    verification = receipt["artifact_completeness"]
    selected = {}
    for kind, flag in (("sources", "-s"), ("objects", "-o")):
        record = run_command(out, env, receipt, "gprls-" + kind,
                             [tools["gprls"], "-P" + str(out / PROJECT_REL), "-U", flag,
                              *BOOTSTRAP_SCENARIO])
        selected[kind] = selected_paths(out, record, kind)
        verification["gpr_selected_" + kind] = [p.relative_to(out).as_posix() for p in selected[kind]]
    active = {rel: sha for rel, sha in EXPECTED_SOURCE_HASHES.items()
              if rel != ALTERNATIVE_REL and Path(rel).parent in
              (Path("include/spark"), Path("include/spark/full"))}
    active_by_name = {Path(rel).name: rel for rel in active}
    if len(active_by_name) != len(active):
        raise BootstrapError("Ambiguous active source basenames")
    if any(p.relative_to(out).as_posix() not in active for p in selected["sources"]):
        raise BootstrapError("GPR selected a light, alternate or unknown source in full mode")
    if out / "include/spark/full/spark.ads" not in selected["sources"]:
        raise BootstrapError("GPR did not select the real full-mode SPARK spec")
    expected_objects = {out / OBJECT_REL / p.with_suffix(".o").name for p in selected["sources"]}
    if len(expected_objects) != len(selected["sources"]) or expected_objects != set(selected["objects"]):
        raise BootstrapError("Complete GPR source-to-object roster mismatch")
    # Require the binder-facing ALI copies as well as the compiler's object/ALI
    # pairs. A nonempty archive alone cannot repair missing spark.ali in CI.
    expected_ali_names = {p.with_suffix(".ali").name for p in selected["objects"]}
    for directory in (out / OBJECT_REL, out / LIBRARY_REL):
        actual_alis = {p.name for p in directory.glob("*.ali")}
        if actual_alis != expected_ali_names:
            raise BootstrapError("Incomplete or unexpected ALI roster in " + str(directory))
    if {p.name for p in (out / OBJECT_REL).glob("*.o")} != {p.name for p in expected_objects}:
        raise BootstrapError("Unselected object in private object directory")
    if list((out / LIBRARY_REL).glob("*.o")):
        raise BootstrapError("Unexpected loose object in private library directory")
    represented = set()
    mapping = []
    verification["mapping"] = mapping
    for obj in selected["objects"]:
        ali = require_file(out, obj.with_suffix(".ali").relative_to(out).as_posix())
        library_ali = require_file(out, LIBRARY_REL + "/" + ali.name)
        lines = ali.read_text(encoding="utf-8").splitlines()
        units = [line.split() for line in lines if line.startswith("U ")]
        if not units or any(len(unit) < 4 for unit in units) or "A -fPIC" not in lines:
            raise BootstrapError("ALI unit/PIC compilation identity absent: " + str(ali))
        if not lines or lines[0] != 'V "GNAT Lib v16"':
            raise BootstrapError("ALI compiler format/version differs: " + str(ali))
        unit_names = {unit[2] for unit in units}
        expected_unit_names = {name for name in active_by_name if Path(name).stem == obj.stem}
        unit_ids = [unit[1] for unit in units]
        unit_name = obj.stem.replace("-", ".")
        declared_ids = {unit_name + ("%s" if name.endswith(".ads") else "%b")
                        for name in expected_unit_names}
        # An instantiated generic body and spec can both originate in one .ads.
        if (unit_names != expected_unit_names or len(set(unit_ids)) != len(units)
            or not declared_ids <= set(unit_ids)
            or any(name not in {unit_name + "%s", unit_name + "%b"} for name in unit_ids)):
            raise BootstrapError("ALI U records do not cover the selected unit's spec/body: " + str(ali))
        ali_sha = digest(ali)
        if digest(library_ali) != ali_sha:
            raise BootstrapError("Binder-facing ALI differs from compiled ALI: " + str(library_ali))
        represented.update(unit_names)
        mapping.append({"object": obj.relative_to(out).as_posix(), "object_sha256": digest(obj),
                        "ali": ali.relative_to(out).as_posix(), "ali_sha256": ali_sha,
                        "library_ali": library_ali.relative_to(out).as_posix(),
                        "library_ali_sha256": ali_sha, "source_units": units,
                        "represented_source_hashes": {active_by_name[name]: active[active_by_name[name]]
                                                      for name in sorted(unit_names)}})
    if represented != set(active_by_name):
        raise BootstrapError("ALI source closure mismatch: missing=" + repr(sorted(set(active_by_name) - represented))
                             + " unexpected=" + repr(sorted(represented - set(active_by_name))))
    verification["active_source_hashes"] = active
    verification["nonselected_sources"] = {
        rel: {"sha256": sha, "reason": "shipped light-mode source" if "/light/" in rel else
              "shipped body-mode replacement; real full/spark.ads selected"}
        for rel, sha in EXPECTED_SOURCE_HASHES.items() if rel not in active}
    archive = require_file(out, ARCHIVE_REL)
    with archive.open("rb") as stream:
        if stream.read(8) != b"!<arch>\n":
            raise BootstrapError("Private library is not a self-contained regular ar archive")
    listing = run_command(out, env, receipt, "archive-members", [tools["ar"], "t", str(archive)])
    members = command_text(out, listing).splitlines()
    verification["archive_members"] = members
    if Counter(members) != Counter(obj.name for obj in selected["objects"]):
        raise BootstrapError("Archive membership differs from complete GPR object roster")
    verification["archive_member_hashes"] = {}
    for obj in selected["objects"]:
        result = run_command(out, env, receipt, "archive-member-" + obj.stem,
                             [tools["ar"], "p", str(archive), obj.name], member_bytes=True)
        if result["stdout_sha256"] != digest(obj) or result["stdout_bytes"] != obj.stat().st_size:
            raise BootstrapError("Archived member differs from compiled object: " + obj.name)
        verification["archive_member_hashes"][obj.name] = result["stdout_sha256"]
    verification["archive_sha256"] = digest(archive)
    verification["dependency_artifacts"] = artifact_hashes(out)
    verification["status"] = "complete GPR/ALI/source/archive correspondence established"


def bootstrap(sdk: Path, out: Path, jobs: int, receipt: dict) -> None:
    receipt["stage"] = "materializing pinned SDK Ada/project sources"
    materialize(sdk, out, receipt)
    persist(out, receipt)
    for name in (EVIDENCE_REL, "tmp", "cache"):
        (out / name).mkdir(exist_ok=False)
    env = dict(os.environ)
    # The real tool owns GPR_TOOL. Do not fake gnatprove or inherit a spoofed
    # value. Resolve this standalone project only against its private copy.
    env.pop("GPR_TOOL", None)
    env["GPR_PROJECT_PATH"] = str(out / "lib/gnat")
    env["WORLDLINE_PRIVATE_SPARKLIB_PREBUILT"] = "False"
    env["TMPDIR"] = str(out / "tmp")
    env["TMP"] = env["TEMP"] = env["TMPDIR"]
    env["XDG_CACHE_HOME"] = str(out / "cache")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    receipt["command_environment"] = {name: env.get(name) for name in
                                      ("PATH", "GPR_PROJECT_PATH", "GPR_TOOL",
                                       "WORLDLINE_PRIVATE_SPARKLIB_PREBUILT", "TMPDIR", "TMP", "TEMP",
                                       "XDG_CACHE_HOME", "PYTHONDONTWRITEBYTECODE")}
    receipt["stage"] = "identifying tools"
    tools = identify_tools(out, env, receipt)
    receipt["stage"] = "building full/Production/static/installed private SPARKlib"
    run_command(out, env, receipt, "gprbuild",
                [tools["gprbuild"], "-p", "-P", str(out / PROJECT_REL), f"-j{jobs}",
                 *BOOTSTRAP_SCENARIO, "-cargs:Ada", "-fPIC"])
    receipt["stage"] = "checking complete GPR/ALI/source/archive correspondence"
    verify_dependency(out, env, receipt, tools)
    receipt["stage"] = "checking unchanged SDK and materialized source/project bytes"
    final = receipt["final_input_hashes"] = {
        "installed_source_hashes": source_hashes(sdk), "installed_project_hashes": project_hashes(sdk),
        "private_source_hashes": source_hashes(out), "private_project_hashes": project_hashes(out)}
    require_hashes(final["installed_source_hashes"], EXPECTED_SOURCE_HASHES, "Installed sources after build")
    require_hashes(final["installed_project_hashes"], EXPECTED_PROJECT_HASHES, "Installed projects after build")
    require_hashes(final["private_source_hashes"], EXPECTED_SOURCE_HASHES, "Private sources after build")
    require_hashes(final["private_project_hashes"],
                   {**EXPECTED_PROJECT_HASHES, PROJECT_REL: ADAPTED_PROJECT_SHA256}, "Private projects after build")
    # No caller environment is changed. These are instructions, not evidence
    # that a consumer build or any imported-source proof has run.
    receipt["consumer_environment_after_success"] = {
        "prepend_GPR_PROJECT_PATH": str(out / "lib/gnat"),
        "WORLDLINE_PRIVATE_SPARKLIB_PREBUILT": "True", "SPARKLIB_MODE": "full",
        "SPARKLIB_BUILD": "Production", "SPARKLIB_LIBRARY_TYPE": "static", "SPARKLIB_INSTALLED": "True"}
    receipt["stage"] = "complete"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sdk-root", required=True, type=Path,
                        help="GNATprove FSF 16.1.0-1 SDK prefix (include/spark and lib/gnat)")
    parser.add_argument("--out", required=True, type=Path, help="new private prefix; must not already exist")
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=2, help="bounded build parallelism (default: 2)")
    args = parser.parse_args()
    receipt = {"schema": "worldline-private-sparklib-bootstrap-v1", "started_utc": utc(),
               "status": "INCOMPLETE", "exit_code": None, "stage": "preparing new destination",
               "scope": "build preparation only; never proof, acceptance or independent F7",
               "separate_complete_imported_source_proof_required": True,
               "sdk_source_release": "FSF GNATprove 16.1.0-1 (identified by exact source/project byte pins)",
               "reference_source_manifest_sha256": REFERENCE_SOURCE_MANIFEST_SHA256,
               "reference_adapted_project_sha256": ADAPTED_PROJECT_SHA256,
               "argv": [sys.executable, *sys.argv], "python_version": sys.version,
               "bootstrap_script_sha256": digest(Path(__file__).resolve()),
               "jobs": args.jobs, "bootstrap_scenario": list(BOOTSTRAP_SCENARIO),
               "inputs": {}, "materialization": {}, "commands": [], "artifact_completeness": {}}
    out = None
    created = False
    exit_code = 1
    try:
        sdk = args.sdk_root.expanduser().resolve()
        requested_out = Path(os.path.abspath(args.out.expanduser()))
        receipt["sdk_root"] = str(sdk)
        receipt["requested_out"] = str(requested_out)
        # Do not resolve the leaf before checking: a dangling symlink must also
        # be refused, not followed to create a different destination.
        if os.path.lexists(requested_out):
            raise BootstrapError("Destination already exists; no artifacts were changed: " + str(requested_out))
        out = requested_out.parent.resolve() / requested_out.name
        receipt["out"] = str(out)
        if out.is_relative_to(sdk) or sdk.is_relative_to(out):
            raise BootstrapError("SDK and private output roots must be disjoint")
        out.mkdir(parents=True, exist_ok=False)
        created = True
        persist(out, receipt)
        if not sdk.is_dir():
            raise BootstrapError("SDK root is not an existing directory: " + str(sdk))
        bootstrap(sdk, out, args.jobs, receipt)
        receipt["status"] = "BUILT complete private SPARKlib; NOT PROOF"
        exit_code = 0
    except (Exception, KeyboardInterrupt) as exc:
        exit_code = 130 if isinstance(exc, KeyboardInterrupt) else 1
        receipt["status"] = "ERROR; private dependency must not be consumed"
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
    receipt["exit_code"] = exit_code
    receipt["completed_utc"] = utc()
    if created and out is not None:
        try:
            persist(out, receipt)
        except OSError as exc:
            receipt["status"] = "ERROR; final receipt could not be written"
            receipt["receipt_error"] = type(exc).__name__ + ": " + str(exc)
            receipt["exit_code"] = exit_code = 1
    if exit_code:
        # For a preexisting/unwritable destination, the error receipt goes only
        # to stderr: never overwrite existing evidence to report a refusal.
        print(json.dumps(receipt, indent=2, sort_keys=True), file=sys.stderr)
    else:
        print(json.dumps({"status": receipt["status"], "out": str(out),
                          "receipt": str(out / RECEIPT_REL),
                          "consumer_environment_after_success": receipt["consumer_environment_after_success"]},
                         sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
