# 🧠 Dune Query Service

This project provides a modular and extensible Python client to fetch and export data from [Dune Analytics](https://dune.com) using its official API.

---

## 📦 Features

- Query Dune Analytics using official SDK
- Strongly-typed parameter classes (Text, Number, Date, Enum)
- Clean OOP architecture with pluggable configs
- CSV export functionality
- Extensible via JSON or Python config

---

## 🛠️ Setup

1. **Install dependencies**

```bash
pip install dune-client pandas python-dotenv
```

2. **Set environment variables**

- Copy .env.example to .env and provide your Dune API key:

```bash
cp .env.example .env
```

3. **Run a query**

```bash
python dune_query_service.py
```

✨ **Example Config Usage**
```python
DuneQueryParams(
    query_id=123,
    query_name="pool_fees",
    additional_params=[
        DuneParamFactory.from_param_type(
            name="pool_address",
            value="0xabc...",
            param_type="text"
        )
    ]
)
```

