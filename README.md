# FlowQ
### ***Your Friendly Neighbourhood Distributed Computing System***

FlowQ was created for the goal of making distributed computing free, simple and easier.

### _Features of FlowQ:_
- **Effortless Setup**: Ditch the complicated configurations! FlowQ runs right out of the box, no ssh headaches or pre-installation required.
- **Simple and Secure Connection**: Leverages the Hack.Chat platform to establish secure, base-64 encrypted and anonymous connections with your computing cluster.
- Temporary Storage: Need a place to store input and output files? FlowQ utilizes FileBin for convenient temporary storage.
- Parallel Powerhouse: FlowQ unleashes the true potential of your network by executing tasks in parallel across your machines, significantly boosting your processing speed.

### _I don't have any other computing devices, and I don't want to spend money...._
- **Supercharge your cluster in seconds!** FlowQ lets you seamlessly add new machines with Python. Just 2 lines of command, and you've got a processing powerhouse. FlowQ makes scaling effortless.
```bash
!pip install FlowQ
!python -m FlowQ.cluster -c <your-channel-name>
```
- You can run these commands in your **Google Colab Instances** or any other computer, for scaling your cluster with ease.

### _Client Usage_
- You can set up your client, with simple **FlowQlient** Class!
```python
from FlowQ.client import FlowQlient
flow = FlowQlient(channel="<your-channel-name>")
flow.connect(name="<your-user-name>")

@flow.task
def alpha(x):
    ## Import all the needed modules inside the function
    import requests
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    return requests.get(url).json()["text"], x

output = flow.get([alpha(i) for i in range(6)])

```
#### ⚡Note⚡: Please initialize the cluster before running the Client code(This will be fixed in future updates)