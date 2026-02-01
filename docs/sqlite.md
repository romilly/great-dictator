When an application is using a SQLite database, you should do the following:
Create two databases,one for testing, one for production. Each database file should have a .db extension, and .gitignore should ingore all .db files.

The location of the databases should be specifies in .env files, so you'll need to add python-dotenv to requirements.txt and install it.

One .env file should be in the root of the project. That should specify the locationof the production database. The other .env file should be in the tests direcotry.
That way, test code will find the test database and sofware run from *anywhere* else in the project will find the version on the project root. 

Create a test fixture for database tests.
It should create the test database if it does not exist, and then use SQL `DELETE` to empty each table before each database test is run.
Take foreign keys into account when chosing the order of deletion.

The fixture should *NOT* empty the tables after a test; that way I can see what's in the database if a test behaves unexpectedly.
It *should* close the database after each test in a `finally` clause.

There should be one smoke test that connects to the production database, does nothing to it and then disconects.


