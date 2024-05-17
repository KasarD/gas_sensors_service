# gas_sensors_service

## Combinations

[POST] `/combinations/calc`

```
BODY: multipart-form, one field: name - data, value - attached csv file
RESPONSE: json with job_uuid
RESPONSE EXAMPLE:
{
	"job_uuid": "272ef00cde914bffb0e0c8a4a9813ddd"
}
```

[GET] `/combinations/result?jobUUID=<job_uuid>`

```
RESPONSE: json with a list of dict (a big one)
NOTE: we can use it to gather raw results from backend, but it is not neccessary
```

[GET] `/combinations/max-min-spread?jobUUID=<job_uuid>`

```
RESPONSE: json with a based64-decoded image
NOTE: some useful image for scientists
```

[GET] `/combinations/best-worst?jobUUID=<job_uuid>`

```
RESPONSE: json with final information: the best and the worst combinations of sensors
RESPONSE EXAMPLE:
{
	"best": {
		"mean median": 0.262,
		"sensors": [
			1,
			2,
			4,
			5,
			6,
			8,
			9,
			10,
			15,
			17
		]
	},
	"worst": {
		"mean median": 0.012,
		"sensors": [
			11,
			19
		]
	}
}
```
