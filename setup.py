from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sandboxzilla",
    version="0.1.7",
    description="Collection of tools for writing communication test scripts",
    url="https://github.com/sandboxzilla/comm_helper.git",
    author="Erol Yesin",
    author_email="erol@sandboxzilla.net",
    license="MIT",
    py_modules=["comm.base_dev_helper",
                "comm.ip_helper",
                "comm.udp_listener",
                "utils.event_handler",
                "utils.timer_event",
                "utils.repeating_event",
                "utils.logger",
                "utils.queue",],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
