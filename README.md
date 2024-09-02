**Risk Visualization for Failure Prediction**

This application monitors the level of risk of failure of a network based on the settings and usage of its components. Currently is not integrated to live streaming data and it emulates this behavior via a Flask Server. The app is based mainly on Streamlit framework.

To run the application it is necessary to run the streamlit app on a docker container and the flask serve locally, simultaneously.
To run the server.py file:
  * Create python 3.12 virtual environment
  * Install dependecies listed on requirements.txt
  * Run the _python server.py_ command

To run the front.py file:
  * Build the container with _docker-compose up --build_

