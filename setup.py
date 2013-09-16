from setuptools import setup
setup(
    name='abrt-devel-tools',
    version='1.0',
    author="Jiri Moskovcak",
    author_email="jmoskovc@redhat.com",
    description=("Cmdline tool to ease the abrt devel process"),
    license = "GPLv2+",
    url = "https://github.com/mozeq/abrt-devel-tools",
    scripts = ['src/submit-patch'],
    packages=['abrtdeveltools'],
    package_dir = {'abrtdeveltools': 'src/abrtdeveltools'},
)
