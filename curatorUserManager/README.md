# GWAS Catalog curator user management

NOTE: This is not maintained. The original documentation for this process should be followed to add any new user to the database. See https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/User+administration+in+the+curation+system for more details.


A small wrapper to add or inactivate curator in a specified database. Use with Python 3.


### Usage:


```bash
python ${scriptDir}/curatorGenerator.py --dbInstanceName  ${instance} --action ${action}
```

Where:

* Instance: database instance
* action: what we want to do: create, inactiveate or modify

### Behavior:

When the script is called and the the connection to the db was successful, in an interactive session the script asks for the required fields:

**Action: create**

```
Specify first name: <firstName>
Specify last name: <lastName>
Specify email address: <email@address>
Specify role (admin/curator): curator
Specify password hash: $2a$04$jGq0UGt6e47xS33CKI9sY.v7XZhrX8Cy8rJ2EIu4jeatMgo/auWmC
```

The hash is generated on a website providing BCrypt hashing eg. [this](https://www.dailycred.com/article/bcrypt-calculator) (with 4 rounds). This has will be compared to the hash generated upon login. 

**Action: inactivate**

```
Specify e-mail of the user to be inactivated: <email1>
Specify e-mail of a admin user: <email2>
```

To ensure consistency and tracking, curator accounts are not deleted but inactivated. Upon inactivating the account the password hash is updated with an other user's hash, so the inactivated user's email address can be used to log in with the other user's password. 

**Action: modify**

As a first step, the user is identified by his email address:

```
Specify the email address of the user to be updated:
```

The personal details attached to this user is going to be changed as follows: 

```
[Info] Modification user information of the GWAS Catalog
[Info] Those fields you want to keep the same, leave empty!
Specify email address:
Specify first name:
Specify last name:
Specify password hash: $2a$04$rZ/PUN81G8LJFn0azu1T4ex8gTeo8zaUJRK.Zupvf2EDIJtRvn8l6
```

* To update only the password, just past the hash and leave all the other fields empty.
* If the user want to change email address, the script checks if the given email is in already in use or not.

### More information

See documentation on [confluence](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/Curator+user+manager).
