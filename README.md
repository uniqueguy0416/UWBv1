# IoT-final: Pallet Tracking System

This is a final project of Introdution to IoT. In this project we create a pallet tracking system, a system that utilize UWB to get precise location and a indoor navigation UI to help driver find the pallet easier.

`Demo Video:` https://youtu.be/ZkyWsJ1yiJE

`Final Report`: https://www.canva.com/design/DAGZp43ktfU/YAgh4HthvgjClhMK_XPSzA/view?utm_content=DAGZp43ktfU&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h0ea9ce1e7d

`frontend`:

To show the map, you need to first copy `.env.default` to `.env` under the folder "./frontend" (same as `.env.default`). Then, you need to get the api token from mapbox and fill it in `.env` file. After that, run the following command to start the frontend.

```
cd ./frontend
npm install
yarn start
```

`cloud`: backend database

To use mongoDB as our backend, you need to first copy `.env.default` to `.env` under the folder "./cloud" (same as `.env.default`). Then, you need to get the mongo url from mongoDB and fill it in `.env` file. After that, run the following command to start the backend database.

```
cd ./cloud
npm install
node src/server.js
```

`countPath`: backend server(get position and route)

// ToDo things about UWB

```
cd ./countPath
pip install -r requirements.txt
python3 server.py
```
