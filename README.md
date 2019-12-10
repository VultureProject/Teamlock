TeamLock
===================================

TeamLock is a passwords manager for Enterprises. 

### Security

To manage the security of passwords, this app uses two different encryption mecanism:
- Asymetric encryption with RSA
- Symetric encryption

When a user is created, a mail is sent to allow him to configurate his account. He will have to choose a password for login and for asymetric key generation.

Once all the password are saved, the app will encrypt the database with a symetric key.
Then, the symetric key is encrypted using the user public key.

## Libraries

- django
- pycrypto

## Installation

	$ apt update
	$ apt install libpq-dev
    $ Install postgresql
    $ Create a database
    $ Alter Postgresql,Redis & Public URI informations in the settings.py 

    $ pip3 install -r requirement.txt
    $ python3 manage.py migrate
    $ python3 manage.py runserver
    $ go to http://ip:8000/install

## Licence

Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Teamlock. If not, see <http://www.gnu.org/licenses/>.

## More Information

- Author: Olivier de Régis
- License: GPL 3.0
