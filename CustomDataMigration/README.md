## Install & Dependence
- python3
- pip3
- in your terminal run:
  ```cmd
  pip3 install progressbar
  ```
## Use
```cmd
python3 custom_data_migration.py -url SELENE_ENDPOINT -f PATH_TO_XXX-test-data.json
```
Example: 
```
python3 custom_data_migration.py -url https://selene-health-dev.a-ue1.dotdash.com -f '/Users/jay/Desktop/health-test-data.json'
```

## Directory Hierarchy
```
|—— CustomDataMigration
|    |—— OUTPUT_FOLDER
|        |—— log
|            |—— log.json
|        |—— new-XXX-test-data.json
|        |—— testData
|            |—— XXXX-doc.json
|    |—— custom_data_migration.py
|    |—— README.md
```

## License
@Dotdash Meredith