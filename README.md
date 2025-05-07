# 🧠 MCP Server for bunq API

This is an [MCP](https://github.com/latentspace/mcp) (Modular Command Platform) server that connects to the [bunq](https://www.bunq.com) banking API. It exposes a wide range of tools to interact with bunq, including payments, invoices, cards, and more.

You can use this with Claude Desktop or other MCP-compatible clients.

---
> ⚠️ **WARNING: Running in PRODUCTION**
>
> Be extremely cautious when setting `BUNQ_ENVIROMENT="PRODUCTION"` in your `.env` file.  
> This will connect the MCP server to your live bunq account.  
> Make sure you understand the implications, verify API permissions, and never expose your production API key publicly.
> We take no responsibility for any money lost



## 🚀 Quick Start

### 1. Clone the repository and install dependencies

```bash
git clone https://github.com/yourusername/bunq-MCP.git
cd bunq-MCP
pip install -r requirements.txt
```
2. Add a .env file
In the root of the project, create a .env file with the following content:

```
BUNQ_API_KEY="sandbox_c6428588c758d2b50dbfcbde59371ce88424cc6373249db97d25f7cf"
BUNQ_ENVIROMENT="SANDBOX"
```
For production, set BUNQ_ENVIROMENT to PRODUCTION.

3. Run the server
```
python3 server.py
```
🧠 Using with Claude Desktop
Add the server to your Claude Desktop config.json:

```
{
  "mcpServers": {
    "bunq": {
      "command": "python3",
      "args": [
        "/Users/pvandoorn/Desktop/bunq-MCP/server.py"
      ]
    }
  }
}
```


🔧 Tools Included
This server exposes the following tools via the MCP interface:

get_user_id

get_user_display_name

get_primary_monetary_account_id

get_list_monetary_accounts

list_user_invoices

get_subscription_contracts

send_payment

request_money

create_card

fetch_last_payments

schedule_payment

generate_bunq_me_link

These tools use the official bunq SDK and return structured Python objects.


📁 Project Structure
```
.
├── server.py       # MCP server for bunq
├── .env            # Your bunq API key and environment
├── README.md       # This file\
```

🧑‍💻 License
MIT — feel free to fork and modify.

