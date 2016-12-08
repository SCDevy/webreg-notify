# webreg-notify
Get notified about open registration spots for classes at USC.

## Usage

1. Install dependencies (recommended to use venv):

```
pip install -r requirements.txt
```

1. Configure query in JSON:

```
// data.json
{
	{
		"username": "1234567890", // USC ID #
		"password": "passcode", // 8 character USC passcode
		"query": {
			"term": "20171", // 5 digit code
			"department": "WRIT", // 4 character code
			"course": "340", // 3 digit code
			"section": ["65035 R", "65105 R", "65110 R"] // list of section IDs
		}
	}
}
```

1. Run script:

```
python app.py data.json