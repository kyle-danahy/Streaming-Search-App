To set up your environment for testing:
- Run `pip install -r requirements.txt`

To check that the database is working you have 2 options:
1. Run the unit tests, `pytest -s -m slow` from the root of this folder, you can see both the REST endpoint and the database exercised. (Most of this code is defined in data_collector.py) - if this doesn't work, then please try option 2
2. You can go to https://streaming-search-app-373a9f8fa5f5.herokuapp.com/ and type in a movie or tv show title. When you hit submit, the app will make a REST call to the Watchmode API and write the data to the database. Then the app will query the database to grab the data and format it into a (not very) pretty table which you will see on the next page.

- Continuous Deployment is set up through Heroku, when a new commit is made to main in github Heroku will pick that up and re-deploy that.
- Database is Postgres running as a docker container
- To view Prometheus/Grafana on Heroku, click the "View Metrics on Grafana" button on the link above.