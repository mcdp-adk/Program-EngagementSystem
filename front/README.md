# front

## 开发环境

```python
// app.py
if __name__ == "__main__":
    print("Opening python...")
    start_eel(True)
```

```shell
python app.py
npm run serve
```

## 打包

```python
// app.py
if __name__ == "__main__":
    print("Opening python...")
    start_eel(False)
```

```shell
npm run build
python -m eel app.py web --onefile --noconsole
```
