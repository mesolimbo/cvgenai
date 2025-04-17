from setuptools import setup, find_packages

setup(
    name="cvgenai",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jinja2",
        "weasyprint",
        "tomli",
    ],
    entry_points={
        'console_scripts': [
            'generate-cv=resume.generate:main',
        ],
    },
    python_requires=">=3.7",
)
