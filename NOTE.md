# Dev Cheatsheet

## Encrypt Keys
```
tar cvf secrets.tar config_jsons/flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json gravitate-backend/gravitate/config_jsons/gravitate-backend-testing-firebase-adminsdk-nztgj-d063415ecc.json 
travis login --pro
travis encrypt-file secrets.tar --pro
```

## Update Submodule
```
git submodule update --remote
git add gravitate-backend
```
