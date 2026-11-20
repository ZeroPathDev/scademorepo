import urllib3


def policy_version():
    return "1.0.0 (urllib3 " + urllib3.__version__ + ")"
