# GWAS Catalog curator user management

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
