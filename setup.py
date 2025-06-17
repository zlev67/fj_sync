############################################################################
# INTEL CONFIDENTIAL
# Copyright 2022 Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related
# to the source code ("Material") are owned by Intel Corporation or its
# suppliers or licensors. Title to the Material remains with Intel Corp-
# oration or its suppliers and licensors. The Material may contain trade
# secrets and proprietary and confidential information of Intel Corporation
# and its suppliers and licensors, and is protected by worldwide
# copyright and trade secret laws and treaty provisions. No part of the
# Material may be used, copied, reproduced, modified, published, uploaded,
# posted, transmitted, distributed, or disclosed in any way without
# Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellect-
# ual property right is granted to or conferred upon you by disclosure or
# delivery of the Materials, either expressly, by implication, inducement,
# estoppel or otherwise. Any license under such intellectual property
# rights must be express and approved by Intel in writing.
############################################################################

import os.path
import sys

from setuptools import setup, find_packages

if sys.version_info < (3,4):
    sys.exit('Sorry, Python < 3.4 is not supported')

######################
# For extremely simple modules, you can just fill these top variables in
# for more complex items, you'll want to modify the setup directly
toolname = "utec_data"
######################

version_file = os.path.join(
            os.path.dirname(__file__),
            "adat",
            "tools",
            toolname,
            "_version.py")
encoding_kwargs = {'encoding': 'utf-8',}
kwargs = {}
# LOD (REMOVE_ON_RELEASE)
try:
    # Pylod support: Added to release red and white versions
    import svtools.pylod
    kwargs = svtools.pylod.get_additional_setup_args()
    # open this and read it to get the version
except ImportError:
    kwargs = {}
    # open this and read it to get the version
# LOD END

exec(open(version_file, 'rt', **encoding_kwargs).read())
package_name = "adat.tools.utec_data"

# build package_dir first
package_list = find_packages()

setup(name=package_name,
      version=__version__.get_full_version(),
      description='unit_data tool',
      long_description='tool to read and use Utec database',
      author='vamos',
      author_email='adat-namespace@intel.com',
      url='http://goto/adat',
      packages=package_list,
      include_package_data=True,
      install_requires=[
          "adat",
          "adat.common>=0.14.10",
          "adat.data_access>=2.10.0",
          "svtools.intel_version>=2.0.0",
          'mypy',
          "adat.sic>=0.23.2503251000",
      ],
    entry_points = {
    'console_scripts': [],
        },
      **kwargs,
)
