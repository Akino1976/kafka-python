import time

import pytest_bdd
from fixtures import *

from steps.givens import *
from steps.thens import *
from steps.whens import *

pytest_bdd.scenarios("features")
