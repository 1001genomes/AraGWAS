# AraGWAS
GWAS catalogue for Arabidopsis thaliana

This is a Single Page App (SPA) that consists of a [django backend](aragwas_server) and a [VueJS frontend](aragwas_ui)
The Django backend acts as a REST endpoint for the VueJS frontend. 


## Requirements

Aragwas_server requires Python 3.x and the aragwas_ui requires nodejs (> 6.x) and npm to be installed 

## Installation

1. Install aragwas_server with `cd aragwas_server && pip install -r requirements.txt` 
2. Install aragwas_ui with `cd aragwas_ui && npm install`

## Development

1. Start the aragwas_server with `cd aragwas_server && ./manage runreserver` (will run on localhost:8000)
2. Start the aragwas_ui with `cd aragwas_ui && npm run dev` (will run on localhost:3000)

Once you start aragwas_ui a new browser window should open the frontend part. 
The frontend node server will also make sure to proxy all calls to `/api/` to the django backend.



## Production

1. Build aragwas_ui with `cd aragwas_ui && npm run build` 
2. Start the aragwas_server with `cd aragwas_server && ./manage runserver`

Open the browser on http://localhost:8000 




