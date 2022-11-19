TOT_HOSTS = 9
HOSTS = ['client', 'stamper', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']

HOST_IP = {
	'client': '10.0.0.1',
	'stamper': '10.0.0.9',
	'h1': '10.0.0.2',
	'h2': '10.0.0.3',
	'h3': '10.0.0.4',
	'h4': '10.0.0.5',
	'h5': '10.0.0.6',
	'h6': '10.0.0.7',
	'h7': '10.0.0.8',
}

HOST_MAC = {
	'client': '00:00:00:00:00:01',
	'stamper': '00:00:00:00:00:09',
	'h1': '00:00:00:00:00:02',
	'h2': '00:00:00:00:00:03',
	'h3': '00:00:00:00:00:04',
	'h4': '00:00:00:00:00:05',
	'h5': '00:00:00:00:00:06',
	'h6': '00:00:00:00:00:07',
	'h7': '00:00:00:00:00:08',
}

MAC_TO_HOST = { mac: name for name, mac in HOST_MAC.items()}

SWITCH_HOST_TO_PORT = {
	'switch-1': {
		'stamper': 1,
		'client': 2,
		'switch-2': 3,
		'h1': 3,
		'h2': 3,
		'h3': 3,
		'h4': 3,
		'h5': 3,
		'h6': 3,
		'h7': 3,
	},
	'switch-2': {
		'h1': 1,
		'h2': 2,
		'h3': 3,
		'h4': 4,
		'h5': 5,
		'h6': 6,
		'h7': 7,
		'stamper': 8,
		'switch-1': 9,
		'client': 9
	}
}


PRIMARIES = ['h1', 'h2', 'h3', 'h5', 'h7']


# secondary is chosen on node-basis....need to change later
# TODO : multiple primary in one node

PRIMARY_TO_SECONDARY = {
	'h1': 'h2',
	'h2': 'h3',
	'h3': 'h4',
	'h5': 'h6',
	'h7': 'h1'
}
