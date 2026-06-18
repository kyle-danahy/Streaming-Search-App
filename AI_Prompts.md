I used the following AI prompts to assist me while developing:

1. I won't post the full stack from Heroku since it is quite large, but I was having issues getting a database connection there so I asked the AI to describe how to fix that issue. It suggested installing the postgres addon through the Heroku CLI which fixed the issue (along with some checks in the code, those are not necessary once the addon is installed)
2. "how do I automatically start the database before running unit tests?"
3. I had an "pika.exceptions.AMQPConnectionError" when running the app on Heroku, asked the AI to help diagnose this issue.
4. Asked the AI to help write and/or clean up comments on multiple methods throughout the app.
5. Asked the following to help implement and debug the configuration to view application metrics in grafana:
    - How do I see data from this app on a grafana dashboard?
    - How do I add metrics via Prometheus?
    - How would I create a docker container setup to run Prometheus as a heroku app?