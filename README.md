# neo4index
Flask &amp; Neo4j citation index calculation app

![Alt Text](https://media.giphy.com/media/1iok6OhhxIJsrlq2YK/giphy.gif)

## Abstract
Citations are very important for the world of science. Scientific achievements of researchers are often estimated based on research carried out on bibliographic lists. Scientists who are cited more often are considered the most valuable. The evolution of the Internet requires the development of information storage methods, because data is constantly increasing in quantity. Non-relational databases have been gaining popularity over the last years, because traditional database solutions, despite being a standard, do not necessarily cope well with storing and processing huge amounts of connected data. The graph model of data representation becomes noteworthy in such cases. This work combines both issues -- the evaluation of scientific achievements using bibliometric indicators and the use of graph databases to store and process connected data.


## Installation
I recommend using virtualenv. 

```
virtualenv venv --python=python3.6
source venv/bin/activate
pip install -r requirements.txt
```
## How to run
Remember to have your Neo4j database running. Datasets can be found below.
```
FLASK_APP=run.py FLASK_DEBUG=1 flask run
```

## See also
* [oai-harvest](https://github.com/jacekmiecznikowski/oai-harvest) - A harvester used to collect records from arXiv via OAI2.
* [figshare](https://figshare.com/s/3378e00e2362f5ac5e4d) - Datasets used in this project
* [arXivCSV](https://github.com/jacekmiecznikowski/arXivCSV) - This script manipulates arXiv OAI-PMH files to CSV format
* [arxivCite](https://github.com/jacekmiecznikowski/arxivCite) - Citation simulator for dataset used in this application


## Author
Copyright &copy; 2018 [Jacek Miecznikowski](https://github.com/jacekmiecznikowski). All rights reserved.
