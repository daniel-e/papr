# Papr

Papr is a command line tool to manage and quickyl access scientific papers.

![papr](screenshot.png)

## Install

You can install papr via pip as follows:

    pip install papr
   
## Getting started.

Papers are organized in repositories. To create a repository change into a directory where the repository should be created and type `papr init`. Example:

    cd astro_repo
    papr init
    
This will create a directory `.paper` in the `astro_repo` directory to store metadata. All PDFs will be stored in `astro_repo`.

**Default repositories**

The last repository which you create with `papr init` is set as the default repository. If you call `papr` without being in a repository the default repository will be used for all operations. Otherwise, the current working directory will be used as the repository.

**Fetch a paper from arXiv.org**

Fetch a document from arXiv is quite easy. You just have to provide the URL of the abstract and papr will download the PDF and will automatically extract the title. Example:

    papr fetch https://arxiv.org/abs/1812.07561