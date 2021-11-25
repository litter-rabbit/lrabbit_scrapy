import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lrabbit_scrapy",
    version="2.0.3",
    author="lrabbit",
    author_email="709343607@qq.com",
    description="this is a small spider,you can easy running. When you often need to crawl a single site, you don't have to redo some repeated code every time, using this small framework you can quickly crawl data into a file or database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/litter-rabbit/lrabbit_scrapy",
    project_urls={
        "Bug Tracker": "https://github.com/litter-rabbit/lrabbit_scrapy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "parsel == 1.6.0",
        "requests >= 2.26.0",
        "PyMySQL >= 0.9.3",
        "redispy >= 3.0.0"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
