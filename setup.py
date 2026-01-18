import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yt-search-python",
    version="2.0.0",
    author="Prakhar",
    license="MIT",
    author_email="srvopus@gmail.com",
    description="Search YouTube contents without YouTube Data API v3. Professionally maintained fork with modern Python support. Sync & async support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BillaSpace/yt-search-python",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "httpx>=0.28.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
