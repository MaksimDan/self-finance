# self-finance

self-finance is a local python web application for providing insights on your bank transactions.

TODO - gif of the interface

## Installation

1. Make sure that you have ` >= python 3.5` available on your machine and active.
2. Ensure you have virtual env available on your machine, otherwise `pip install virtualenv`.
3. Create and active your new virtual environment

```bash
virtualenv self-finance
source self-finance/bin/activate
```

4. Clone and install the application from to a temporary directory

   ```
   cd ~/Desktop
   mkdir tmp
   cd tmp
   git clone https://github.com/MaksimDan/self-finance.git
   ```

5. Go to plaid.com and request a developors license. Once you do, export them as path variables onto your machine.

**Mac** 

```
touch ~/.bash_profile; open ~/.bash_profile

add:
export PLAID_CLIENT_ID=your_plaid_client_id
export PLAID_PUBLIC_KEY=you_plaid_public_key
export PLAID_SECRET=your_plaid_secret

source ~/.bash_profile
```

**Windows**



## Usage

```python

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)