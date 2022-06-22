from setuptools import setup, find_packages
import dpv


setup(
    name=dpv.__name__,
    version=dpv.__version__,
    description=dpv.__doc__,
    url='https://github.com/wangelik/TraVaS/tree/main/implementation/TraVaS',
    author=dpv.__author__,
    author_email=dpv.__author_email__,
    license='not_licensed',
    packages=find_packages(),
    install_requires=['numpy', 'numba',
                    'matplotlib', 'seaborn',
                    'python_Levenshtein', 'pyemd',
                    'diffprivlib', 'ortools',
                    'pm4py'],
    classifiers=[
        'Development Status :: 3 - Prototype',
        'Intended Audience :: Science/Research',
        'License :: None',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)
