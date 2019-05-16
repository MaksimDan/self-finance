# self-finance

self-finance is a local python web application for providing analytical insights on your bank transactions.

[![self-finance demo](http://i3.ytimg.com/vi/_IIMtb0O5QE/maxresdefault.jpg)](https://youtu.be/_IIMtb0O5QE "self-finance demo")

## Installation

### Mac

**Run Down**

```bash
touch ~/.bash_profile; open ~/.bash_profile
# add:
export PLAID_CLIENT_ID=your_plaid_client_id
export PLAID_PUBLIC_KEY=you_plaid_public_key
export PLAID_SECRET=your_plaid_secret
source ~/.bash_profile

git clone https://github.com/MaksimDan/self-finance.git
cd self-finance/
python3 -m venv .
source bin/activate
pip install -r requirements.txt 
pip install .
self-finance
```

**Detailed**

1. Go to plaid.com and request a developors license. Once your request is approved, export them as path variables onto your machine.

      ```bash
   touch ~/.bash_profile; open ~/.bash_profile
   
   # add:
   export PLAID_CLIENT_ID=your_plaid_client_id
   export PLAID_PUBLIC_KEY=you_plaid_public_key
   export PLAID_SECRET=your_plaid_secret
   
   source ~/.bash_profile
   ```

2. Make sure that you have ` >= python 3.5` available on your machine and active and make sure it is NOT an anaconda based distribution. Otherwise

   ```bash
   brew install python3
   ```

3. Verify your python version

   ```bash
   python3 --version
   Python 3.x.x
   ```

4. If this does not show modify your path, and in a NEW terminal session check again.

   ```bash
   vim ~/.bash_profile
   # add the following
   PATH="/Library/Frameworks/Python.framework/Versions/3.<your version>/bin:${PATH}"
   export PATH=/usr/local/bin:/usr/local/sbin:$PATH
   ```

5. Clone the repository anywhere you want

   ```bash
   git clone https://github.com/MaksimDan/self-finance.git
   ```

6. Activate a virtual enviroment

   ```bash
   cd self-finance/
   python3 -m venv .
   source bin/activate
   ```

7. Install the package requirements and the web app itself

   ```bash
   pip install -r requirements.txt 
   pip install .
   ```

8. Run the application

   ```
   self-finance
   ```


## Usage

```bash
cd to/this/repo
source bin/activate
self-finance
```

## Updating

```bash
cd to/this/repo
git pull origin master
source bin/activate
pip install -r requirements.txt
pip install .
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)