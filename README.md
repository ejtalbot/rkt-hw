## Running the containerized app

In a terminal run `docker-compose build` to create the app.
Once the app is built, run `docker-compose up -d` to spin up the container

The server will be running locally in the background on port 5000.
curl the endpoint (example below)
`curl -X POST http://0.0.0.0:5000/api/predict --data '{"0":{"borough":"Bronx","tstamp":"2021-05-05","cuisine":"Asian"},"1":{"borough":"Brooklyn","tstamp":"2021-03-10","cuisine":"Mexican"}}' -H "Content-Type: application/json"`
to get back a response:
`{
  "0": 0.76,
  "1": 0.69
}`

When finished, use `docker-compose down` to stop the server.

### Running tests
To run a few unit tests, use the following commands to build and run:
`docker-compose -f docker-compose-test.yml build`
`docker-compose -f docker-compose-test.yml up`