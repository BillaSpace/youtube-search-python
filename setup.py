import setuptools
from pathlib import Path

long_description=Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="yt-search-python",
    version="2.1.1",
    author="Prakhar-Shukla",
    license="MIT",
    author_email="srvopus@gmail.com",
    description="Search YouTube contents without YouTube Data v3 API_KEY with Modern Sync & Async Python support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BillaSpace/yt-search-python",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "httpx>=0.28.1"
    ],
    extras_require={
        "transcript":[
            'yt-dlp; python_version >= "3.10"'
        ]
    },
    python_requires=">=3.7"
)
