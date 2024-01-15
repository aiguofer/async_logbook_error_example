Install deps:

```
pip install -U -e .
```

Run server:

```
cd src
uvicorn app:app --workers 1 --host 0.0.0.0 --port 8001
```

Run multiple simultaneous requests:

```
python client.py
```
