# burns - Bulk Upload of Remote Networks 
The scripts in this repository are used for bulk creation, modification, and deletion of Remote Networks, IPSec tunnels, and IKE gateways within a Palo Alto Networks SASE environment.

## Usage
Both scripts process a comma-separated values (CSV) file as a command line argument.  Templates for these CSV files can be found in the `templates` directory.

A valid OAuth2 access token is required for API client authorization.  This token should be set in an environment variable called `API_TOKEN`.

### tunnels.py
```
usage: tunnels.py [-h] [--delete] filename

Manage SASE IKE gateways and IPSec tunnels

positional arguments:
  filename    The CSV file containing IKE gateway and IPSec tunnel information

optional arguments:
  -h, --help  show this help message and exit
  --delete    Delete IKE gateways and IPSec tunnels
  ```

### networks.py
```
usage: networks.py [-h] [--delete] filename

Manage SASE remote networks

positional arguments:
  filename    The CSV file containing remote network information

optional arguments:
  -h, --help  show this help message and exit
  --delete    Delete SASE remote networks
  ```


