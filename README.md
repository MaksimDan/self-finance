# self-finance

self-finance is a local python web application for providing insights on your bank transactions.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_IIMtb0O5QE" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Installation

### Mac

1. Make sure that you have ` >= python 3.5` available on your machine and active. Otherwise

    ```shell
    brew install python3
    
    need to add the path
    verify 
    danielm-00XLHV2J:self-fin danielm$ python3 --version
    Python 3.7.3
    
    ```

2. Ensure you have virtual env available on your machine, otherwise `pip install virtualenv`.

3. Create and active your new virtual environment

    ```bash
    virtualenv self-finance
    source self-finance/bin/activate
    ```

4. Clone and install the application from to a temporary directory, and then remove the directory

   ```bash
   cd ~/Desktop
   mkdir tmp
   cd tmp
   git clone https://github.com/MaksimDan/self-finance.git
   pip install -r ./self-finance/requirements.txt
   pip install ./self-finance
   rm -rf ~/Desktop/tmp # dont do this? keep somewhere safe for updates (nd reinstall, add information for updating)
   
   // notes
   - need to not use anaconda python
   - change path to your normal python env
   
   python3 -m venv .
   source ./bin/activate
   pip install .
   ```

5. Go to plaid.com and request a developors license. Once your request is approved, export them as path variables onto your machine.

    ```bash
    touch ~/.bash_profile; open ~/.bash_profile
    
    # add:
    export PLAID_CLIENT_ID=your_plaid_client_id
    export PLAID_PUBLIC_KEY=you_plaid_public_key
    export PLAID_SECRET=your_plaid_secret
    
    source ~/.bash_profile
    ```

## Windows

## Usage

```bash
source self-finance/bin/activate
self-finance run
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)