1) Do activate your virtual enviornment (name it venv, as added in gitignore, python -m venv venv)
2) after installing dependencies do update requirements.txt (pip freeze > requirements.txt)
---
1) we will push all code in dev branch.
2) we will make feature branches from dev and work accordingly
3) To get dev branch in your local follow these commands
4) git checkout -b dev (tho it could be anyname, but prefer whats being created in github )
5) git pull origin dev (this dev is of github i.e remote->local )
6) Now from dev branch make respective feature branches locally
7) To do so, first make sure u r in dev branch locally then:
8) git checkout -b meetings
9) so this is like main -> dev -> meetings
10) Best Practice: to do regular git pull!
11) Before merging, feature to dev, merge dev to feature, for consistency.

---

Run the App:

1) docker compose up --build
2) From terminal login to databse via:
   * docker ps (see the container id of postgres container say 1xc2)
   * docker exec -it 1xc2 bash
   * psql -U username -d databse name (see from env)
   * enter password
   * \l list all databses
   * \c databasename
   * \dt list all table in current db
   * \d tablename
   * normal sql commands
