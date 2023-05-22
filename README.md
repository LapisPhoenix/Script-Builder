![Banner](assets/banner.png)
## About
Quickly create scripts you can call from the command line with ease. **Currently only supports Windows.**

## Installation
1. Clone the repository
```bash
gh repo clone LapisPhoenix/Script-Builder
```

2. Install the requirements
```bash
pip install -r requirements.txt
```

## Usage
1. Fill out the `intents.json` file.
Example `intents.json`:
```json
{
    "storage": {
        "driver": "C",
        "scriptStorage": "C:\\PythonScripts"
    },
    
    "script": {
        "mainScript": "C:\\Users\\Lapis\\Desktop\\Example-Project\\main.py",
        "include": ["C:\\Users\\Lapis\\Desktop\\Example-Project\\utils\\util1.py", "C:\\Users\\Lapis\\Desktop\\Example-Project\\utils\\util2.py"]
    },
    
    "command": "python main.py"
}
```

2. Run the sb.py in administrator
```bash
python sb.py
```


## Dependencies
- [Colorama 0.4.6](https://pypi.org/project/colorama/)


## License
[MIT](https://choosealicense.com/licenses/mit/)

## Support Me
[Cash App](https://cash.app/$LapisPheonix)